from __future__ import annotations

from dataclasses import dataclass

import yaml  # type: ignore

from kit.dbx import DBConfig
from kit.mqx import RabbitMQConfig


@dataclass
class Config:
    db: DBConfig
    telegram_token: str
    camera_sources: list[int | str]
    model_path: str
    org_id: str
    message_queue: RabbitMQConfig

    def __post_init__(self):
        if isinstance(self.db, dict):
            self.db = DBConfig(**self.db)
        if isinstance(self.message_queue, dict):
            self.message_queue = RabbitMQConfig(**self.message_queue)


def read_config(path: str) -> Config:
    with open(path, "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)
