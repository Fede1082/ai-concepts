import yaml
# import pydantic

# class ChunkingConfig(pydantic.BaseModel):
#     input_dir: str
#     output_file: str
#     strategy: str
#     max_tokens: int
#     overlap_tokens: int
#     header_pattern: str

# with open("configs/chunking.yaml") as f:
#     cfg = yaml.safe_load(f)

# config = ChunkingConfig(**cfg)
# print(config.max_tokens)  # 800


# cli.py
import typer
from rag.config import load_config
# from rag.chunking import structural

app = typer.Typer()

@app.command()
def chunk(config: str = "configs/chunking_800.yaml"):
    cfg = load_config(config)
    # structural.run(cfg.chunking.input_dir, cfg.chunking.output_file, cfg.chunking.max_tokens)

# stesso schema per: clean, index, eval