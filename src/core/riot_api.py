import json
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class RiotApiClient:
    def __init__(self, api_key: str, configs: dict):
        riot_configs = configs["riot"]
        self.api_key = api_key
        self.platform = riot_configs["platform"]
        self.region = riot_configs["region"]
        self.request_sleep_seconds = riot_configs["request_sleep_seconds"]
        self.header_profile = riot_configs.get("header_profile", "server")
        self.last_request_url: str | None = None
        self.last_request_headers: dict[str, str] | None = None

    def request(self, url: str, timeout: int = 10):
        headers = _get_headers(self.api_key, self.header_profile)
        self.last_request_url = url
        self.last_request_headers = headers

        return request_riot_api(
            url,
            headers,
            request_sleep_seconds=self.request_sleep_seconds,
            timeout=timeout,
        )

    def get_last_request(self, mask_token: bool = True) -> dict:
        headers = dict(self.last_request_headers or {})
        if mask_token and "X-Riot-Token" in headers:
            headers["X-Riot-Token"] = _mask_token(headers["X-Riot-Token"])

        return {
            "url": self.last_request_url,
            "headers": headers,
        }


def request_riot_api(
    url: str,
    headers: dict[str, str],
    request_sleep_seconds: float = 0.0,
    timeout: int = 10,
):
    sleep_seconds = max(float(request_sleep_seconds), 0.0)
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        message = _get_error_message(error.code)
        raise RuntimeError(f"Riot API request failed: {error.code} {message}\n{body}") from error


def _get_headers(api_key: str, header_profile: str) -> dict[str, str]:
    if header_profile == "developer_portal":
        return {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": api_key,
        }

    return {
        "User-Agent": "riot-database-maker/0.1",
        "Accept": "application/json",
        "X-Riot-Token": api_key,
    }


def _mask_token(token: str) -> str:
    if len(token) <= 12:
        return "***"

    return f"{token[:8]}...{token[-4:]}"


def _get_error_message(status_code: int) -> str:
    if status_code == 401:
        return "Unauthorized. API key is missing."
    if status_code == 403:
        return "Forbidden. Check whether the API key is expired, invalid, or unauthorized."
    if status_code == 404:
        return "Not found. Check request parameters."
    if status_code == 429:
        return "Rate limit exceeded. Wait and retry after the Retry-After header."

    return "Unexpected Riot API error."
