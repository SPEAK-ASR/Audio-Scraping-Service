# json_to_csv_channels.py
import json
import csv
from pathlib import Path

INPUT_JSON = Path("channels_topics.json")
OUTPUT_CSV = Path("channels_topics.csv")


def to_pg_text_array(values):
    """Convert list[str] -> Postgres text[] literal."""
    def escape(v: str) -> str:
        # Escape backslashes and double quotes for Postgres array syntax
        return v.replace("\\", "\\\\").replace('"', '\\"')

    inner = ",".join(f'"{escape(v)}"' for v in values)
    return "{" + inner + "}"


def main():
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["channel_id", "topic_categories"])

        for item in data:
            channel_id = item.get("channel_id")
            topics = item.get("topic_categories") or []

            if not channel_id:
                continue

            array_literal = to_pg_text_array(topics)
            writer.writerow([channel_id, array_literal])

    print(f"✅ Wrote CSV to {OUTPUT_CSV} ({len(data)} rows input)")


if __name__ == "__main__":
    main()
