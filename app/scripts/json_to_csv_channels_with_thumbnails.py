import json
import csv
from pathlib import Path

# Input: original big dataset with channel_content + videos
INPUT_JSON = Path("data.json")

# Output CSV: channel_id, topic_categories (text[]), thumbnail_url
OUTPUT_CSV = Path("channels_with_thumbnails.csv")


def to_pg_text_array(values):
    """Convert list[str] -> Postgres text[] literal."""
    def escape(v: str) -> str:
        # Escape backslashes and double quotes for Postgres array syntax
        return v.replace("\\", "\\\\").replace('"', '\\"')

    inner = ",".join(f'"{escape(v)}"' for v in values)
    return "{" + inner + "}"


def main():
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"{INPUT_JSON} not found")

    raw = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    seen = set()
    rows_written = 0

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Add thumbnail_url column
        writer.writerow(["channel_id", "topic_categories", "thumbnail_url"])

        for item in raw:
            cc = item.get("channel_content") or {}
            channel_id = cc.get("channel_id")
            if not channel_id or channel_id in seen:
                continue
            seen.add(channel_id)

            # topic_categories from channel_content
            topics = cc.get("topic_categories") or []
            pg_array = to_pg_text_array(topics)

            # Build thumbnail from the FIRST video, if any
            videos = item.get("videos") or []
            thumb_url = ""
            if videos:
                first_video = videos[0]
                video_id = first_video.get("video_id")
                if video_id:
                    thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

            writer.writerow([channel_id, pg_array, thumb_url])
            rows_written += 1

    print(f"Wrote CSV to {OUTPUT_CSV} ({rows_written} channels)")


if __name__ == "__main__":
    main()
