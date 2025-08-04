import yaml
from pathlib import Path
from .schema import DocumentConfig


def load_config(path: str | Path) -> DocumentConfig:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"配置檔不存在：{path}")

    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return DocumentConfig(**data)

if __name__ == "__main__":
    cfg = load_config("../sample-passport.yml")

    print(cfg.id)          # 輸出: sample-passport
    print(cfg.fields[0].key)  # 輸出: name