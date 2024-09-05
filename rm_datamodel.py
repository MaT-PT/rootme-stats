from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal, NewType, Self, TypeAlias, TypedDict

AuthorId = NewType("AuthorId", int)
ChallengeId = NewType("ChallengeId", int)
SolutionId = NewType("SolutionId", int)
CategoryId = NewType("CategoryId", int)
RelativeUrl = NewType("RelativeUrl", str)
RelativeLocalizedUrl = NewType("RelativeLocalizedUrl", str)

BoolStr: TypeAlias = Literal["true", "false"]
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

ACCOUNT_TYPE_COLORS: dict[AccountTypeCode, str] = {
    "0minirezo": "#767676",
    "5pre": "#DE2B0F",
    "1comite": "#DE770F",
    "6forum": "#00CC00",
}


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


@dataclass
class Author:
    class AuthorDict(TypedDict):
        id_auteur: str
        nom: str
        statut: AccountTypeCode
        logo_url: str
        score: str
        position: int | Literal[""]
        rang: RankCode
        membre: BoolStr
        challenges: list[Challenge.ChallengeDict]
        solutions: list[Solution.SolutionDict]
        validations: list[Validation.ValidationDict]

    id_auteur: AuthorId
    nom: str
    statut: AccountType
    logo_url: RelativeUrl
    score: int
    position: int | None
    rang: Rank
    membre: bool
    challenges: list[Challenge]
    solutions: list[Solution]
    validations: list[Validation]

    @classmethod
    def from_dict(cls, data: AuthorDict) -> Self:
        return cls(
            id_auteur=AuthorId(int(data["id_auteur"])),
            nom=data["nom"],
            statut=AccountType(data["statut"]),
            logo_url=RelativeUrl(data["logo_url"]),
            score=int(data["score"]),
            position=data["position"] or None,
            rang=Rank(data["rang"]),
            membre=data["membre"] == "true",
            challenges=[Challenge.from_dict(challenge) for challenge in data["challenges"]],
            solutions=[Solution.from_dict(solution) for solution in data["solutions"]],
            validations=[Validation.from_dict(validation) for validation in data["validations"]],
        )


@dataclass
class Challenge:
    class ChallengeDict(TypedDict):
        id_challenge: str
        titre: str
        url_challenge: str

    id_challenge: ChallengeId
    titre: str
    url_challenge: RelativeLocalizedUrl

    @classmethod
    def from_dict(cls, data: ChallengeDict) -> Self:
        return cls(
            id_challenge=ChallengeId(int(data["id_challenge"])),
            titre=data["titre"],
            url_challenge=RelativeLocalizedUrl(data["url_challenge"]),
        )


@dataclass
class Solution:
    class SolutionDict(TypedDict):
        id_solution: str
        url_solution: str

    id_solution: SolutionId
    url_solution: RelativeLocalizedUrl

    @classmethod
    def from_dict(cls, data: SolutionDict) -> Self:
        return cls(
            id_solution=SolutionId(int(data["id_solution"])),
            url_solution=RelativeLocalizedUrl(data["url_solution"]),
        )


@dataclass
class Validation:
    class ValidationDict(TypedDict):
        id_challenge: str
        titre: str
        id_rubrique: str
        date: str

    id_challenge: ChallengeId
    titre: str
    id_rubrique: CategoryId
    date: datetime

    @classmethod
    def from_dict(cls, data: ValidationDict) -> Self:
        return cls(
            id_challenge=ChallengeId(int(data["id_challenge"])),
            titre=data["titre"],
            id_rubrique=CategoryId(int(data["id_rubrique"])),
            date=datetime.fromisoformat(data["date"]),
        )
