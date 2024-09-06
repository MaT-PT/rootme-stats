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

# TODO: Create data model for requests and other responses

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)
_TD = TypeVar("_TD", bound=Mapping[str, Any])
_TD_co = TypeVar("_TD_co", bound=Mapping[str, Any])
_TD_contra = TypeVar("_TD_contra", bound=Mapping[str, Any])

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


class Rel(TypedDict):
    rel: RelType
    href: Url


PagedResults: TypeAlias = tuple[DictList[_TD], *tuple[Rel, ...]]
# PagedData: TypeAlias = tuple[list[_T], *tuple[Rel, ...]]


class PagedItem(Generic[_T]):
    _item: _T
    _rels: dict[RelType, Url]

    def __init__(self, item: _T, rels: dict[RelType, Url] | None = None) -> None:
        self._item = item
        self._rels = rels or {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._item!r}, {self._rels!r})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PagedItem):
            return NotImplemented
        return self._item == other._item and self._rels == other._rels

    @classmethod
    def from_rawrels(cls, item: _T, *rels: Rel) -> PagedItem[_T]:
        return cls(item, {rel["rel"]: rel["href"] for rel in rels})

    @staticmethod
    def from_pagedresult(
        result: tuple[_TD, *tuple[Rel, ...]],
        target_type: type[TypedDictDataclass[_TD]],
    ) -> PagedItem[TypedDictDataclass[_TD]]:
        return PagedItem[TypedDictDataclass[_TD]].from_rawrels(
            target_type.from_dict(result[0]), *result[1:]
        )

    @property
    def item(self) -> _T:
        return self._item

    @property
    def rels(self) -> dict[RelType, Url]:
        return self._rels

    @property
    def prev(self) -> Url | None:
        return self._rels.get("previous")

    @property
    def next(self) -> Url | None:
        return self._rels.get("next")


class PagedList(Sequence[_T_co]):
    _list: list[_T_co]
    _rels: dict[RelType, Url]

    def __init__(self, data: Iterable[_T_co], rels: dict[RelType, Url] | None = None) -> None:
        self._list = list(data)
        self._rels = rels or {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._list!r}, {self._rels!r})"

    def __iter__(self) -> Iterator[_T_co]:
        return iter(self._list)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PagedList):
            return NotImplemented
        return self._list == other._list and self._rels == other._rels

    @overload
    def __getitem__(self, index: int) -> _T_co: ...
    @overload
    def __getitem__(self, index: slice) -> PagedList[_T_co]: ...
    def __getitem__(self, index: int | slice) -> _T_co | PagedList[_T_co]:
        if isinstance(index, slice):
            return PagedList(self._list[index], self._rels)
        return self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def __contains__(self, value: Any) -> bool:
        return value in self._list

    def __reversed__(self) -> Iterator[_T_co]:
        return reversed(self._list)

    @classmethod
    def from_rawrels(cls, data: Iterable[_T_co], *rels: Rel) -> PagedList[_T_co]:
        return cls(data, {rel["rel"]: rel["href"] for rel in rels})

    @staticmethod
    def from_pagedresults(
        # results: PagedResults[_TD], target_type: type[_TDD_contra]
        results: tuple[DictList[_TD], *tuple[Rel, ...]],
        target_type: type[TypedDictDataclass[_TD]],
    ) -> PagedList[TypedDictDataclass[_TD]]:
        return PagedList[TypedDictDataclass[_TD]].from_rawrels(
            target_type.from_dictlist(results[0]), *results[1:]
        )

    @property
    def rels(self) -> dict[RelType, Url]:
        return self._rels

    @property
    def prev(self) -> Url | None:
        return self._rels.get("previous")

    @property
    def next(self) -> Url | None:
        return self._rels.get("next")


class TypedDictDataclass(ABC, Generic[_TD]):
    @classmethod
    @abstractmethod
    def from_dict(cls, data: _TD) -> Self: ...

    @classmethod
    def from_dictlist(cls, dictlist: DictList[_TD]) -> list[Self]:
        print("dictlist:", dictlist)
        return [cls.from_dict(val) for val in dictlist.values()]


_TDD_contra = TypeVar("_TDD_contra", bound=TypedDictDataclass[Any], contravariant=True)


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
        print(data)
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
