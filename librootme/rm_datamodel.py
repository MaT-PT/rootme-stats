from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    NewType,
    NotRequired,
    Self,
    Sequence,
    TypeAlias,
    TypedDict,
    TypeVar,
    overload,
)
from urllib.parse import SplitResult, parse_qs, parse_qsl, urlsplit

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)
_TD = TypeVar("_TD", bound=Mapping[str, Any])
_TD_co = TypeVar("_TD_co", bound=Mapping[str, Any], covariant=True)
_TD_contra = TypeVar("_TD_contra", bound=Mapping[str, Any], contravariant=True)

AuthorId = NewType("AuthorId", int)
ChallengeId = NewType("ChallengeId", int)
SolutionId = NewType("SolutionId", int)
CategoryId = NewType("CategoryId", int)
ChallengeIndex = NewType("ChallengeIndex", str)
DifficultyStr = NewType("DifficultyStr", str)
Url = NewType("Url", str)
RelativeUrl = NewType("RelativeUrl", str)
RelativeLocalizedUrl = NewType("RelativeLocalizedUrl", str)
IntStr = NewType("IntStr", str)
DateStr = NewType("DateStr", str)

DictList: TypeAlias = dict[IntStr, _T]

BoolStr: TypeAlias = Literal["true", "false"]
LanguageCode: TypeAlias = Literal["fr", "en", "de", "es", "ru", "zh"]
AccountTypeCode: TypeAlias = Literal[
    "0minirezo",
    "5pre",
    "1comite",
    "6forum",
    "nouveau",
    "aconfirmer",
    "5cheater",
    "5leaker",
    "5poubelle",
    "5banned",
]
RankCode: TypeAlias = Literal[
    "visitor", "curious", "trainee", "insider", "enthusiast", "hacker", "elite", "legend"
]
RelType: TypeAlias = Literal["previous", "next"]

LANGUAGE_NAMES: dict[LanguageCode, str] = {
    "fr": "French",
    "en": "English",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "zh": "Chinese",
}
ACCOUNT_TYPE_COLORS: dict[AccountTypeCode, str] = {
    "0minirezo": "#767676",
    "5pre": "#DE2B0F",
    "1comite": "#DE770F",
    "6forum": "#00CC00",
}


def parse_bool(value: BoolStr) -> bool:
    return value == "true"


def parse_int(value: IntStr) -> int:
    return int(value)


def parse_date(value: DateStr) -> datetime:
    return datetime.fromisoformat(value)


def split_url(value: Url) -> SplitResult:
    return urlsplit(value)


def parse_url_qs(value: Url) -> dict[str, list[str]]:
    return parse_qs(split_url(value).query)


def parse_url_qsl(value: Url) -> list[tuple[str, str]]:
    return parse_qsl(split_url(value).query)


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


class AccountType(StrEnum):
    ADMIN = "0minirezo"
    PREMIUM = "5pre"
    REDACTOR = "1comite"
    VISITOR = "6forum"
    NEW = "nouveau"
    UNCONFIRMED = "aconfirmer"
    CHEATER = "5cheater"
    LEAKER = "5leaker"
    TRASH = "5poubelle"
    BANNED = "5banned"

    def __str__(self) -> str:
        return self.name.capitalize()

    @property
    def is_banned(self) -> bool:
        return self in {
            AccountType.CHEATER,
            AccountType.LEAKER,
            AccountType.TRASH,
            AccountType.BANNED,
        }

    @property
    def color(self, default: str = "#CCCCCC") -> str:
        return ACCOUNT_TYPE_COLORS.get(self.value, default)


class Rank(StrEnum):
    VISITOR = "visitor"
    CURIOUS = "curious"
    TRAINEE = "trainee"
    INSIDER = "insider"
    ENTHUSIAST = "enthusiast"
    HACKER = "hacker"
    ELITE = "elite"
    LEGEND = "legend"

    def __str__(self) -> str:
        return self.name.capitalize()


class Rel(StrEnum):
    PREV = "previous"
    NEXT = "next"


class RelDict(TypedDict):
    rel: RelType
    href: Url


class PagedData(ABC, Generic[_T_co]):
    _data: _T_co
    _rels: dict[RelType, Url]

    def __init__(self, data: _T_co, rels: dict[RelType, Url] | None = None) -> None:
        self._data = data
        self._rels = rels or {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._data!r}, {self._rels!r})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._data == other._data and self._rels == other._rels

    @property
    def data(self) -> _T_co:
        return self._data

    @property
    def rels(self) -> dict[RelType, Url]:
        return self._rels

    def rel(self, rel: RelType | Rel) -> Url | None:
        return self._rels.get(rel.value if isinstance(rel, Rel) else rel)

    def rel_split(self, rel: RelType | Rel) -> SplitResult | None:
        url = self.rel(rel)
        return None if url is None else split_url(url)

    @property
    def prev(self) -> Url | None:
        return self.rel(Rel.PREV)

    @property
    def next(self) -> Url | None:
        return self.rel(Rel.NEXT)

    @property
    def prev_split(self) -> SplitResult | None:
        url = self.prev
        return None if url is None else split_url(url)

    @property
    def next_split(self) -> SplitResult | None:
        url = self.next
        return None if url is None else split_url(url)

    @property
    def prev_start(self) -> int | None:
        url = self.prev
        if url is None:
            return None
        query = parse_url_qsl(url)
        start_values = [int(v) for k, v in query if k.startswith("debut_")]
        if len(start_values) == 0:
            return 0
        if len(start_values) > 1:
            raise ValueError(f"Multiple start values found in previous URL query: {url}")
        return start_values[0]

    @property
    def next_start(self) -> int | None:
        url = self.next
        if url is None:
            return None
        query = parse_url_qsl(url)
        start_values = [int(v) for k, v in query if k.startswith("debut_")]
        if len(start_values) == 0:
            return 0
        if len(start_values) > 1:
            raise ValueError(f"Multiple start values found in next URL query: {url}")
        return start_values[0]


class PagedItem(PagedData[_T_co]):
    @classmethod
    def from_rawrels(cls: type[PagedItem[_T]], data: _T, *rels: RelDict) -> PagedItem[_T]:
        return cls(data, {rel["rel"]: rel["href"] for rel in rels})

    @staticmethod
    def from_pagedresult(
        result: tuple[_TD, *tuple[RelDict, ...]],
        target_type: type[TypedDictDataclass[_TD]],
    ) -> PagedItem[TypedDictDataclass[_TD]]:
        return PagedItem[TypedDictDataclass[_TD]].from_rawrels(
            target_type.from_dict(result[0]), *result[1:]
        )


class PagedList(PagedData[Sequence[_T_co]], Sequence[_T_co]):
    def __init__(self, data: Iterable[_T_co], rels: dict[RelType, Url] | None = None) -> None:
        super().__init__(list(data), rels)

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self._data)

    @overload
    def __getitem__(self, index: int) -> _T_co: ...
    @overload
    def __getitem__(self, index: slice) -> Self: ...
    def __getitem__(self, index: int | slice) -> _T_co | Self:
        if isinstance(index, slice):
            return type(self)(self._data[index], self._rels)
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, value: Any) -> bool:
        return value in self._data

    def __reversed__(self) -> Iterator[_T_co]:
        return reversed(self._data)

    @classmethod
    def from_rawrels(cls, data: Iterable[_T_co], *rels: RelDict) -> Self:
        return cls(data, {rel["rel"]: rel["href"] for rel in rels})

    @staticmethod
    def from_pagedresults(
        results: tuple[DictList[_TD], *tuple[RelDict, ...]],
        target_type: type[TypedDictDataclass[_TD]],
    ) -> PagedList[TypedDictDataclass[_TD]]:
        return PagedList[TypedDictDataclass[_TD]].from_rawrels(
            target_type.from_dictlist(results[0]), *results[1:]
        )


class TypedDictDataclass(ABC, Generic[_TD]):
    # _base_typed_dict: ClassVar[type[Mapping[str, Any]]]  # ClassVar[type[_TD]] not supported

    @classmethod
    @abstractmethod
    def from_dict(cls, data: _TD) -> Self: ...

    @classmethod
    def from_dictlist(cls, dictlist: DictList[_TD]) -> list[Self]:
        return [cls.from_dict(val) for val in dictlist.values()]


class AuthorShortDict(TypedDict):
    id_auteur: IntStr
    nom: str


@dataclass
class AuthorShort(TypedDictDataclass[AuthorShortDict]):
    id_auteur: AuthorId
    nom: str

    @classmethod
    def from_dict(cls, data: AuthorShortDict) -> Self:
        return cls(
            id_auteur=AuthorId(parse_int(data["id_auteur"])),
            nom=data["nom"],
        )


class AuthorDict(TypedDict):
    id_auteur: IntStr
    nom: str
    statut: AccountTypeCode
    logo_url: str
    score: str
    position: int | Literal[""]
    rang: NotRequired[RankCode]
    membre: BoolStr
    challenges: list[ChallengeVeryShortDict]
    solutions: list[SolutionDict]
    validations: list[ValidationAuthorDict]


@dataclass
class Author(TypedDictDataclass[AuthorDict]):
    id_auteur: AuthorId
    nom: str
    statut: AccountType
    logo_url: RelativeUrl
    score: int
    position: int | None
    rang: Rank | None
    membre: bool
    challenges: list[ChallengeVeryShort]
    solutions: list[Solution]
    validations: list[ValidationAuthor]

    @classmethod
    def from_dict(cls, data: AuthorDict) -> Self:
        return cls(
            id_auteur=AuthorId(parse_int(data["id_auteur"])),
            nom=data["nom"],
            statut=AccountType(data["statut"]),
            logo_url=RelativeUrl(data["logo_url"]),
            score=int(data["score"]),
            position=data["position"] or None,
            rang=Rank(data["rang"]) if "rang" in data else None,
            membre=parse_bool(data["membre"]),
            challenges=[
                ChallengeVeryShort.from_dict(challenge) for challenge in data["challenges"]
            ],
            solutions=[Solution.from_dict(solution) for solution in data["solutions"]],
            validations=[
                ValidationAuthor.from_dict(validation) for validation in data["validations"]
            ],
        )


class ChallengeVeryShortDict(TypedDict):
    id_challenge: IntStr
    titre: str
    url_challenge: str


@dataclass
class ChallengeVeryShort(TypedDictDataclass[ChallengeVeryShortDict]):
    id_challenge: ChallengeId
    titre: str
    url_challenge: RelativeLocalizedUrl

    @classmethod
    def from_dict(cls, data: ChallengeVeryShortDict) -> Self:
        return cls(
            id_challenge=ChallengeId(parse_int(data["id_challenge"])),
            titre=data["titre"],
            url_challenge=RelativeLocalizedUrl(data["url_challenge"]),
        )


class ChallengeShortDict(TypedDict):
    id_challenge: IntStr
    id_rubrique: IntStr
    titre: str
    lang: LanguageCode
    date_publication: DateStr
    maj: DateStr


@dataclass
class ChallengeShort(TypedDictDataclass[ChallengeShortDict]):
    id_challenge: ChallengeId
    id_rubrique: CategoryId
    titre: str
    lang: Language
    date_publication: datetime
    maj: datetime

    @classmethod
    def from_dict(cls, data: ChallengeShortDict) -> Self:
        return cls(
            id_challenge=ChallengeId(parse_int(data["id_challenge"])),
            id_rubrique=CategoryId(parse_int(data["id_rubrique"])),
            titre=data["titre"],
            lang=Language(data["lang"]),
            date_publication=parse_date(data["date_publication"]),
            maj=parse_date(data["maj"]),
        )


class ChallengeDict(TypedDict):
    titre: str
    rubrique: str
    soustitre: str
    score: IntStr
    index_challenge: ChallengeIndex
    id_rubrique: IntStr
    id_trad: IntStr
    url_challenge: RelativeLocalizedUrl
    date_publication: DateStr
    maj: DateStr
    difficulte: DifficultyStr
    auteurs: DictList[AuthorShortDict]
    validations: DictList[ValidationChallengeDict]


@dataclass
class Challenge(TypedDictDataclass[ChallengeDict]):
    titre: str
    rubrique: str
    soustitre: str
    score: int
    index_challenge: ChallengeIndex
    id_rubrique: CategoryId
    id_trad: ChallengeId
    url_challenge: RelativeLocalizedUrl
    date_publication: datetime
    maj: datetime
    difficulte: DifficultyStr
    auteurs: list[AuthorShort]
    validations: list[ValidationChallenge]

    @classmethod
    def from_dict(cls, data: ChallengeDict) -> Self:
        return cls(
            titre=data["titre"],
            rubrique=data["rubrique"],
            soustitre=data["soustitre"],
            score=parse_int(data["score"]),
            index_challenge=ChallengeIndex(data["index_challenge"]),
            id_rubrique=CategoryId(parse_int(data["id_rubrique"])),
            id_trad=ChallengeId(parse_int(data["id_trad"])),
            url_challenge=RelativeLocalizedUrl(data["url_challenge"]),
            date_publication=parse_date(data["date_publication"]),
            maj=parse_date(data["maj"]),
            difficulte=DifficultyStr(data["difficulte"]),
            auteurs=[AuthorShort.from_dict(author) for author in data["auteurs"].values()],
            validations=[
                ValidationChallenge.from_dict(validation)
                for validation in data["validations"].values()
            ],
        )


class SolutionDict(TypedDict):
    id_solution: IntStr
    url_solution: str


@dataclass
class Solution(TypedDictDataclass[SolutionDict]):
    id_solution: SolutionId
    url_solution: RelativeLocalizedUrl

    @classmethod
    def from_dict(cls, data: SolutionDict) -> Self:
        return cls(
            id_solution=SolutionId(parse_int(data["id_solution"])),
            url_solution=RelativeLocalizedUrl(data["url_solution"]),
        )


class ValidationAuthorDict(TypedDict):
    id_challenge: IntStr
    titre: str
    id_rubrique: IntStr
    date: DateStr


@dataclass
class ValidationAuthor(TypedDictDataclass[ValidationAuthorDict]):
    id_challenge: ChallengeId
    titre: str
    id_rubrique: CategoryId
    date: datetime

    @classmethod
    def from_dict(cls, data: ValidationAuthorDict) -> Self:
        return cls(
            id_challenge=ChallengeId(parse_int(data["id_challenge"])),
            titre=data["titre"],
            id_rubrique=CategoryId(parse_int(data["id_rubrique"])),
            date=parse_date(data["date"]),
        )


class ValidationChallengeDict(TypedDict):
    id_auteur: IntStr
    date: DateStr


@dataclass
class ValidationChallenge(TypedDictDataclass[ValidationChallengeDict]):
    id_auteur: AuthorId
    date: datetime

    @classmethod
    def from_dict(cls, data: ValidationChallengeDict) -> Self:
        return cls(
            id_auteur=AuthorId(parse_int(data["id_auteur"])),
            date=parse_date(data["date"]),
        )
