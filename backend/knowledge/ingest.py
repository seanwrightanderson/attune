"""
Knowledge base ingestion script for Attune.

Run this script to chunk, embed, and store music theory content into ChromaDB.

Usage:
    cd backend
    python knowledge/ingest.py
"""

import asyncio
import hashlib
import json
import re
import sys
import os
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag import add_documents, collection_count
from config import get_settings

settings = get_settings()

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")
CHUNK_SIZE = 400   # tokens (approximate via words)
CHUNK_OVERLAP = 50


def parse_sections(markdown_text: str) -> List[dict]:
    """
    Parse a markdown file into sections based on ## headers.
    Each section becomes a document chunk with metadata.
    """
    sections = []
    current_topic = "general"
    current_difficulty = "all"
    current_header = ""
    current_content = []

    lines = markdown_text.split("\n")

    for line in lines:
        # Extract metadata from frontmatter-style comments
        if line.startswith("topic:"):
            current_topic = line.split(":", 1)[1].strip()
            continue
        if line.startswith("difficulty:"):
            current_difficulty = line.split(":", 1)[1].strip()
            continue

        # New section on ## header
        if line.startswith("## "):
            if current_header and current_content:
                content_str = "\n".join(current_content).strip()
                if content_str:
                    sections.append({
                        "header": current_header,
                        "content": content_str,
                        "topic": current_topic,
                        "difficulty": current_difficulty,
                    })
            current_header = line[3:].strip()
            current_content = []

        # Reset topic/difficulty on # header (new top-level section)
        elif line.startswith("# "):
            if current_header and current_content:
                content_str = "\n".join(current_content).strip()
                if content_str:
                    sections.append({
                        "header": current_header,
                        "content": content_str,
                        "topic": current_topic,
                        "difficulty": current_difficulty,
                    })
            current_header = ""
            current_content = []
            # Next topic/difficulty metadata will follow in the file

        else:
            current_content.append(line)

    # Don't forget the last section
    if current_header and current_content:
        content_str = "\n".join(current_content).strip()
        if content_str:
            sections.append({
                "header": current_header,
                "content": content_str,
                "topic": current_topic,
                "difficulty": current_difficulty,
            })

    return sections


def make_doc_id(topic: str, header: str) -> str:
    raw = f"{topic}::{header}"
    return hashlib.md5(raw.encode()).hexdigest()


async def ingest_file(filepath: str) -> int:
    with open(filepath, "r") as f:
        text = f.read()

    sections = parse_sections(text)
    if not sections:
        print(f"  No sections found in {filepath}")
        return 0

    documents = []
    metadatas = []
    ids = []

    for section in sections:
        doc_text = f"## {section['header']}\n\n{section['content']}"
        doc_id = make_doc_id(section["topic"], section["header"])

        documents.append(doc_text)
        metadatas.append({
            "topic": section["topic"],
            "difficulty": section["difficulty"],
            "header": section["header"],
            "source_file": os.path.basename(filepath),
        })
        ids.append(doc_id)

    await add_documents(documents, metadatas, ids)
    return len(documents)


async def ingest_songs(filepath: str) -> int:
    """Ingest songs.json — each song becomes its own searchable document."""
    with open(filepath, "r") as f:
        songs = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for song in songs:
        concepts_str = ", ".join(song.get("concepts", []))
        doc_text = (
            f"Song: {song['song']} by {song['artist']} ({song.get('year', '')})\n"
            f"Genre: {song.get('genre', '')}\n"
            f"Theory concepts: {concepts_str}\n\n"
            f"{song.get('context', '')}"
        )
        doc_id = hashlib.md5(f"song::{song['song']}::{song['artist']}".encode()).hexdigest()

        documents.append(doc_text)
        metadatas.append({
            "topic": "song_example",
            "difficulty": "all",
            "header": f"{song['song']} — {song['artist']}",
            "source_file": "songs.json",
            "concepts": concepts_str,
        })
        ids.append(doc_id)

    await add_documents(documents, metadatas, ids)
    return len(documents)


async def main():
    print("[Attune Ingest] Starting knowledge base ingestion...")

    if not os.path.exists(CONTENT_DIR):
        print(f"Content directory not found: {CONTENT_DIR}")
        return

    total = 0

    # Ingest markdown content files
    for filename in os.listdir(CONTENT_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(CONTENT_DIR, filename)
            print(f"  Processing: {filename}")
            count = await ingest_file(filepath)
            print(f"  → {count} chunks ingested")
            total += count

    # Ingest songs database
    songs_path = os.path.join(os.path.dirname(__file__), "songs.json")
    if os.path.exists(songs_path):
        print(f"  Processing: songs.json")
        count = await ingest_songs(songs_path)
        print(f"  → {count} songs ingested")
        total += count

    print(f"\n[Attune Ingest] Done. {total} total chunks in knowledge base.")
    print(f"[Attune Ingest] Collection size: {collection_count()} documents")


if __name__ == "__main__":
    asyncio.run(main())
