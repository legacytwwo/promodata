from json import load
from typing import Type
from random import randint
from dataclasses import dataclass

@dataclass
class Restart:
    restart_count: int
    interval_m: float

    @classmethod
    def from_dict(cls: Type["Restart"], obj: dict):
        return cls(
            restart_count=obj["restart_count"],
            interval_m=obj["interval_m"],
        )

@dataclass
class Config:
    output_directory: str
    categories: list[str]
    delay_range_s: int
    max_retries: int
    headers: dict[str: str]
    logs_dir: str
    restart: Restart

    @classmethod
    def from_dict(cls: Type["Config"], obj: dict):
        return cls(
            output_directory=obj["output_directory"],
            categories=obj["categories"],
            delay_range_s=randint(obj["delay_range_s"]["min"], obj["delay_range_s"]["max"]),
            max_retries=obj["max_retries"],
            headers=obj["headers"],
            logs_dir=obj["logs_dir"],
            restart=Restart.from_dict(obj["restart"]),
        )

def get_config() -> Config:
    config = load(open('config.json'))
    return Config.from_dict(config)