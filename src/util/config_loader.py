from pathlib import Path

import yaml


def load_config(config_path: str | Path = "config.yaml") -> dict:
    with Path(config_path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)
