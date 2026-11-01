from pathlib import Path
from .ingestion import extract_pdfs
from .data_cleaning import clean_text


def run_pipeline(raw_dir: str | Path = None, clean_dir: str | Path = None) -> dict:
    """
    Orchestra il pipeline RAG:
    1. Extract: legge PDF da raw_dir
    2. Clean: pulisce il testo
    3. Save: salva testo pulito in clean_dir

    Ritorna dict con statistiche: {"processed": N, "skipped": N}
    """
    if raw_dir is None:
        module_dir = Path(__file__).parent.parent.parent
        raw_dir = module_dir / "data" / "raw"
    if clean_dir is None:
        module_dir = Path(__file__).parent.parent.parent
        clean_dir = module_dir / "data" / "clean"

    clean_path = Path(clean_dir)
    clean_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PHASE 1: EXTRACT")
    print("=" * 60)
    raw_documents = extract_pdfs(raw_dir)
    print(f"\n→ Estratti {len(raw_documents)} documenti\n")

    print("=" * 60)
    print("PHASE 2: CLEAN")
    print("=" * 60)
    processed = 0
    skipped = 0

    for pdf_name, raw_text in raw_documents.items():
        cleaned = clean_text(raw_text)

        if cleaned is None:
            print(f"✗ {pdf_name} (vuoto dopo cleaning)")
            skipped += 1
        else:
            output_dir = clean_path / Path(pdf_name).stem
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{Path(pdf_name).stem}.txt"
            output_file.write_text(cleaned, encoding="utf-8")
            print(f"✓ {pdf_name} ({len(cleaned)} char)")
            processed += 1

    print(f"\n→ Processati {processed}, Scartati {skipped}\n")

    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    return {"processed": processed, "skipped": skipped}


def run_clean_only(raw_dir: str | Path = None, clean_dir: str | Path = None) -> dict:
    """
    Esegue SOLO il cleaning (senza extract).
    Utile per testare la fase di cleaning in isolation.
    """
    if raw_dir is None:
        module_dir = Path(__file__).parent.parent.parent
        raw_dir = module_dir / "data" / "raw"
    if clean_dir is None:
        module_dir = Path(__file__).parent.parent.parent
        clean_dir = module_dir / "data" / "clean"

    clean_path = Path(clean_dir)
    clean_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PHASE 1: EXTRACT")
    print("=" * 60)
    raw_documents = extract_pdfs(raw_dir)
    print(f"\n→ Estratti {len(raw_documents)} documenti\n")

    print("=" * 60)
    print("PHASE 2: CLEAN (standalone)")
    print("=" * 60)
    processed = 0
    skipped = 0

    for pdf_name, raw_text in raw_documents.items():
        cleaned = clean_text(raw_text)

        if cleaned is None:
            print(f"✗ {pdf_name} (vuoto dopo cleaning)")
            skipped += 1
        else:
            output_dir = clean_path / Path(pdf_name).stem
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{Path(pdf_name).stem}.txt"
            output_file.write_text(cleaned, encoding="utf-8")
            print(f"✓ {pdf_name} ({len(cleaned)} char)")
            processed += 1

    print(f"\n→ Processati {processed}, Scartati {skipped}\n")

    return {"processed": processed, "skipped": skipped}


if __name__ == "__main__":
    run_pipeline()
