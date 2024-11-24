import requests
import json

# Notion の設定
NOTION_API_TOKEN = "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"
DATABASE_ID = "14728509e2b2809c8161f7d563958d75"

headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_notion_entries():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    data = response.json()
    print(data)  # レスポンスデータを表示
    if response.status_code != 200:
        print(f"Notion API からのエラー: {data.get('message')}")
        return []
    if "results" not in data:
        print("レスポンスデータに 'results' キーがありません。")
        return []
    entries = []

    for result in data["results"]:
        properties = result["properties"]

        # 各フィールドからデータを取得
        spell = (
            properties["Name"]["title"][0]["plain_text"]
            if properties["Name"]["title"]
            else ""
        )
        pronunciation = (
            properties["Pronunciation"]["rich_text"][0]["plain_text"]
            if properties["Pronunciation"]["rich_text"]
            else ""
        )
        category = (
            properties["Category"]["select"]["name"]
            if properties["Category"]["select"]
            else ""
        )
        in_japanese = (
            properties["In Japanese"]["rich_text"][0]["plain_text"]
            if properties["In Japanese"]["rich_text"]
            else ""
        )
        example = (
            properties["Example"]["rich_text"][0]["plain_text"]
            if properties["Example"]["rich_text"]
            else ""
        )

        entries.append(
            {
                "spell": spell,
                "pronunciation": pronunciation,
                "category": category,
                "in_japanese": in_japanese,
                "example": example,
            }
        )

    return entries


def add_card_to_anki(entry):
    anki_connect_url = "http://localhost:8765"
    note = {
        "deckName": "default",  # デッキ名を修正
        "modelName": "NotionWord",  # Anki で作成したノートタイプの名前
        "fields": {
            "Spell": entry["spell"],
            "Pronunciation": entry["pronunciation"],
            "Category": entry["category"],
            "In Japanese": entry["in_japanese"],
            "Example": entry["example"],
            "Front": entry["spell"] or "No data",  # 空フィールドを防止
            "Back": entry["in_japanese"] or "No data",
        },
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "deck",
            "duplicateScopeOptions": {
                "deckName": "default",
                "checkChildren": False,
                "checkAllModels": False,
            },
        },
        "tags": ["Notion"],
    }
    # デバッグ用: 送信データを表示
    print("送信データ:", json.dumps(note, indent=4, ensure_ascii=False))

    payload = {"action": "addNote", "version": 6, "params": {"note": note}}
    response = requests.post(anki_connect_url, data=json.dumps(payload))
    return response.json()


def main():
    entries = get_notion_entries()
    for entry in entries:
        result = add_card_to_anki(entry)
        if result.get("error") is None:
            print(f"カードを追加しました： {entry['spell']}")
        else:
            print(f"エラーが発生しました： {entry['spell']} - {result['error']}")


if __name__ == "__main__":
    main()
