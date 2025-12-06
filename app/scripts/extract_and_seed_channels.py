#!/usr/bin/env python
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

# --------------- CONFIG ---------------

# Input file: your original big dataset
INPUT_FILE = Path("data.json")

# Output file: simplified channels list
OUTPUT_FILE = Path("channels_topics.json")

# Optional: Supabase config (used only if both env vars are set)
SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# --------------- EXTRACTION ---------------

def extract_channels(
    raw: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extract unique channels as:
    [
      {
        "channel_id": "...",
        "topic_categories": ["...", ...]
      },
      ...
    ]
    """
    result: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for item in raw:
        cc: Dict[str, Any] = item.get("channel_content") or {}
        channel_id: Optional[str] = cc.get("channel_id")
        topics = cc.get("topic_categories") or []

        if not channel_id:
            continue
        if channel_id in seen:
            continue

        seen.add(channel_id)
        result.append(
            {
                "channel_id": channel_id,
                "topic_categories": list(topics),
            }
        )

    return result


def load_raw_data(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON to be a list")
    return data


def write_simplified(path: Path, channels: List[Dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(channels, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote simplified channels to {path} (count={len(channels)})")


# --------------- OPTIONAL: SEED SUPABASE ---------------

def seed_supabase(channels: List[Dict[str, Any]]) -> None:
    """
    Bulk-upsert into Supabase 'channels' table:
      channel_id (text, PK)
      topic_categories (text[])
      is_deleted (bool, default false)
      created_at (timestamptz)
    Requires:
      - SUPABASE_URL
      - SUPABASE_SERVICE_ROLE_KEY  (service role key, NOT anon)
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set; skipping Supabase seed.")
        return

    try:
        from supabase import create_client  # pip install supabase
    except ImportError:
        print("'supabase' package not installed. Run: pip install supabase")
        return

    print("Connecting to Supabase…")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    rows = [
        {
            "channel_id": c["channel_id"],
            "topic_categories": c["topic_categories"],
            # is_deleted will use default = false
        }
        for c in channels
    ]

    # Insert in chunks to avoid huge single request
    chunk_size = 500
    total = len(rows)
    for i in range(0, total, chunk_size):
        chunk = rows[i : i + chunk_size]
        print(f"Upserting rows {i + 1}–{i + len(chunk)} of {total}…")

        resp = supabase.table("channels").upsert(chunk).execute()
        if getattr(resp, "error", None):
            print("Error inserting chunk:", resp.error)
            break

    print("Finished seeding Supabase.")


# --------------- MAIN ---------------

def main() -> None:
    print(f"Loading raw data from {INPUT_FILE} …")
    raw = load_raw_data(INPUT_FILE)

    print(f"Extracting channel_id + topic_categories from {len(raw)} entries…")
    channels = extract_channels(raw)
    print(f"Extracted {len(channels)} unique channels.")

    write_simplified(OUTPUT_FILE, channels)
    seed_supabase(channels)


if __name__ == "__main__":
    main()
