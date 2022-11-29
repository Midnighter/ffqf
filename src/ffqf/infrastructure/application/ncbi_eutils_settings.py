from pydantic import BaseSettings, HttpUrl, EmailStr


class NCBIEutilsSettings(BaseSettings):

    api_url: HttpUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    tool: str = "ffqf"
    email: EmailStr
    timeout: int = 10
    concurrency: int = 3  # 10 with API Key
