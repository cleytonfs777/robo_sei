import os
import json
import time
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# =========================
# ENV
# =========================
API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")

TARGET_BOARD_NAME = os.getenv("TARGET_BOARD_NAME", os.getenv("BOARD_NAME", "Desenvolvimento de Sistemas"))
TARGET_LIST_NAME = os.getenv("TARGET_LIST_NAME", "To Do")  # lista onde os cards serão criados

BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
BACKUP_BOARD_FOLDER = os.getenv("BACKUP_BOARD_FOLDER", "Desenvolvimento de Sistemas")  # nome da pasta do backup (igual ao board na hora do backup)

TIMEOUT = 60
SLEEP_BETWEEN_CALLS = float(os.getenv("SLEEP_BETWEEN_CALLS", "0.10"))


# =========================
# Helpers
# =========================
def safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180] if len(name) > 180 else name


def trello_request(method: str, url: str, *, params=None, files=None, data=None, json_body=None, retries=6):
    """
    Wrapper com retry para 429 (rate limit) + erros transitórios.
    """
    params = params or {}
    params.update({"key": API_KEY, "token": TOKEN})

    for attempt in range(1, retries + 1):
        try:
            r = requests.request(
                method,
                url,
                params=params,
                files=files,
                data=data,
                json=json_body,
                timeout=TIMEOUT,
                allow_redirects=True,
            )

            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", "5"))
                time.sleep(wait)
                continue

            r.raise_for_status()

            time.sleep(SLEEP_BETWEEN_CALLS)
            # algumas respostas podem ser vazias
            return r.json() if r.text and r.headers.get("content-type", "").startswith("application/json") else r.text

        except requests.RequestException as e:
            if attempt == retries:
                raise
            time.sleep(min(2 ** attempt, 20))

    raise RuntimeError("Falha inesperada no trello_request.")


def trello_get(url, params=None):
    return trello_request("GET", url, params=params)


def trello_post(url, params=None, files=None, data=None):
    return trello_request("POST", url, params=params, files=files, data=data)


def get_board_id_by_name(board_name: str) -> str:
    boards = trello_get(
        "https://api.trello.com/1/members/me/boards",
        {"fields": "name"},
    )
    for b in boards:
        if b.get("name") == board_name:
            return b["id"]
    raise SystemExit(f'Board alvo "{board_name}" não encontrado.')


def get_lists_map(board_id: str) -> dict:
    lists_ = trello_get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        {"fields": "name"},
    )
    return {lst["name"]: lst["id"] for lst in lists_}


def create_card(list_id: str, title: str, description: str) -> dict:
    return trello_post(
        "https://api.trello.com/1/cards",
        {
            "idList": list_id,
            "name": title,
            "desc": description,
        },
    )


def add_comment_to_card(card_id: str, text: str):
    trello_post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        {"text": text},
    )


def attach_url(card_id: str, url: str, name: str | None = None):
    params = {"url": url}
    if name:
        params["name"] = name
    trello_post(f"https://api.trello.com/1/cards/{card_id}/attachments", params)


def attach_file(card_id: str, file_path: str):
    with open(file_path, "rb") as f:
        trello_post(
            f"https://api.trello.com/1/cards/{card_id}/attachments",
            params={},
            files={"file": f},
        )


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# Main
# =========================
def main():
    if not API_KEY or not TOKEN:
        raise SystemExit("API_KEY e TOKEN precisam estar definidos no .env")

    backup_base = os.path.join(BACKUP_DIR, safe_filename(BACKUP_BOARD_FOLDER))
    cards_min_path = os.path.join(backup_base, "cards_min.json")
    comments_dir = os.path.join(backup_base, "comments")
    attachments_dir = os.path.join(backup_base, "attachments")

    if not os.path.exists(cards_min_path):
        raise SystemExit(f"Não encontrei: {cards_min_path}")

    cards_min = load_json(cards_min_path)

    # board/list destino
    target_board_id = get_board_id_by_name(TARGET_BOARD_NAME)
    lists_map = get_lists_map(target_board_id)

    if TARGET_LIST_NAME not in lists_map:
        raise SystemExit(
            f'Lista "{TARGET_LIST_NAME}" não existe no board "{TARGET_BOARD_NAME}". '
            f"Listas disponíveis: {list(lists_map.keys())}"
        )

    target_list_id = lists_map[TARGET_LIST_NAME]

    print(f"[INFO] Restore para board='{TARGET_BOARD_NAME}' lista='{TARGET_LIST_NAME}'")
    print(f"[INFO] Backup base: {backup_base}")
    print(f"[INFO] Cards no backup: {len(cards_min)}\n")

    restored = 0
    for item in cards_min:
        old_id = item["id"]
        title = item.get("title", "")
        desc = item.get("description", "")

        # 1) cria card
        new_card = create_card(target_list_id, title, desc)
        new_id = new_card["id"]

        # 2) comentários (em ordem cronológica)
        comments_file = os.path.join(comments_dir, f"{old_id}.json")
        if os.path.exists(comments_file):
            comments = load_json(comments_file)
            # ordena do mais antigo pro mais novo
            comments.sort(key=lambda x: x.get("date", ""))
            for c in comments:
                text = (c.get("data", {}) or {}).get("text", "")
                if text:
                    add_comment_to_card(new_id, text)

        # 3) anexos
        # 3.1) reupload dos arquivos baixados (uploads)
        old_card_att_dir = os.path.join(attachments_dir, old_id)
        if os.path.isdir(old_card_att_dir):
            for fname in sorted(os.listdir(old_card_att_dir)):
                fpath = os.path.join(old_card_att_dir, fname)
                if os.path.isfile(fpath):
                    try:
                        attach_file(new_id, fpath)
                    except Exception as e:
                        print(f'[ERRO] Upload anexo "{fname}" no card "{title}": {e}')

        # 3.2) reanexa URLs externas (Drive etc.) quando existirem no cards_min.json
        for att in item.get("attachments", []) or []:
            att_url = att.get("url")
            att_name = att.get("name")
            is_upload = att.get("isUpload", False)

            # Se era upload do Trello, já tentamos reupload pelo arquivo local.
            # Se era link externo, reanexa via URL:
            if att_url and (is_upload is False):
                try:
                    attach_url(new_id, att_url, att_name)
                except Exception as e:
                    print(f'[ERRO] Reanexar URL "{att_name}" no card "{title}": {e}')

        restored += 1
        print(f'[OK] {restored}/{len(cards_min)} "{title}" (old={old_id} -> new={new_id})')

    print("\n[FIM] Restore mínimo concluído.")


if __name__ == "__main__":
    main()
