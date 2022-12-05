from pydantic import BaseSettings, HttpUrl


class APISettings(BaseSettings):

    api_url: HttpUrl
    concurrency: int
    timeout: int = 30
