from urllib.parse import quote, urlencode

from src.core.riot_api import RiotApiClient


def get_challenger_league_by_queue(
    client: RiotApiClient,
    queue: str = "RANKED_SOLO_5x5",
) -> dict:
    return _get_top_league_by_queue(
        "challengerleagues",
        client,
        queue,
    )


def get_grandmaster_league_by_queue(
    client: RiotApiClient,
    queue: str = "RANKED_SOLO_5x5",
) -> dict:
    return _get_top_league_by_queue(
        "grandmasterleagues",
        client,
        queue,
    )


def get_master_league_by_queue(
    client: RiotApiClient,
    queue: str = "RANKED_SOLO_5x5",
) -> dict:
    return _get_top_league_by_queue(
        "masterleagues",
        client,
        queue,
    )


def get_league_entries_by_tier_division(
    client: RiotApiClient,
    tier: str,
    division: str,
    queue: str = "RANKED_SOLO_5x5",
    page: int = 1,
) -> list[dict]:
    queue = quote(queue, safe="")
    tier = quote(tier.upper(), safe="")
    division_map = {
        "1": "I",
        "2": "II",
        "3": "III",
        "4": "IV",
    }
    division = division_map.get(division.upper(), division.upper())
    division = quote(division, safe="")
    query = urlencode({"page": page})
    url = (
        f"https://{client.platform}.api.riotgames.com"
        f"/lol/league/v4/entries/{queue}/{tier}/{division}"
        f"?{query}"
    )

    return client.request(url)


def _get_top_league_by_queue(
    league_type: str,
    client: RiotApiClient,
    queue: str = "RANKED_SOLO_5x5",
) -> dict:
    queue = quote(queue, safe="")
    url = (
        f"https://{client.platform}.api.riotgames.com"
        f"/lol/league/v4/{league_type}/by-queue/{queue}"
    )

    return client.request(url)
