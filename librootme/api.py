from typing import Any, AsyncGenerator, cast, overload
from urllib.parse import parse_qs

from httpx import AsyncClient, AsyncHTTPTransport, Timeout

from .constants import AccountType, Language, LanguageCode, Rel, RelType
from .datamodel import (
    Author,
    AuthorDict,
    AuthorShort,
    AuthorShortDict,
    Challenge,
    ChallengeDict,
    ChallengeShort,
    ChallengeShortDict,
    ChallengeVeryShort,
    RelDict,
    TypedDictDataclass,
    ValidationChallenge,
)
from .paged import PagedItem, PagedList
from .types import _T, _TD, AuthorId, ChallengeId, DictList

API_URL = "https://api.www.root-me.org"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"


# TODO: Handle 401/404 errors


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
        # if self._lang is not None:
        #     headers["Accept-Language"] = self._lang.value

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
        headers: dict[str, str] | None = None
        if use_default_lang and self._lang is not None:
            params = params or {}
            params["lang"] = self._lang.value
            headers = {"Accept-Language": self._lang.value}
        res = await self._client.get(endpoint, params=params, headers=headers)
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

    async def iter_item_pages(
        self, paged_item: PagedItem[TypedDictDataclass[_TD]]
    ) -> AsyncGenerator[PagedItem[TypedDictDataclass[_TD]], None]:
        while True:
            yield paged_item
            res = await self.get_next_page(paged_item)
            if res is None:
                break
            paged_item = res

    async def iter_list_pages(
        self, paged_list: PagedList[TypedDictDataclass[_TD]]
    ) -> AsyncGenerator[PagedList[TypedDictDataclass[_TD]], None]:
        while True:
            yield paged_list
            res = await self.get_next_page(paged_list)
            if res is None:
                break
            paged_list = res

    async def iter_list_elements(
        self, paged_list: PagedList[TypedDictDataclass[_TD]]
    ) -> AsyncGenerator[TypedDictDataclass[_TD], None]:
        async for page in self.iter_list_pages(paged_list):
            for element in page:
                yield element

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

    async def iter_authors(
        self,
        name: str | None = None,
        account_type: AccountType | None = None,
        lang: LanguageCode | Language | None = None,
        start: int | None = None,
    ) -> AsyncGenerator[AuthorShort, None]:
        async for author in self.iter_list_elements(
            await self.get_authors(name=name, account_type=account_type, lang=lang, start=start)
        ):
            yield author  # type: ignore[misc]

    async def get_author(self, author: AuthorId | AuthorShort) -> Author:
        if isinstance(author, AuthorShort):
            author = author.id_auteur
        res = await self.api(f"auteurs/{author}", return_type=AuthorDict)
        return Author.from_dict(res)

    async def get_author_by_name(self, name: str) -> Author | None:
        async for author in self.iter_authors(name=name):
            if author.nom == name:
                return await self.get_author(author)
        return None

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
            # TODO: Find out how id_auteur[] works, it doesn't seem to do anything
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

    async def iter_challenges(
        self,
        titre: str | None = None,
        soustitre: str | None = None,
        lang: LanguageCode | Language | None = None,
        score: int | None = None,
        id_auteur: AuthorId | list[AuthorId] | None = None,
        start: int | None = None,
    ) -> AsyncGenerator[ChallengeShort, None]:
        async for challenge in self.iter_list_elements(
            await self.get_challenges(
                titre=titre,
                soustitre=soustitre,
                lang=lang,
                score=score,
                id_auteur=id_auteur,
                start=start,
            )
        ):
            yield challenge  # type: ignore[misc]

    async def get_challenge(
        self,
        challenge: ChallengeId | ChallengeShort | ChallengeVeryShort,
        start: int | None = None,
    ) -> PagedItem[Challenge]:
        if isinstance(challenge, (ChallengeShort, ChallengeVeryShort)):
            challenge = challenge.id_challenge
        params: dict[str, str] = {}
        if start is not None:
            params["debut_validations"] = str(start)
        res = await self.api(
            f"challenges/{challenge}",
            params=params,
            return_type=tuple[ChallengeDict, *tuple[RelDict, ...]],
        )
        return PagedItem.from_pagedresult(res, Challenge)  # type: ignore[return-value]

    async def iter_challenge_validations(
        self,
        challenge: ChallengeId
        | ChallengeShort
        | ChallengeVeryShort
        | Challenge
        | PagedItem[Challenge],
        start: int | None = None,
    ) -> AsyncGenerator[ValidationChallenge, None]:
        if not isinstance(challenge, PagedItem):
            if isinstance(challenge, Challenge):
                challenge = PagedItem(challenge)
            else:
                if isinstance(challenge, (ChallengeShort, ChallengeVeryShort)):
                    challenge = challenge.id_challenge
                challenge = await self.get_challenge(challenge, start=start)

        async for chall_page in self.iter_item_pages(challenge):
            chall = cast(Challenge, chall_page.data)
            for validation in chall.validations:
                yield validation
