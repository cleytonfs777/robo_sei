import os
import json
import re
import time
import requests
from dotenv import load_dotenv

# =========================
# Config
# =========================
load_dotenv()

API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")
BOARD_NAME = os.getenv("BOARD_NAME", "Desenvolvimento de Sistemas")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
TIMEOUT = 60

SLEEP_BETWEEN_CALLS = 0.10  # ajuda com rate limit


# =========================
# Helpers
# =========================
def trello_get(url, params=None):
    params = params or {}
    params.update({"key": API_KEY, "token": TOKEN})
    r = requests.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    time.sleep(SLEEP_BETWEEN_CALLS)
    return r.json()


def safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)  # windows-safe
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180] if len(name) > 180 else name


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def get_board_id_by_name(board_name: str) -> str:
    boards = trello_get(
        "https://api.trello.com/1/members/me/boards",
        {"fields": "name"},
    )
    for b in boards:
        if b.get("name") == board_name:
            return b["id"]
    raise SystemExit(f'Board "{board_name}" não encontrado.')


def download_file(url: str, dest_path: str):
    # Tenta baixar via URL do Trello com key/token e redirects
    with requests.get(
        url,
        params={"key": API_KEY, "token": TOKEN},
        stream=True,
        timeout=TIMEOUT,
        allow_redirects=True,
    ) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)


def get_card_comments(card_id: str):
    # Comentários são actions do tipo commentCard
    comments = trello_get(
        f"https://api.trello.com/1/cards/{card_id}/actions",
        {
            "filter": "commentCard",
            "limit": 1000,
            "fields": "id,type,date,data,memberCreator",
            "memberCreator_fields": "fullName,username",
        },
    )
    return comments


# =========================
# Main
# =========================
def main():
    if not API_KEY or not TOKEN:
        raise SystemExit("API_KEY e TOKEN precisam estar definidos no .env")

    board_id = get_board_id_by_name(BOARD_NAME)

    base_path = os.path.join(BACKUP_DIR, safe_filename(BOARD_NAME))
    ensure_dir(base_path)

    comments_dir = os.path.join(base_path, "comments")
    attachments_dir = os.path.join(base_path, "attachments")
    ensure_dir(comments_dir)
    ensure_dir(attachments_dir)

    # Pega cards com título, desc e metadata de anexos
    cards = trello_get(
        f"https://api.trello.com/1/boards/{board_id}/cards",
        {
            "fields": "name,desc,url,closed,dateLastActivity",
            "attachments": "true",
            "attachment_fields": "name,url,bytes,date,mimeType,isUpload",
        },
    )

    # Monta um JSON mínimo com o que você quer
    cards_min = []
    total_comments = 0
    total_attachments_downloaded = 0

    for card in cards:
        card_id = card["id"]
        title = card.get("name", "")
        desc = card.get("desc", "")
        url = card.get("url", "")

        # 1) Comentários
        try:
            comments = get_card_comments(card_id)
        except Exception as e:
            comments = []
            print(f'[ERRO] Comentários de "{title}": {e}')

        total_comments += len(comments)

        with open(os.path.join(comments_dir, f"{card_id}.json"), "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)

        # 2) Anexos
        atts = card.get("attachments", []) or []
        card_att_dir = os.path.join(attachments_dir, card_id)
        if atts:
            ensure_dir(card_att_dir)

        attachments_meta = []
        for att in atts:
            att_name = att.get("name") or "attachment"
            att_url = att.get("url")
            is_upload = att.get("isUpload", False)

            attachments_meta.append(
                {
                    "name": att_name,
                    "url": att_url,
                    "isUpload": is_upload,
                    "mimeType": att.get("mimeType"),
                    "bytes": att.get("bytes"),
                    "date": att.get("date"),
                }
            )

            # Só baixa arquivo quando for upload do próprio Trello
            if is_upload and att_url:
                filename = safe_filename(att_name)
                dest_path = os.path.join(card_att_dir, filename)

                # evita sobrescrever duplicados
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(dest_path)
                    k = 2
                    while os.path.exists(f"{base} ({k}){ext}"):
                        k += 1
                    dest_path = f"{base} ({k}){ext}"

                try:
                    download_file(att_url, dest_path)
                    total_attachments_downloaded += 1
                    print(f'[DL] "{title}" -> {os.path.relpath(dest_path, base_path)}')
                except Exception as e:
                    print(f'[ERRO] Baixar anexo "{att_name}" do card "{title}": {e}')

        cards_min.append(
            {
                "id": card_id,
                "title": title,
                "description": desc,
                "url": url,
                "comments_file": f"comments/{card_id}.json",
                "attachments": attachments_meta,
            }
        )

        print(f'[OK] "{title}" | comments={len(comments)} | attachments={len(atts)}')

    # salva o index mínimo
    with open(os.path.join(base_path, "cards_min.json"), "w", encoding="utf-8") as f:
        json.dump(cards_min, f, ensure_ascii=False, indent=2)

    print("\n=== RESUMO ===")
    print("Cards:", len(cards_min))
    print("Comentários:", total_comments)
    print("Anexos baixados (uploads):", total_attachments_downloaded)
    print("Pasta:", base_path)


if __name__ == "__main__":
    main()
