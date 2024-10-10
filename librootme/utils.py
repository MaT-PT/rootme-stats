from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import SplitResult, parse_qs, parse_qsl, urljoin, urlsplit

from .types import BoolStr, DateStr, IntStr, RelativeUrl, Url


class _MLStripper(HTMLParser):
    fed: list[str]

    def __init__(self) -> None:
        super().__init__()
        self.fed = []

    def handle_data(self, data: str) -> None:
        self.fed.append(data)

    def get_data(self) -> str:
        return "".join(self.fed)


def strip_tags(html: str) -> str:
    s = _MLStripper()
    s.feed(html)
    return s.get_data()


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
