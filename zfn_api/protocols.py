from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Protocol

import requests


class ClientProtocol(Protocol):
    """Protocol describing attributes shared by mixins."""

    base_url: str
    sess: requests.Session
    headers: Mapping[str, str]
    cookies: MutableMapping[str, str]
    timeout: float
    raspisanie: list[list[str]]
    ignore_type: list[str]
    detail_category_type: list[str]
    login_url: str
    key_url: str
    kaptcha_url: str

    @staticmethod
    def parse_int(digits: str | None) -> int | str | None: ...
    @staticmethod
    def align_floats(floats: str | None) -> str | None: ...
    @staticmethod
    def get_place(place: str) -> str: ...
    @staticmethod
    def get_course_time(time: str) -> str: ...
    @staticmethod
    def encrypt_password(pwd: str, n: str, e: str) -> Any: ...
    @classmethod
    def get_display_term(cls, sid: str, year: str, term: str) -> str | None: ...
    def get_course_category(self, type: str, item: dict[str, Any]) -> str | None: ...
    @staticmethod
    def is_number(s: str) -> bool: ...
