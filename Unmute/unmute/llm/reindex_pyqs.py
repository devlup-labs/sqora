import argparse
import re
from pathlib import Path
from typing import Iterable, List

from qdrant_client.models import Distance, VectorParams

from unmute.llm.rag_proxy import (
    QDRANT_COLLECTION,
    add_documents,
    client,
    embedder,
)


QUESTION_PATTERN = re.compile(r"<q>(.*?)</q>", flags=re.IGNORECASE | re.DOTALL)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_long_chunk(text: str, max_chars: int) -> List[str]:
    if len(text) <= max_chars:
        return [text]

    parts: List[str] = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            parts.append(current)
        if len(sentence) <= max_chars:
            current = sentence
        else:
            for i in range(0, len(sentence), max_chars):
                parts.append(sentence[i : i + max_chars])
            current = ""
    if current:
        parts.append(current)
    return parts


def extract_chunks(text: str, max_chars: int, min_chars: int) -> List[str]:
    chunks: List[str] = []

    q_matches = QUESTION_PATTERN.findall(text)
    if q_matches:
        for raw in q_matches:
            cleaned = normalize_text(raw)
            if len(cleaned) < min_chars:
                continue
            chunks.extend(split_long_chunk(cleaned, max_chars=max_chars))
        return chunks

    for block in re.split(r"\n\s*\n+", text):
        cleaned = normalize_text(block)
        if len(cleaned) < min_chars:
            continue
        chunks.extend(split_long_chunk(cleaned, max_chars=max_chars))

    return chunks


def discover_files(source_paths: Iterable[str], glob_pattern: str) -> List[Path]:
    files: List[Path] = []
    for raw in source_paths:
        p = Path(raw)
        if p.is_file():
            files.append(p)
            continue
        if p.is_dir():
            files.extend(sorted(p.glob(glob_pattern)))
    return files


def rebuild_collection(chunks: List[str], recreate: bool, batch_size: int) -> None:
    if recreate:
        try:
            client.delete_collection(QDRANT_COLLECTION)
            print(f"Deleted existing collection: {QDRANT_COLLECTION}")
        except Exception:
            print(f"Collection {QDRANT_COLLECTION} did not exist; creating fresh")

    dim = int(embedder.get_sentence_embedding_dimension())
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    print(f"Created collection {QDRANT_COLLECTION} with dimension {dim}")

    total = len(chunks)
    for start in range(0, total, batch_size):
        batch = chunks[start : start + batch_size]
        add_documents(batch)
        print(f"Indexed {min(start + len(batch), total)}/{total} chunks")


def main() -> None:
    parser = argparse.ArgumentParser(description="Reindex pyqs collection from text corpora")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="File or directory to ingest. Can be provided multiple times.",
    )
    parser.add_argument(
        "--glob",
        default="*.txt",
        help="Glob when a source is a directory (default: *.txt)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1200,
        help="Maximum characters per chunk",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=40,
        help="Minimum characters required for a chunk",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for upserts",
    )
    parser.add_argument(
        "--no-recreate",
        action="store_true",
        help="Do not recreate the collection before indexing",
    )

    args = parser.parse_args()

    sources = list(args.source)
    if not sources:
        sources = [
            "/home/raid/sqora/VLM_Testing/images_test/image_testing",
            "/home/raid/sqora/Vector_DB/qdrant/Data/Papers",
            str(Path(__file__).parents[3] / "manim" / "app" / "data"),
        ]

    files = discover_files(sources, args.glob)
    if not files:
        raise SystemExit("No source files found for ingestion.")

    all_chunks: List[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        chunks = extract_chunks(text, max_chars=args.max_chars, min_chars=args.min_chars)
        all_chunks.extend([f"SOURCE: {f.name}\n{chunk}" for chunk in chunks])
        print(f"{f}: extracted {len(chunks)} chunks")

    if not all_chunks:
        raise SystemExit("No chunks extracted from source files.")

    print(f"Total chunks prepared: {len(all_chunks)}")
    rebuild_collection(
        chunks=all_chunks,
        recreate=not args.no_recreate,
        batch_size=args.batch_size,
    )

    info = client.get_collection(QDRANT_COLLECTION)
    points_count = int(getattr(info, "points_count", 0) or 0)
    print(f"Reindex complete. Collection={QDRANT_COLLECTION}, points={points_count}")


if __name__ == "__main__":
    main()
