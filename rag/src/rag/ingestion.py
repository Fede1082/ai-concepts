from pathlib import Path
from pypdf import PdfReader


def extract_pdfs(raw_dir: str | Path = None) -> dict[str, str]:
    """
    Estrae testo grezzo da tutti i PDF in raw_dir.
    Ritorna dict: {pdf_name: raw_text}
    """
    if raw_dir is None:
        module_dir = Path(__file__).parent.parent.parent
        raw_dir = module_dir / "data" / "raw"

    raw_path = Path(raw_dir)

    if not raw_path.exists():
        raise FileNotFoundError(f"Directory {raw_dir} non esiste")

    documents = {}

    for pdf_file in sorted(raw_path.glob("*.pdf")):
        if not pdf_file.is_file():
            continue

        try:
            reader = PdfReader(pdf_file)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

            raw_text = "\n".join(pages_text)
            documents[pdf_file.name] = raw_text
            print(f"✓ Estratto {pdf_file.name}")
        except Exception as e:
            print(f"✗ Errore lettura {pdf_file.name}: {e}")

    return documents


if __name__ == "__main__":
    docs = extract_pdfs()
    print(f"\nEstratti {len(docs)} documenti")







