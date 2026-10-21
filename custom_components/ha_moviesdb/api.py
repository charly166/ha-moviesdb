"""Schlanker asynchroner Client für die kostenlose themoviedb.org (TMDB) API v3.

Es wird bewusst kein zusätzliches Python-Paket genutzt, sondern nur die in
Home Assistant ohnehin vorhandene aiohttp-Session, damit die Integration
keine externen Requirements benötigt.

API-Dokumentation: https://developer.themoviedb.org/reference/intro/getting-started
Watch-Provider-Daten stammen von JustWatch und werden von TMDB durchgereicht:
https://developer.themoviedb.org/docs/watch-providers-attribution-requirement
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import async_timeout
from aiohttp import ClientSession, ContentTypeError

from .const import (
    FALLBACK_REGIONS,
    NOW_PLAYING_MAX_PAGES,
    TMDB_BASE_URL,
    TMDB_IMAGE_BASE,
    TMDB_LANGUAGE,
    TMDB_POSTER_SIZE,
    TMDB_PROVIDER_LOGO_SIZE,
)

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 20

PROVIDER_CATEGORIES = ("flatrate", "rent", "buy", "ads", "free")


class TMDBError(Exception):
    """Allgemeiner Fehler bei der Kommunikation mit themoviedb.org."""


class TMDBAuthError(TMDBError):
    """API-Key wurde von themoviedb.org abgelehnt."""


def _image_url(path: str | None, size: str) -> str:
    if not path:
        return ""
    return f"{TMDB_IMAGE_BASE}{size}{path}"


def _map_provider(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": item.get("provider_id"),
        "provider_name": item.get("provider_name", ""),
        "logo_path": _image_url(item.get("logo_path"), TMDB_PROVIDER_LOGO_SIZE),
    }


def _map_movie_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Vereinfacht einen Eintrag aus Listen-Endpunkten (Suche, Im Kino)."""
    movie_id = item.get("id")
    if movie_id is None:
        return None
    release_date = item.get("release_date") or ""
    return {
        "movie_id": str(movie_id),
        "title": item.get("title") or item.get("original_title") or "?",
        "overview": item.get("overview", ""),
        "image": _image_url(item.get("poster_path"), TMDB_POSTER_SIZE),
        "release_year": release_date[:4],
        "release_date": release_date,
    }


# Home-Assistant-Sprache -> TMDB-Sprachcode (TMDB erwartet z.B. "de-DE").
_TMDB_LANGUAGE_MAP = {
    "de": "de-DE",
    "en": "en-US",
    "zh-Hans": "zh-CN",
    "zh-Hant": "zh-TW",
    "nb": "no",
}


def tmdb_language(ha_language: str | None) -> str:
    """Leitet die TMDB-Sprache aus der Home-Assistant-Sprache ab (Fallback: Deutsch)."""
    if not ha_language:
        return TMDB_LANGUAGE
    return _TMDB_LANGUAGE_MAP.get(ha_language, ha_language)


class TMDBClient:
    """Kapselt die wenigen TMDB-Endpunkte, die diese Integration braucht.

    TMDB nutzt (in der kostenlosen "API Key (v3 auth)"-Variante) einen
    simplen API-Key, der bei jeder Anfrage als Query-Parameter mitgeschickt
    wird – es ist also kein separater Login-Schritt nötig.
    """

    def __init__(
        self, session: ClientSession, api_key: str, language: str = TMDB_LANGUAGE
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._language = language

    @property
    def language(self) -> str:
        """TMDB-Sprache, in der Titel, Beschreibungen usw. abgefragt werden."""
        return self._language

    async def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = {"api_key": self._api_key, "language": self._language}
        if params:
            query.update(params)

        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                resp = await self._session.get(f"{TMDB_BASE_URL}{path}", params=query)
        except Exception as err:  # noqa: BLE001
            raise TMDBError(f"Anfrage an themoviedb.org fehlgeschlagen: {err}") from err

        if resp.status == 401:
            raise TMDBAuthError("API-Key wurde von themoviedb.org abgelehnt (401).")
        if resp.status == 404:
            raise TMDBError("Nicht gefunden (404) bei themoviedb.org.")
        if resp.status == 429:
            raise TMDBError("Rate-Limit von themoviedb.org erreicht, bitte kurz warten.")
        if resp.status != 200:
            raise TMDBError(f"themoviedb.org antwortete mit HTTP {resp.status} für {path}.")

        try:
            return await resp.json()
        except ContentTypeError as err:
            raise TMDBError("Unerwartete Antwort von themoviedb.org.") from err

    async def async_test_connection(self) -> None:
        """Wird beim Einrichten des Config-Flows genutzt, um den API-Key zu prüfen."""
        await self._request("/authentication")

    async def async_search_movies(self, query: str) -> list[dict[str, Any]]:
        """Sucht Filme über /search/movie und liefert eine vereinfachte Liste zurück."""
        data = await self._request(
            "/search/movie", params={"query": query, "include_adult": "false"}
        )
        mapped = (_map_movie_item(item) for item in data.get("results", []))
        return [movie for movie in mapped if movie]

    async def async_get_now_playing(self, region: str) -> list[dict[str, Any]]:
        """Holt die Filme, die aktuell in der Region im Kino laufen.

        Nutzt /movie/now_playing (TMDB-Reihenfolge bleibt erhalten). Die
        weiteren Seiten werden parallel geholt, doppelte Einträge entfernt.
        """
        first = await self._request("/movie/now_playing", params={"region": region, "page": 1})
        pages = [first]
        total_pages = min(first.get("total_pages") or 1, NOW_PLAYING_MAX_PAGES)
        if total_pages > 1:
            pages.extend(
                await asyncio.gather(
                    *(
                        self._request("/movie/now_playing", params={"region": region, "page": page})
                        for page in range(2, total_pages + 1)
                    )
                )
            )

        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        for page in pages:
            for item in page.get("results", []):
                movie = _map_movie_item(item)
                if movie and movie["movie_id"] not in seen:
                    seen.add(movie["movie_id"])
                    results.append(movie)
        return results

    async def async_get_movie(self, movie_id: str) -> dict[str, Any]:
        """Holt Filminfos (Titel, Poster, Beschreibung, Laufzeit, Jahr)."""
        movie = await self._request(f"/movie/{movie_id}")
        year = (movie.get("release_date") or "")[:4]
        return {
            "movie_id": str(movie_id),
            "title": movie.get("title") or movie.get("original_title") or "?",
            "overview": movie.get("overview", ""),
            "image": _image_url(movie.get("poster_path"), TMDB_POSTER_SIZE),
            "release_year": year,
            "runtime": movie.get("runtime"),
            "language": self._language,
        }

    async def async_get_watch_providers(self, movie_id: str, region: str) -> dict[str, Any]:
        """Holt die Streaming-Verfügbarkeit eines Films für eine Region.

        TMDB liefert die Daten (von JustWatch) verschachtelt unter
        ``results.<region>``. Existiert die Region nicht in der Antwort
        (keine bekannten Angebote in diesem Land), werden leere Listen
        zurückgegeben statt eines Fehlers.
        """
        data = await self._request(f"/movie/{movie_id}/watch/providers")
        region_data = (data.get("results") or {}).get(region, {})

        result: dict[str, Any] = {"link": region_data.get("link", "")}
        for category in PROVIDER_CATEGORIES:
            result[category] = [_map_provider(p) for p in region_data.get(category, [])]
        return result

    async def async_get_watch_provider_list(self, region: str) -> list[dict[str, Any]]:
        """Holt die vollständige, aktuelle Anbieterliste für eine Region.

        Wird von der Options-Flow-UI genutzt, damit die Auswahl der eigenen
        Streamingdienste immer den echten, aktuellen TMDB-Katalog zeigt statt
        einer hartkodierten (und damit potenziell veralteten) Liste.
        """
        data = await self._request(
            "/watch/providers/movie", params={"watch_region": region}
        )
        return [_map_provider(item) for item in data.get("results", [])]

    async def async_get_watch_provider_regions(self) -> dict[str, str]:
        """Holt die Liste der von TMDB unterstützten Watch-Provider-Regionen.

        Fällt bei einem Fehler auf eine kleine statische Liste gängiger
        Länder zurück, damit die Options-Flow-UI trotzdem nutzbar bleibt.
        """
        try:
            data = await self._request("/watch/providers/regions")
        except TMDBError as err:
            _LOGGER.warning("Konnte Regionenliste nicht laden, nutze Fallback: %s", err)
            return dict(FALLBACK_REGIONS)

        regions = {}
        for item in data.get("results", []):
            code = item.get("iso_3166_1")
            name = item.get("english_name") or item.get("native_name")
            if code and name:
                regions[code] = name
        return regions or dict(FALLBACK_REGIONS)
