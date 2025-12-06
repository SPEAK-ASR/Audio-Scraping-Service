#!/usr/bin/env python3
"""
Generate channels_import.csv from the original dataset data.json

Output CSV (Postgres-friendly):
  channels_import.csv

Columns:
 channel_id, topic_categories (Postgres array), thumbnail_url, domain
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Input file: your original big dataset
RAW_JSON = Path("data.json")
OUT_CSV = Path("channels_import.csv")

# Canonical enum values (your database domain enum)
CANONICAL_DOMAINS = {
    "education",
    "health",
    "politics_and_government",
    "news_and_current_affairs",
    "science",
    "technology_and_computing",
    "business_and_finance",
    "entertainment",
    "food_and_drink",
    "law_and_justice",
    "environment_and_sustainability",
    "religion",
    "media_marketing",
    "history_and_cultural",
    "work_and_careers",
    "sports",
    "music",
    "others",
}

# Mapping table: normalized topic (string) -> domain
TOPIC_TO_DOMAIN = {
    # entertainment family
    "Film": "entertainment",
    "Entertainment": "entertainment",
    "Humour": "entertainment",
    "Music": "music",
    "Television": "entertainment",
    "Movie": "entertainment",
    "Comedy": "entertainment",
    "Gaming": "entertainment",
    # education / science
    "Education": "education",
    "Science": "science",
    "Physics": "science",
    "Mathematics": "science",
    "Biology": "science",
    # technology
    "Computer science": "technology_and_computing",
    "Technology": "technology_and_computing",
    "Programming": "technology_and_computing",
    # news, politics
    "News": "news_and_current_affairs",
    "Politics": "politics_and_government",
    "Journalism": "news_and_current_affairs",
    # business & finance
    "Business": "business_and_finance",
    "Finance": "business_and_finance",
    "Economics": "business_and_finance",
    # food
    "Food": "food_and_drink",
    "Cooking": "food_and_drink",
    # law / justice
    "Law": "law_and_justice",
    # environment
    "Environment": "environment_and_sustainability",
    # religion
    "Religion": "religion",
    # marketing / media
    "Advertising": "media_marketing",
    "Marketing": "media_marketing",
    # history / culture
    "History": "history_and_cultural",
    "Culture": "history_and_cultural",
    # sports/music explicit
    "Sports": "sports",
}

def to_pg_text_array(values):
    """Convert list[str] -> Postgres text[] literal."""
    def escape(v: str) -> str:
        # Escape backslashes and double quotes for Postgres array syntax
        return v.replace("\\", "\\\\").replace('"', '\\"')

    inner = ",".join(f'"{escape(v)}"' for v in values)
    return "{" + inner + "}"

def normalize_topic(topic: str) -> str:
    """Convert a wiki URL or raw topic to a human-friendly label.

    Examples:
      'https://en.wikipedia.org/wiki/Hobby' -> 'Hobby'
      'Stand-up_comedy' -> 'Stand-up comedy'
    """
    if not topic:
        return ""
    t = topic.strip().rstrip("/")
    if "://" in t:
        # Extract from Wikipedia URL
        parts = t.split("/")
        t = parts[-1] or parts[-2] if len(parts) > 1 else t
    # Replace underscores with spaces
    t = t.replace("_", " ").strip()
    # Capitalize first letter while preserving inner casing
    if len(t) > 0:
        t = t[0].upper() + t[1:]
    return t

def map_topics_to_domain(topics: List[str]) -> str:
    """Map a list of cleaned topic labels to one canonical domain value."""
    # 1) Exact mapping first
    for t in topics:
        if t in TOPIC_TO_DOMAIN:
            return TOPIC_TO_DOMAIN[t]

    # 2) Keyword-based heuristic mapping
    joined = " ".join(topics).lower()
    
    # Entertainment categories
    if any(k in joined for k in ["film", "movie", "entertainment", "comedy", "humour", "television", "cinema", "actor", "actress", "celebrity"]):
        return "entertainment"
    
    # Music
    if any(k in joined for k in ["music", "song", "singer", "band", "musician", "album", "concert"]):
        return "music"
    
    # Sports
    if any(k in joined for k in ["sport", "cricket", "football", "tennis", "basketball", "soccer", "athletics", "olympic"]):
        return "sports"
    
    # Education
    if any(k in joined for k in ["education", "school", "university", "learning", "tutorial", "academic", "student", "teacher"]):
        return "education"
    
    # Science
    if any(k in joined for k in ["science", "physics", "biology", "chemistry", "research", "laboratory", "scientific"]):
        return "science"
    
    # Technology
    if any(k in joined for k in ["computer", "programming", "technology", "software", "coding", "internet", "digital", "tech"]):
        return "technology_and_computing"
    
    # Business & Finance
    if any(k in joined for k in ["business", "finance", "economy", "market", "invest", "money", "bank", "entrepreneur"]):
        return "business_and_finance"
    
    # Food & Drink
    if any(k in joined for k in ["food", "cooking", "recipe", "restaurant", "chef", "cuisine", "drink", "beverage"]):
        return "food_and_drink"
    
    # Law & Justice
    if any(k in joined for k in ["law", "court", "justice", "legal", "lawyer", "attorney", "judge"]):
        return "law_and_justice"
    
    # Environment
    if any(k in joined for k in ["environment", "sustainability", "climate", "ecology", "nature", "green", "conservation"]):
        return "environment_and_sustainability"
    
    # Politics & Government
    if any(k in joined for k in ["politic", "government", "election", "mp", "minister", "democracy", "parliament"]):
        return "politics_and_government"
    
    # News & Current Affairs
    if any(k in joined for k in ["news", "current affairs", "breaking", "journalist", "reporter", "media"]):
        return "news_and_current_affairs"
    
    # Religion
    if any(k in joined for k in ["religion", "buddhism", "christian", "islam", "hindu", "spiritual", "faith", "church"]):
        return "religion"
    
    # Media & Marketing
    if any(k in joined for k in ["advert", "marketing", "media", "brand", "advertising", "promotion", "social media"]):
        return "media_marketing"
    
    # History & Cultural
    if any(k in joined for k in ["history", "culture", "heritage", "archaeology", "historical", "tradition", "ancient"]):
        return "history_and_cultural"
    
    # Work & Careers
    if any(k in joined for k in ["career", "job", "resume", "work", "skills", "employment", "professional"]):
        return "work_and_careers"
    
    # Health
    if any(k in joined for k in ["health", "medical", "medicine", "doctor", "hospital", "fitness", "wellness"]):
        return "health"

    return "others"

def main():
    """Main function to generate the CSV file."""
    if not RAW_JSON.exists():
        raise FileNotFoundError(f"{RAW_JSON} not found")

    raw_data = json.loads(RAW_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(raw_data)} items from dataset")
    
    seen_channel_ids = set()
    rows_written = 0
    
    # Get current timestamp
    now_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with OUT_CSV.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header (removed is_deleted and created_at)
        writer.writerow([
            "channel_id", 
            "topic_categories", 
            "thumbnail_url", 
            "domain"
        ])
        
        for item in raw_data:
            # Extract channel content
            channel_content = item.get("channel_content", {})
            channel_id = channel_content.get("channel_id")
            
            if not channel_id or channel_id in seen_channel_ids:
                continue
            
            seen_channel_ids.add(channel_id)
            
            # Extract and normalize topic categories
            raw_topics = channel_content.get("topic_categories", [])
            normalized_topics = []
            
            for topic in raw_topics:
                if topic:  # Skip empty topics
                    normalized = normalize_topic(str(topic))
                    if normalized and normalized not in normalized_topics:
                        normalized_topics.append(normalized)
            
            # Generate thumbnail from first video if available
            thumbnail_url = ""
            videos = item.get("videos", [])
            if videos and isinstance(videos, list) and len(videos) > 0:
                first_video = videos[0]
                video_id = first_video.get("video_id")
                if video_id:
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            
            # Map topics to domain
            domain = map_topics_to_domain(normalized_topics)
            
            # Write data row (removed is_deleted and created_at)
            writer.writerow([
                channel_id,
                to_pg_text_array(normalized_topics),
                thumbnail_url,
                domain
            ])
            
            rows_written += 1
    
    print(f" Successfully generated {OUT_CSV}")
    print(f"   - {rows_written} channels processed")
    print(f"   - All channels created at: {now_ts}")
    
    # Print domain distribution for verification
    domain_counts = {}
    for item in raw_data:
        channel_content = item.get("channel_content", {})
        channel_id = channel_content.get("channel_id")
        if not channel_id:
            continue
        raw_topics = channel_content.get("topic_categories", [])
        normalized_topics = []
        for topic in raw_topics:
            if topic:
                normalized = normalize_topic(str(topic))
                if normalized and normalized not in normalized_topics:
                    normalized_topics.append(normalized)
        domain = map_topics_to_domain(normalized_topics)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print("\nDomain distribution:")
    for domain, count in sorted(domain_counts.items()):
        print(f"   {domain}: {count}")

if __name__ == "__main__":
    main()