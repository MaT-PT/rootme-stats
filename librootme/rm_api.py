from typing import Any, overload
from urllib.parse import parse_qs

from httpx import AsyncClient, AsyncHTTPTransport, Timeout

from .rm_datamodel import (
    _T,
    _TD,
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
    RelDict,
    RelType,
    TypedDictDataclass,
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
        print("URL:", res.request.url)
        # print(res.request.headers)
        return res.json()

    @overload
    async def get_rel_page(
        self, paged_data: PagedItem[TypedDictDataclass[_TD]], rel: RelType | Rel
    ) -> PagedItem[TypedDictDataclass[_TD]] | None: ...
    @overload
    async def get_rel_page(
        self, paged_data: PagedList[TypedDictDataclass[_TD]], rel: RelType | Rel
    ) -> PagedList[TypedDictDataclass[_TD]] | None: ...
    async def get_rel_page(
        self,
        paged_data: PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]],
        rel: RelType | Rel,
    ) -> PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]] | None:
        split_url = paged_data.rel_split(rel)
        if split_url is None:
            return None
        if f"{split_url.scheme}://{split_url.netloc}" != API_URL.rstrip("/"):
            raise ValueError(f"URL is not part of the Root-Me API: {split_url.geturl()}")

        endpoint = split_url.path.lstrip("/")
        query = parse_qs(split_url.query)
        if isinstance(paged_data, PagedItem):
            res_item = await self.api(
                endpoint,
                params=query,
                use_default_lang=False,
                return_type=tuple[_TD, *tuple[RelDict, ...]],
            )
            return PagedItem.from_pagedresult(res_item, type(paged_data.data))
        else:
            res_list = await self.api(
                endpoint,
                params=query,
                use_default_lang=False,
                return_type=tuple[DictList[_TD], *tuple[RelDict, ...]],
            )
            return PagedList.from_pagedresults(res_list, type(paged_data.data[0]))

    @overload
    async def get_prev_page(
        self, paged_data: PagedItem[TypedDictDataclass[_TD]]
    ) -> PagedItem[TypedDictDataclass[_TD]] | None: ...
    @overload
    async def get_prev_page(
        self, paged_data: PagedList[TypedDictDataclass[_TD]]
    ) -> PagedList[TypedDictDataclass[_TD]] | None: ...
    async def get_prev_page(
        self, paged_data: PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]]
    ) -> PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]] | None:
        return await self.get_rel_page(paged_data, Rel.PREV)

    @overload
    async def get_next_page(
        self, paged_data: PagedItem[TypedDictDataclass[_TD]]
    ) -> PagedItem[TypedDictDataclass[_TD]] | None: ...
    @overload
    async def get_next_page(
        self, paged_data: PagedList[TypedDictDataclass[_TD]]
    ) -> PagedList[TypedDictDataclass[_TD]] | None: ...
    async def get_next_page(
        self, paged_data: PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]]
    ) -> PagedItem[TypedDictDataclass[_TD]] | PagedList[TypedDictDataclass[_TD]] | None:
        return await self.get_rel_page(paged_data, Rel.NEXT)

    async def get_authors(
        self,
        name: str | None = None,
        account_type: AccountType | None = None,
        lang: LanguageCode | Language | None = None,
        start: int | None = None,
    ) -> PagedList[AuthorShort]:
        params: dict[str, str] = {}
        if name is not None:
            params["nom"] = name
        if account_type is not None:
            params["statut"] = account_type.value
        if lang is not None:
            params["lang"] = Language(lang).value
        if start is not None:
            params["debut_auteurs"] = str(start)
        res = await self.api(
            "auteurs",
            params=params,
            use_default_lang=False,
            return_type=tuple[DictList[AuthorShortDict], *tuple[RelDict, ...]],
        )
        return PagedList.from_pagedresults(res, AuthorShort)  # type: ignore[return-value]

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
        start: int | None = None,
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
        if start is not None:
            params["debut_challenges"] = str(start)
        res = await self.api(
            "challenges",
            params=params,
            use_default_lang=False,
            return_type=tuple[DictList[ChallengeShortDict], *tuple[RelDict, ...]],
        )

        return PagedList.from_pagedresults(res, ChallengeShort)  # type: ignore[return-value]

    async def get_challenge(
        self, challenge_id: ChallengeId, start: int | None = None
    ) -> PagedItem[Challenge]:
        params: dict[str, str] = {}
        if start is not None:
            params["debut_validations"] = str(start)
        res = await self.api(
            f"challenges/{challenge_id}",
            params=params,
            return_type=tuple[ChallengeDict, *tuple[RelDict, ...]],
        )
        return PagedItem.from_pagedresult(res, Challenge)  # type: ignore[return-value]
