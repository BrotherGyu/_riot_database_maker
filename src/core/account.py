from urllib.parse import quote

from src.core.riot_api import RiotApiClient


def get_puuid_by_riot_id(
    game_name: str,
    tag_line: str,
    client: RiotApiClient,
) -> str:
    game_name = quote(game_name, safe="")
    tag_line = quote(tag_line, safe="")
    url = (
        f"https://{client.region}.api.riotgames.com"
        f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    )

    account = client.request(url)
    return account["puuid"]
