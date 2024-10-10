from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum
from html import unescape
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
from urllib.parse import SplitResult, parse_qs, parse_qsl, urljoin, urlsplit

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)
_TD = TypeVar("_TD", bound=Mapping[str, Any])
_TD_co = TypeVar("_TD_co", bound=Mapping[str, Any], covariant=True)
_TD_contra = TypeVar("_TD_contra", bound=Mapping[str, Any], contravariant=True)

AuthorId = NewType("AuthorId", int)
ChallengeId = NewType("ChallengeId", int)
SolutionId = NewType("SolutionId", int)
ChallengeIndex = NewType("ChallengeIndex", str)
DifficultyStr = NewType("DifficultyStr", str)
Url = NewType("Url", str)
RelativeUrl = NewType("RelativeUrl", str)
RelativeLocalizedUrl = NewType("RelativeLocalizedUrl", RelativeUrl)
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


def bool_yn(value: bool) -> str:
    return "yes" if value else "no"


def indent(text: str | Iterable[str], spaces: int = 2, add_newline: bool = False) -> str:
    if isinstance(text, str):
        text = text.splitlines()
    indented = "\n".join(" " * spaces + line for line in text)
    if add_newline and len(indented) > 0:
        indented += "\n"
    return indented


def get_absolute_url(rel_url: RelativeUrl, base_url: Url | str = "https://www.root-me.org/") -> Url:
    return Url(urljoin(base_url, rel_url))


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


class Category(IntEnum):
    WEB_CLIENT = 16
    PROGRAMMING = 17
    CRYPTANALYSIS = 18
    STEGANOGRAPHY = 67
    WEB_SERVER = 68
    CRACKING = 69
    REALIST = 70
    NETWORK = 182
    APP_SCRIPT = 189
    APP_SYSTEM = 203
    FORENSIC = 208

    def get_name(self, lang: Language = Language.EN) -> str:
        return CATEGORY_NAMES[lang][self]


class CategoryLocalized(IntEnum):
    FR_APP_SCRIPT = 189
    FR_APP_SYSTEM = 203
    FR_CRACKING = 69
    FR_CRYPTANALYSIS = 18
    FR_FORENSIC = 208
    FR_PROGRAMMING = 17
    FR_REALIST = 70
    FR_NETWORK = 182
    FR_STEGANOGRAPHY = 67
    FR_WEB_CLIENT = 16
    FR_WEB_SERVER = 68

    EN_APP_SCRIPT = 191
    EN_APP_SYSTEM = 204
    EN_CRACKING = 158
    EN_CRYPTANALYSIS = 160
    EN_FORENSIC = 209
    EN_PROGRAMMING = 159
    EN_REALIST = 157
    EN_NETWORK = 183
    EN_STEGANOGRAPHY = 156
    EN_WEB_CLIENT = 155
    EN_WEB_SERVER = 154

    DE_APP_SCRIPT = 217
    DE_APP_SYSTEM = 218
    DE_CRACKING = 228
    DE_CRYPTANALYSIS = 229
    DE_FORENSIC = 230
    DE_PROGRAMMING = 231
    DE_REALIST = 235
    DE_NETWORK = 232
    DE_STEGANOGRAPHY = 236
    DE_WEB_CLIENT = 234
    DE_WEB_SERVER = 233

    ES_APP_SCRIPT = 251
    ES_APP_SYSTEM = 252
    ES_CRACKING = 253
    ES_CRYPTANALYSIS = 254
    ES_FORENSIC = 255
    ES_PROGRAMMING = 256
    ES_REALIST = 257
    ES_NETWORK = 258
    ES_STEGANOGRAPHY = 259
    ES_WEB_CLIENT = 260
    ES_WEB_SERVER = 261

    RU_APP_SCRIPT = 327
    RU_APP_SYSTEM = 329
    RU_CRACKING = 323
    RU_CRYPTANALYSIS = 325
    RU_FORENSIC = 330
    RU_PROGRAMMING = 324
    RU_REALIST = 322
    RU_NETWORK = 326
    RU_STEGANOGRAPHY = 321
    RU_WEB_CLIENT = 320
    RU_WEB_SERVER = 319

    ZH_APP_SCRIPT = 371
    ZH_APP_SYSTEM = 376
    ZH_CRACKING = 359
    ZH_CRYPTANALYSIS = 361
    ZH_FORENSIC = 377
    ZH_PROGRAMMING = 360
    ZH_REALIST = 358
    ZH_NETWORK = 370
    ZH_STEGANOGRAPHY = 357
    ZH_WEB_CLIENT = 356
    ZH_WEB_SERVER = 355

    @property
    def lang(self) -> Language:
        return Language[self.name.split("_", 1)[0]]

    @property
    def category(self) -> Category:
        return Category[self.name.split("_", 1)[1]]

    def __str__(self) -> str:
        return self.category.get_name(self.lang)


CATEGORY_NAMES: dict[Language, dict[Category, str]] = {
    Language.FR: {
        Category.WEB_CLIENT: "Web - Client",
        Category.PROGRAMMING: "Programmation",
        Category.CRYPTANALYSIS: "Cryptanalyse",
        Category.STEGANOGRAPHY: "Stéganographie",
        Category.WEB_SERVER: "Web - Serveur",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Réaliste",
        Category.NETWORK: "Réseau",
        Category.APP_SCRIPT: "App - Script",
        Category.APP_SYSTEM: "App - Système",
        Category.FORENSIC: "Forensic",
    },
    Language.EN: {
        Category.WEB_CLIENT: "Web - Client",
        Category.PROGRAMMING: "Programming",
        Category.CRYPTANALYSIS: "Cryptanalysis",
        Category.STEGANOGRAPHY: "Steganography",
        Category.WEB_SERVER: "Web - Server",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Realist",
        Category.NETWORK: "Network",
        Category.APP_SCRIPT: "App - Script",
        Category.APP_SYSTEM: "App - System",
        Category.FORENSIC: "Forensic",
    },
    Language.DE: {
        Category.WEB_CLIENT: "Web - Kunde",
        Category.PROGRAMMING: "Programmierung",
        Category.CRYPTANALYSIS: "Kryptoanalyse",
        Category.STEGANOGRAPHY: "Steganografie",
        Category.WEB_SERVER: "Web - Server",
        Category.CRACKING: "Knacken",
        Category.REALIST: "Realist",
        Category.NETWORK: "Netzwerk",
        Category.APP_SCRIPT: "App - Skript",
        Category.APP_SYSTEM: "Anwendung - System",
        Category.FORENSIC: "Forensische",
    },
    Language.ES: {
        Category.WEB_CLIENT: "Web - Cliente",
        Category.PROGRAMMING: "Programación",
        Category.CRYPTANALYSIS: "Criptoanálisis",
        Category.STEGANOGRAPHY: "Esteganografía",
        Category.WEB_SERVER: "Web - Servidor",
        Category.CRACKING: "Cracking",
        Category.REALIST: "Realista",
        Category.NETWORK: "Red",
        Category.APP_SCRIPT: "Aplicación - Guión",
        Category.APP_SYSTEM: "Aplicación - Sistema",
        Category.FORENSIC: "Forense",
    },
    Language.RU: {
        Category.WEB_CLIENT: "Веб - Клиент",
        Category.PROGRAMMING: "Программирование",
        Category.CRYPTANALYSIS: "Криптоанализ",
        Category.STEGANOGRAPHY: "Стеганография",
        Category.WEB_SERVER: "Веб - сервер",
        Category.CRACKING: "Взлом",
        Category.REALIST: "Реалист",
        Category.NETWORK: "Сеть",
        Category.APP_SCRIPT: "App - Сценарий",
        Category.APP_SYSTEM: "Приложение - Система",
        Category.FORENSIC: "Судебная экспертиза",
    },
    Language.ZH: {
        Category.WEB_CLIENT: "网络 - 客户端",
        Category.PROGRAMMING: "编程",
        Category.CRYPTANALYSIS: "密码分析",
        Category.STEGANOGRAPHY: "隐写术",
        Category.WEB_SERVER: "网络 - 服务器",
        Category.CRACKING: "裂缝",
        Category.REALIST: "现实主义者",
        Category.NETWORK: "网络",
        Category.APP_SCRIPT: "应用程序 - 脚本",
        Category.APP_SYSTEM: "应用程序 - 系统",
        Category.FORENSIC: "法医",
    },
}


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

    def get_rel_start(self, rel: RelType | Rel) -> int | None:
        url = self.rel(rel)
        if url is None:
            return None
        query = parse_url_qsl(url)
        start_values = [int(v) for k, v in query if k.startswith("debut_")]
        if len(start_values) == 0:
            return 0
        if len(start_values) > 1:
            raise ValueError(f"Multiple start values found in {rel} URL query: {url}")
        return start_values[0]

    @property
    def prev_start(self) -> int | None:
        return self.get_rel_start(Rel.PREV)

    @property
    def next_start(self) -> int | None:
        return self.get_rel_start(Rel.NEXT)


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

    def __str__(self) -> str:
        return str(self._data)


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

    def __str__(self) -> str:
        return "\n".join(str(item) for item in self._data)


class TypedDictDataclass(ABC, Generic[_TD]):
    # _base_typed_dict: ClassVar[type[Mapping[str, Any]]]  # ClassVar[type[_TD]] not supported

    @classmethod
    @abstractmethod
    def from_dict(cls, data: _TD) -> Self: ...

    @classmethod
    def from_dictlist(cls, dictlist: DictList[_TD]) -> list[Self]:
        return [cls.from_dict(val) for val in dictlist.values()]

    @abstractmethod
    def __str__(self) -> str: ...


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

    def __str__(self) -> str:
        return f"{self.nom} ({self.id_auteur})"


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

    def __str__(self) -> str:
        return (
            f"{self.id_auteur}: {self.nom} ({self.statut}) "
            f"| Score: {self.score} [{self.rang or 'No rank'}] "
            f"| Position: {self.position} "
            f"| Member: {self.membre} "
            f"| Challenges: {len(self.challenges)} "
            f"| Solutions: {len(self.solutions)} "
            f"| Validations: {len(self.validations)}"
        )

    def pretty(self) -> str:
        return (
            f"{self.nom} - Id: {self.id_auteur} ({self.statut}, member: {bool_yn(self.membre)})\n"
            f"  Score: {self.score} [{self.rang or 'No rank'}] | Position: {self.position}\n"
            f"  Profile picture: https://www.root-me.org/{self.logo_url}\n"
            f"  Challenges: {len(self.challenges)}\n"
            + indent((str(challenge) for challenge in self.challenges), 4, True)
            + f"  Solutions: {len(self.solutions)}\n"
            + indent((str(solution) for solution in self.solutions), 4, True)
            + f"  Validations: {len(self.validations)}\n"
            + indent((str(validation) for validation in self.validations), 4, True)
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
            titre=unescape(data["titre"]),
            url_challenge=RelativeLocalizedUrl(RelativeUrl(data["url_challenge"])),
        )

    def __str__(self) -> str:
        return f"{self.id_challenge}: {self.titre} ({get_absolute_url(self.url_challenge)})"


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
    id_rubrique: CategoryLocalized
    titre: str
    lang: Language
    date_publication: datetime
    maj: datetime

    @classmethod
    def from_dict(cls, data: ChallengeShortDict) -> Self:
        return cls(
            id_challenge=ChallengeId(parse_int(data["id_challenge"])),
            id_rubrique=CategoryLocalized(parse_int(data["id_rubrique"])),
            titre=unescape(data["titre"]),
            lang=Language(data["lang"]),
            date_publication=parse_date(data["date_publication"]),
            maj=parse_date(data["maj"]),
        )

    def __str__(self) -> str:
        return (
            f"{self.id_challenge}: {self.titre} ({self.lang.name}) [{self.id_rubrique}] "
            f"| Created: {self.date_publication} "
            f"| Updated: {self.maj}"
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
    id_rubrique: CategoryLocalized
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
            titre=unescape(data["titre"]),
            rubrique=data["rubrique"],
            soustitre=unescape(data["soustitre"]),
            score=parse_int(data["score"]),
            index_challenge=ChallengeIndex(data["index_challenge"]),
            id_rubrique=CategoryLocalized(parse_int(data["id_rubrique"])),
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

    def __str__(self) -> str:
        return (
            f"{self.index_challenge} ({self.id_trad}): {self.titre} ({self.rubrique}) "
            f"| {self.soustitre} "
            f"| Authors: {', '.join(str(author) for author in self.auteurs)} "
            f"| Score: {self.score} [{self.difficulte}] "
            f"| Created: {self.date_publication} "
            f"| Updated: {self.maj} "
        )

    def pretty(self) -> str:
        return (
            f"{self.titre} ({self.rubrique}) | Id: {self.index_challenge} ({self.id_trad})\n"
            f"> {self.soustitre}\n"
            f"  Score: {self.score} [{self.difficulte}] "
            f"| Created: {self.date_publication} "
            f"| Updated: {self.maj}\n"
            f"  Authors: {', '.join(str(author) for author in self.auteurs)}\n"
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
            url_solution=RelativeLocalizedUrl(RelativeUrl(data["url_solution"])),
        )

    def __str__(self) -> str:
        return f"{self.id_solution}: {get_absolute_url(self.url_solution)}"


class ValidationAuthorDict(TypedDict):
    id_challenge: IntStr
    titre: str
    id_rubrique: IntStr
    date: DateStr


@dataclass
class ValidationAuthor(TypedDictDataclass[ValidationAuthorDict]):
    id_challenge: ChallengeId
    titre: str
    id_rubrique: CategoryLocalized
    date: datetime

    @classmethod
    def from_dict(cls, data: ValidationAuthorDict) -> Self:
        return cls(
            id_challenge=ChallengeId(parse_int(data["id_challenge"])),
            titre=unescape(data["titre"]),
            id_rubrique=CategoryLocalized(parse_int(data["id_rubrique"])),
            date=parse_date(data["date"]),
        )

    def __str__(self) -> str:
        return f"{self.id_challenge}: {self.titre} [{self.id_rubrique}] | {self.date}"


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

    def __str__(self) -> str:
        return f"{self.id_auteur} | {self.date}"
