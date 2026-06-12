from src.core.account import get_puuid_by_riot_id
from src.util.config_loader import load_config
from src.util.key_loader import get_riot_api_key


def main(configs: dict):
    api_key_path = configs["keys"]["file"]
    api_key = get_riot_api_key(api_key_path)

    print(get_puuid_by_riot_id("Hide on bush", "KR1", api_key))


if __name__ == "__main__":
    configs = load_config("config.yaml")
    main(configs)
