from typing import Any, Literal, Mapping, NewType, TypeAlias, TypeVar

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
