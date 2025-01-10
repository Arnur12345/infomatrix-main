from dataclasses import dataclass


@dataclass
class DBConfig:
    host: str
    username: str
    password: str
    database: str
    port: int = 5432

    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    def async_connection_string(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
