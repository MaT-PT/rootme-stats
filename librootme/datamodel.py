from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from typing import Generic, Literal, NotRequired, Self, TypedDict, cast, final

from .constants import (
    AccountType,
    AccountTypeCode,
    CategoryLocalized,
    Difficulty,
    Language,
    LanguageCode,
    Rank,
    RankCode,
    RelType,
)
from .types import (
    _T,
    _TD,
    AuthorId,
    BoolStr,
    ChallengeId,
    ChallengeIndex,
    DateStr,
    DictList,
    DifficultyStr,
    IntStr,
    PrettyPrintable,
    RelativeLocalizedUrl,
    RelativeUrl,
    SolutionId,
    Url,
)
from .utils import bool_yn, get_absolute_url, indent, parse_bool, parse_date, parse_int


class RelDict(TypedDict):
    rel: RelType
    href: Url


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

    @final
    def as_type(self, target_type: type[_T]) -> _T:
        if isinstance(self, target_type):
            return cast(_T, self)
        raise TypeError(f"Cannot convert {type(self)} to {target_type}")


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
class Author(TypedDictDataclass[AuthorDict], PrettyPrintable):
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
            + indent((str(validation) for validation in self.validations), 4)
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
class Challenge(TypedDictDataclass[ChallengeDict], PrettyPrintable):
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
    difficulte: Difficulty
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
            difficulte=Difficulty.from_str(data["difficulte"]),
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
            f"| Updated: {self.maj}"
        )

    def pretty(self, lang: Language = Language.EN) -> str:
        cat_str = self.rubrique
        cat_localized = self.id_rubrique.category.get_name(lang)
        if cat_str != cat_localized:
            cat_str += f" [{cat_localized}]"
        return (
            f"{self.titre} ({cat_str}) | Id: {self.index_challenge} ({self.id_trad})\n"
            f"> {self.soustitre}\n"
            f"  Score: {self.score} [{self.difficulte.localized_name(lang)}] "
            f"| Created: {self.date_publication} "
            f"| Updated: {self.maj}\n"
            f"  Authors: {', '.join(str(author) for author in self.auteurs)}"
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
