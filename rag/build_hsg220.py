import fitz
from pathlib import Path
from rag.hsg220_embeddings import CHAPTER_EMBEDDINGS

PDF_PATH = Path("data/documents/hsg220.pdf")
OUTPUT_PATH = Path("hsg220_clean.txt")

CHAPTER_PAGES = {
    "Chapter 1":  (7,  13),
    "Chapter 2":  (13, 16),
    "Chapter 3":  (16, 21),
    "Chapter 4":  (21, 26),
    "Chapter 5":  (26, 31),
    "Chapter 6":  (31, 34),
    "Chapter 7":  (34, 38),
    "Chapter 8":  (38, 44),
    "Chapter 9":  (44, 48),
    "Chapter 10": (48, 51),
    "Chapter 11": (51, 55),
    "Chapter 12": (55, 58),
    "Chapter 13": (58, 64),
    "Chapter 14": (64, 69),
}

NOISE_PATTERN_LINES = [
    "Health and safety in care homes",
    "Health and Safety",
    "Executive",
]


def extract_chapter_text(doc: fitz.Document, start_page: int, end_page: int) -> str:
    pages = []
    for page_idx in range(start_page, end_page):
        raw = doc[page_idx].get_text()
        lines = [
            line for line in raw.split("\n")
            if line.strip() not in NOISE_PATTERN_LINES
            and not line.strip().startswith("Page ")
        ]
        pages.append("\n".join(lines))
    return "\n".join(pages).strip()


def build_chapters(pdf_path: Path) -> list[dict]:
    doc = fitz.open(pdf_path)
    chapters = []
    for chapter_key, (start_page, end_page) in CHAPTER_PAGES.items():
        text = extract_chapter_text(doc, start_page, end_page)
        chapters.append({
            "chapter_key": chapter_key,
            "text": text,
            "embedding_string": CHAPTER_EMBEDDINGS[chapter_key],
            "pages": f"{start_page + 1}-{end_page}",
        })
    return chapters


def main():
    print(f"Opening {PDF_PATH}")
    chapters = build_chapters(PDF_PATH)
    print(f"Chapters built: {len(chapters)}")
    for ch in chapters:
        print(f"  {ch['chapter_key']}: {len(ch['text'])} chars")
    OUTPUT_PATH.write_text(
        "\n\n---\n\n".join(
            f"{ch['chapter_key']}\n{ch['text']}" for ch in chapters
        ),
        encoding="utf-8"
    )
    print(f"\nCleaned chapters written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()