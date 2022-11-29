from pydantic import BaseSettings, HttpUrl


class ENAAPIPortalSettings(BaseSettings):

    api_url: HttpUrl = "https://www.ebi.ac.uk/ena/portal/api/"
    timeout: int = 10
    concurrency: int = 10
