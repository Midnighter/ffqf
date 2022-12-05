from pydantic import EmailStr, HttpUrl

from ffqf.application.service import APISettings


class NCBIEutilsSettings(APISettings):

    email: EmailStr
    api_url: HttpUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    tool: str = "ffqf"
    concurrency: int = 3  # 10 with API Key
