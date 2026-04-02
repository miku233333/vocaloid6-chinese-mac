#!/usr/bin/env python3
"""
Helpers for keeping product-specific localization data out of the public repo.
"""

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def private_data_dir() -> Path:
    override = os.environ.get("VOCALOID6_PRIVATE_DATA_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".vocaloid6-chinese-mac-private"


def private_glossary_path(name: str) -> Path:
    return private_data_dir() / "glossaries" / name


def private_translation_path(language: str) -> Path:
    return private_data_dir() / "translations" / f"{language}.json"
