from typing import Any, overload

from httpx import AsyncClient, AsyncHTTPTransport, Timeout

from rm_datamodel import (
    _T,
    AccountType,
    Author,
    AuthorDict,
    AuthorId,
    AuthorShort,
    AuthorShortDict,
    Challenge,
    ChallengeDict,
    ChallengeId,
    ChallengeShort,
    ChallengeShortDict,
    DictList,
    Language,
    LanguageCode,
    PagedItem,
    PagedList,
    Rel,
)

API_URL = "https://api.www.root-me.org"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"


class RootMeAPI:
    _api_key: str
    _lang: Language | None
    _client: AsyncClient

    def __init__(
        self,
        api_key: str,
        lang: LanguageCode | Language | None = None,
        user_agent: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._lang = Language(lang) if lang else None

        headers = {
            "User-Agent": user_agent or USER_AGENT,
        }
        if self._lang is not None:
            headers["Accept-Language"] = self._lang.value

        self._client = AsyncClient(
            transport=AsyncHTTPTransport(retries=3, http1=True, http2=True),
            base_url=API_URL,
            headers=headers,
            cookies={"api_key": api_key},
            timeout=Timeout(30, connect=10),
        )

    @overload
    async def api(
        self,
        endpoint: str,
        /,
        return_type: None = None,
        params: dict[str, Any] | None = None,
        use_default_lang: bool = True,
    ) -> Any: ...
    @overload
    async def api(
        self,
        endpoint: str,
        /,
        return_type: type[_T],
        params: dict[str, Any] | None = None,
        use_default_lang: bool = True,
    ) -> _T: ...

    async def api(
        self,
        endpoint: str,
        /,
        return_type: type[_T] | None = None,
        params: dict[str, Any] | None = None,
        use_default_lang: bool = True,
    ) -> _T | Any:
        if use_default_lang and self._lang is not None:
            params = params or {}
            params["lang"] = self._lang.value
        res = await self._client.get(endpoint, params=params)
        print(res.request.url)
        # print(res.request.headers)
        return res.json()

    async def get_authors(
        self,
        name: str | None = None,
        account_type: AccountType | None = None,
        lang: LanguageCode | Language | None = None,
    ) -> PagedList[AuthorShort]:
        params: dict[str, str] = {}
        if name is not None:
            params["nom"] = name
        if account_type is not None:
            params["statut"] = account_type.value
        if lang is not None:
            params["lang"] = Language(lang).value
        res = await self.api(
            "auteurs",
            params=params,
            use_default_lang=False,
            return_type=tuple[DictList[AuthorShortDict], *tuple[Rel, ...]],
        )
        return PagedList.from_pagedresults(res, AuthorShort)  # type: ignore

    async def get_author(self, author_id: AuthorId) -> Author:
        res = await self.api(f"auteurs/{author_id}", return_type=AuthorDict)
        return Author.from_dict(res)

    async def get_challenges(
        self,
        titre: str | None = None,
        soustitre: str | None = None,
        lang: LanguageCode | Language | None = None,
        score: int | None = None,
        id_auteur: AuthorId | list[AuthorId] | None = None,
    ) -> PagedList[ChallengeShort]:
        params: dict[str, str | list[str]] = {}
        if titre is not None:
            params["titre"] = titre
        if soustitre is not None:
            params["soustitre"] = soustitre
        if lang is not None:
            params["lang"] = Language(lang).value
        if score is not None:
            params["score"] = str(score)
        if id_auteur is not None:
            params["id_auteur[]"] = (
                [str(i) for i in id_auteur] if isinstance(id_auteur, list) else str(id_auteur)
            )
        res = await self.api(
            "challenges",
            params=params,
            use_default_lang=False,
            return_type=tuple[DictList[ChallengeShortDict], *tuple[Rel, ...]],
        )

        return PagedList.from_pagedresults(res, ChallengeShort)  # type: ignore

    async def get_challenge(self, challenge_id: ChallengeId) -> PagedList[Challenge]:
        res = await self.api(f"challenges/{challenge_id}", return_type=ChallengeDict)
        return PagedItem.from_pagedresult(res, target_type=Challenge)  # type: ignore
