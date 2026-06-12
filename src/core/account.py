import json
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


def get_puuid_by_riot_id(
    game_name: str,
    tag_line: str,
    api_key: str,
    region: str = "asia",
) -> str:
    game_name = quote(game_name, safe="")
    tag_line = quote(tag_line, safe="")
    url = (
        f"https://{region}.api.riotgames.com"
        f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    )
    headers = {
        "User-Agent": "riot-database-maker/0.1",
        "Accept": "application/json",
        "X-Riot-Token": api_key,
    }
    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=10) as response:
            account = json.load(response)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        message = _get_error_message(error.code)
        raise RuntimeError(f"Riot API request failed: {error.code} {message}\n{body}") from error

    return account["puuid"]


def _get_error_message(status_code: int) -> str:
    if status_code == 401:
        return "Unauthorized. API key is missing."
    if status_code == 403:
        return "Forbidden. Check whether the API key is expired, invalid, or unauthorized."
    if status_code == 404:
        return "Not found. Check game_name, tag_line, and region."
    if status_code == 429:
        return "Rate limit exceeded. Wait and retry after the Retry-After header."

    return "Unexpected Riot API error."
