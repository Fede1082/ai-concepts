import hashlib
import json
import re
from pathlib import Path

import tiktoken

from .config import Config, ChunkingConfig


_SUPPORTED_HEADER_IDS = re.compile(r"^(?:CTR|NAR|TEC)-\d{2}$")
_TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")


def load_documents(input_dir: str | Path) -> list[tuple[Path, str]]:
    """Read all cleaned text documents, including documents in nested folders."""
    directory = Path(input_dir)
    if not directory.exists():
        raise FileNotFoundError(f"Input directory does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {directory}")

    return [
        (path, path.read_text(encoding="utf-8"))
        for path in sorted(directory.rglob("*.txt"))
        if path.is_file()
    ]


def split_by_headers(text: str, header_pattern: str) -> list[tuple[int, str, str | None]]:
    """Split text at configured CTR, NAR, and TEC structural headings.

    Returns list of (start_pos, section_text, header_id).
    header_id is the matched header (e.g., 'CTR-01') or None if no header.
    """
    pattern = re.compile(header_pattern, re.MULTILINE)
    headings = [
        match
        for match in pattern.finditer(text)
        if match.lastindex and _SUPPORTED_HEADER_IDS.fullmatch(match.group(1))
    ]

    if not headings:
        return [(0, text, None)] if text else []

    sections: list[tuple[int, str, str | None]] = []
    if headings[0].start() > 0:
        sections.append((0, text[:headings[0].start()], None))

    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        header_id = heading.group(1)  # Estrai l'ID (CTR-01, NAR-02, etc.)
        sections.append((heading.start(), text[heading.start():end], header_id))

    return sections


def _token_count(text: str) -> int:
    return len(_TOKEN_ENCODING.encode(text, disallowed_special=()))


def _split_oversized_piece(text: str, max_tokens: int) -> list[str]:
    pieces: list[str] = []
    while text:
        if _token_count(text) <= max_tokens:
            pieces.append(text)
            break

        low, high = 1, len(text)
        best = 0
        while low <= high:
            middle = (low + high) // 2
            if _token_count(text[:middle]) <= max_tokens:
                best = middle
                low = middle + 1
            else:
                high = middle - 1

        if best == 0:
            raise ValueError("max_tokens is too small to encode a text character")

        pieces.append(text[:best])
        text = text[best:]

    return pieces


def split_to_limit(text: str, max_tokens: int) -> list[str]:
    """Split text without exceeding the configured cl100k_base token limit."""
    chunks: list[str] = []
    current = ""

    for piece in re.findall(r"\s+|\S+", text):
        candidate = current + piece
        if _token_count(candidate) <= max_tokens:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if _token_count(piece) <= max_tokens:
            current = piece
            continue

        oversized_pieces = _split_oversized_piece(piece, max_tokens)
        chunks.extend(oversized_pieces[:-1])
        current = oversized_pieces[-1]

    if current:
        chunks.append(current)

    return chunks


def build_chunks(
    documents: list[tuple[Path, str]], config: ChunkingConfig
) -> list[dict[str, str | int | None]]:
    chunks: list[dict[str, str | int | None]] = []

    for path, text in documents:
        doc_name = path.stem
        doc_title = next((line.strip() for line in text.splitlines() if line.strip()), doc_name)
        if text.strip():
            title_start = text.index(doc_title)
            text = text[:title_start] + text[title_start + len(doc_title):]
        index = 0
        for section_start, section, header_id in split_by_headers(text, config.header_pattern):
            page_number = text.count("\f", 0, section_start) + 1
            pages = section.split("\f")

            for page_offset, page_text in enumerate(pages):
                if not page_text.strip():
                    continue

                for raw_text in split_to_limit(page_text, config.max_tokens):
                    chunk_text = raw_text.strip()
                    if not chunk_text:
                        continue
                    index += 1
                    chunks.append({
                        "indice": index,
                        "doc_title": doc_title,
                        "doc_name": doc_name,
                        "doc_id": f"{doc_name}_{index}",
                        "header_id": header_id,  # CTR-01, NAR-02, TEC-03, etc.
                        "hash": hashlib.sha256(chunk_text.encode("utf-8")).hexdigest(),
                        "page": page_number + page_offset,
                        "embed_text": f"{doc_title} {chunk_text}",
                        "raw_text": chunk_text,
                    })

    return chunks


def write_chunks(chunks: list[dict[str, str | int]], output_file: str | Path) -> None:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")


def run_chunking(config: Config) -> dict[str, int | str]:
    chunk_config = config.chunking
    documents = load_documents(chunk_config.input_dir)
    chunks = build_chunks(documents, chunk_config)
    write_chunks(chunks, chunk_config.output_file)
    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "output_file": str(chunk_config.output_file),
    }
