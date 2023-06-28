from typing import Optional
from enum import Enum

from pydantic import BaseModel, BaseSettings, validator, root_validator


class Environment(str, Enum):
    prod = "prod"
    dev = "dev"


class SQLConnectionModel(BaseModel):
    def make_database_url(self):
        return ""


class PSQLModel(SQLConnectionModel):
    host: str
    user: str
    password: str
    db: str
    port: int = 5432

    def make_database_url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    class Config:
        validate_assignment = True


class SQLiteModel(SQLConnectionModel):
    file_location: str

    def make_database_url(self):
        return f"sqlite+aiosqlite:///{self.file_location}"

    class Config:
        validate_assignment = True


class Settings(BaseSettings):
    app_env: Environment = Environment.dev
    psql: Optional[PSQLModel]
    sqlite: Optional[SQLiteModel]

    class Config:
        env_nested_delimiter = '__'
        validate_assignment = True

    @root_validator(skip_on_failure=True)
    def validate_db_settings(cls, values: dict):
        """
        Validate that only one db connection is provided
        """
        given_settings = list(filter(lambda v: isinstance(v, SQLConnectionModel), values.values()))
        settings_num = len(given_settings)
        if settings_num != 1:
            raise ValueError(f"There could be only one SQL setting ({settings_num} given)")
        return values

    def database_url(self):
        setting: SQLConnectionModel
        pairs = filter(lambda f: isinstance(f[1], SQLConnectionModel), self)
        for setting in map(lambda f: f[1], pairs):
            return setting.make_database_url()
        raise ValueError("No connection config found! Did you alter the settings?")


if __name__ == '__main__':
    settings = Settings()
    print(settings)
    print(settings.database_url())
