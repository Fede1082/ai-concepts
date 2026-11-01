import typer
from rag.config import load_config
from .pipeline import run_pipeline, run_clean_only

app = typer.Typer()

# === PHASE 1: INGESTION ===
@app.command()
def ingestion():
    """Extract PDF text and clean documents."""
    run_pipeline()

@app.command()
def clean():
    """Test cleaning phase only (extract → clean, no downstream processing)."""
    run_clean_only()

# === PHASE 2: CHUNKING (coming soon) ===
@app.command()
def chunk(config: str = "configs/chunking_800.yaml"):
    """Split cleaned documents into chunks."""
    cfg = load_config(config)
    # from .chunking import run_chunking
    # run_chunking(cfg)

# === PHASE 3: EMBEDDING & VECTOR DB (coming soon) ===
# @app.command()
# def embed(config: str = "configs/embedding.yaml"):
#     """Embed chunks and save to vector database."""
#     cfg = load_config(config)
#     # from .embedding import run_embedding
#     # run_embedding(cfg)

if __name__ == "__main__":
    app()