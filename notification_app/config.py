from __future__ import annotations

from dataclasses import dataclass

import yaml  # type: ignore

from kit.dbx.config import DBConfig


@dataclass
class Config:
    db: DBConfig
    telegram_token: str

    def __post_init__(self):
        if isinstance(self.db, dict):
            self.db = DBConfig(**self.db)


def read_config(path: str) -> Config:
    with open(path, "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)
