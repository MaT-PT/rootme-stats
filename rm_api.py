from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, NewType, TypeAlias
from urllib.parse import urljoin

from requests.sessions import Session

BASE_URL = "https://api.www.root-me.org"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"

UserId = NewType("UserId", str)
LanguageCode: TypeAlias = Literal["fr", "en", "de", "es", "ru", "zh"]

LANGUAGE_NAMES: dict[LanguageCode, str] = {
    "fr": "French",
    "en": "English",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "zh": "Chinese",
}


class Language(StrEnum):
    FR = "fr"
    EN = "en"
    DE = "de"
    ES = "es"
    RU = "ru"
    ZH = "zh"

    @property
    def full_name(self) -> str:
        return LANGUAGE_NAMES[self.value]


class RootMeAPI:
    def __init__(
        self,
        lang: LanguageCode | Language = Language.EN,
        base_url: str = BASE_URL,
        user_agent: str | None = None,
    ) -> None:
        self._base_url = base_url
        self._lang: LanguageCode = Language(lang).value
        self._session = Session()
        if user_agent is None:
            user_agent = USER_AGENT
        self._session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": self._lang,
            }
        )

    def get_path(
        self,
        path: str = "",
        with_lang: bool = True,
        params: dict[str, Any] | None = None,
    ) -> str:
        if with_lang:
            if params is None:
                params = {}
            params["lang"] = self._lang
        url = urljoin(self._base_url, path)
        res = self._session.get(url, params=params)
        print(res.request.url)
        return res.text


@dataclass
class User:
    name: str
    id: UserId
    account_type: str
    points: int
    position: int
