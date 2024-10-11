from __future__ import annotations

from abc import ABC
from typing import Any, Generic, Iterable, Iterator, Self, Sequence, overload
from urllib.parse import SplitResult

from .constants import Rel, RelType
from .datamodel import RelDict, TypedDictDataclass
from .types import _T, _TD, DictList, PrettyPrintable, Url, _T_co
from .utils import parse_url_qsl, split_url


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


class PagedItem(PagedData[_T_co], PrettyPrintable):
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

    def pretty(self, *args: Any, **kwargs: Any) -> str:
        if isinstance(self._data, PrettyPrintable):
            return self._data.pretty(*args, **kwargs)
        return str(self)


class PagedList(PagedData[Sequence[_T_co]], Sequence[_T_co], PrettyPrintable):
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

    def pretty(self, *args: Any, **kwargs: Any) -> str:
        return "\n".join(
            (item.pretty(*args, **kwargs) if isinstance(item, PrettyPrintable) else str(item))
            for item in self._data
        )
