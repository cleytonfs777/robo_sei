# ===========================================
# 1) importar_cards.py
# - Lê cards.csv e cria cartões no Trello
# - Aplica labels com cores (mapeadas)
# - Define DueDate com normalize_due_date (evita cair 21:00 do dia anterior)
# - (Opcional) cria comentários a partir da coluna Comments (se existir)
#
# CSV esperado (UTF-8):
# Title,Description,List,Labels,DueDate[,Comments]
#
# .env:
# API_KEY=...
# TOKEN=...
# BOARD_NAME=Desenvolvimento de Sistemas   (opcional)
# ===========================================

import csv
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
TOKEN = os.getenv("TOKEN")
BOARD_NAME = os.getenv("BOARD_NAME", "Desenvolvimento de Sistemas")
CSV_PATH = os.getenv("CSV_PATH", "cards.csv")

DEFAULT_LABEL_COLOR = "blue"

# OBS: você colocou "certificado" duas vezes; mantive a ÚLTIMA ("black") como vencedora.
LABEL_COLORS = {
    "licenca": "green",
    "14133": "yellow",
    "prodemge": "orange",
    "pdcase": "red",
    "aas": "purple",
    "nts": "blue",
    "prateleira": "sky",
    "8666": "lime",
    "certificado": "black",
}


def normalize_due_date(date_str: str) -> str:
    # Recebe YYYY-MM-DD e devolve ISO seguro (UTC meio-dia -> não “vira” dia no BRT)
    return f"{date_str}T12:00:00Z"


# =========================
# HTTP helpers
# =========================
def trello_get(url, params):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def trello_post(url, params):
    r = requests.post(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


# =========================
# Board / Lists / Labels
# =========================
def get_board_id_by_name(board_name: str) -> str:
    boards = trello_get(
        "https://api.trello.com/1/members/me/boards",
        {"key": API_KEY, "token": TOKEN, "fields": "name"},
    )
    for b in boards:
        if b.get("name") == board_name:
            return b["id"]
    raise SystemExit(f'Board "{board_name}" não encontrado.')


def get_lists_map(board_id: str) -> dict:
    lists_ = trello_get(
        f"https://api.trello.com/1/boards/{board_id}/lists",
        {"key": API_KEY, "token": TOKEN, "fields": "name"},
    )
    return {lst["name"]: lst["id"] for lst in lists_}


def get_labels_map(board_id: str) -> dict:
    labels = trello_get(
        f"https://api.trello.com/1/boards/{board_id}/labels",
        {"key": API_KEY, "token": TOKEN, "limit": 1000},
    )
    return {lbl["name"]: lbl["id"] for lbl in labels if lbl.get("name")}


def pick_label_color(label_name: str) -> str:
    key = (label_name or "").strip().lower()
    return LABEL_COLORS.get(key, DEFAULT_LABEL_COLOR)


def create_label(board_id: str, label_name: str) -> str:
    color = pick_label_color(label_name)
    lbl = trello_post(
        "https://api.trello.com/1/labels",
        {
            "key": API_KEY,
            "token": TOKEN,
            "idBoard": board_id,
            "name": label_name,
            "color": color,
        },
    )
    return lbl["id"]


# =========================
# Cards
# =========================
def create_card(list_id: str, title: str, description: str = "", due_date: str | None = None) -> dict:
    params = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": list_id,
        "name": title,
        "desc": description,
    }

    if due_date:
        # Se vier só YYYY-MM-DD, normaliza para ISO seguro
        if len(due_date) == 10 and due_date[4] == "-" and due_date[7] == "-":
            params["due"] = normalize_due_date(due_date)
        else:
            # Se já vier ISO, usa como está
            params["due"] = due_date

    return trello_post("https://api.trello.com/1/cards", params)


def add_label_to_card(card_id: str, label_id: str):
    trello_post(
        f"https://api.trello.com/1/cards/{card_id}/idLabels",
        {"key": API_KEY, "token": TOKEN, "value": label_id},
    )


def add_comment_to_card(card_id: str, text: str):
    trello_post(
        f"https://api.trello.com/1/cards/{card_id}/actions/comments",
        {"key": API_KEY, "token": TOKEN, "text": text},
    )


# =========================
# Import CSV
# =========================
def import_csv():
    if not API_KEY or not TOKEN:
        raise SystemExit("API_KEY e TOKEN precisam estar definidos no .env")

    board_id = get_board_id_by_name(BOARD_NAME)
    lists_map = get_lists_map(board_id)
    labels_map = get_labels_map(board_id)

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise SystemExit("CSV sem cabeçalho.")

        print("Headers do CSV:", reader.fieldnames)

        for i, row in enumerate(reader, start=1):
            title = (row.get("Title") or "").strip()
            description = (row.get("Description") or "").strip()

            # Se você usou \n no CSV, isso vira texto literal. Converte para quebra real:
            description = description.replace("\\n", "\n")

            list_name = (row.get("List") or "").strip()
            due_date = (row.get("DueDate") or "").strip()
            labels_raw = (row.get("Labels") or "").strip()
            comments_raw = (row.get("Comments") or "").strip()  # opcional

            if not title or not list_name:
                continue

            if list_name not in lists_map:
                raise SystemExit(
                    f'[linha {i}] Lista "{list_name}" não existe. '
                    f"Listas válidas: {list(lists_map.keys())}"
                )

            card = create_card(
                list_id=lists_map[list_name],
                title=title,
                description=description,
                due_date=due_date if due_date else None,
            )

            # Labels (separa por ;)
            if labels_raw:
                for lbl in labels_raw.split(";"):
                    lbl = lbl.strip()
                    if not lbl:
                        continue

                    if lbl not in labels_map:
                        labels_map[lbl] = create_label(board_id, lbl)

                    add_label_to_card(card["id"], labels_map[lbl])

            # Comentários opcionais: separa por ||
            if comments_raw:
                for c in comments_raw.split("||"):
                    c = c.strip()
                    if c:
                        add_comment_to_card(card["id"], c)

            print(f'[OK] "{title}" → {list_name} | labels={labels_raw} | due={due_date}')


if __name__ == "__main__":
    import_csv()
    print("Importação finalizada com sucesso!")
