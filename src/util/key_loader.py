from pathlib import Path

import yaml


def get_riot_api_key(key_path: str | Path) -> str:
    """Return the Riot API key from a key YAML file."""
    key_path = Path(key_path).expanduser()

    with key_path.open(encoding="utf-8") as file:
        keys = yaml.safe_load(file)

    return keys["riot"]["api_key"]
