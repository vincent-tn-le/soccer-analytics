"""football-data.org v4 client."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://api.football-data.org/v4"


class FootballDataOrgClient:
    def __init__(self, token: str, *, timeout: float = 30.0) -> None:
        if not token:
            raise ValueError("API token is required")
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"X-Auth-Token": token},
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> FootballDataOrgClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def get_matches(self, competition_code: str, *, season: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        return self._get(f"/competitions/{competition_code}/matches", params=params or None)

    def get_standings(self, competition_code: str, *, season: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        return self._get(f"/competitions/{competition_code}/standings", params=params or None)

    def get_teams(self, competition_code: str, *, season: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if season:
            params["season"] = season
        return self._get(f"/competitions/{competition_code}/teams", params=params or None)
