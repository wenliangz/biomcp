"""Getter module for retrieving article details."""

import json
from ssl import TLSVersion
from typing import Any

from pydantic import BaseModel, Field, computed_field

from src.utils import const, http_client, render
from src.utils.http_client import RequestError

PUBTATOR3_FULLTEXT = f"{const.PUBTATOR3_BASE}/publications/export/biocjson"
PUBTATOR3_FETCH = f"{const.PUBTATOR3_BASE}/fetch/"


class PassageInfo(BaseModel):
    """Model for passage metadata."""
    section_type: str | None = Field(
        None,
        description="Type of the section.",
    )
    passage_type: str | None = Field(
        None,
        alias="type",
        description="Type of the passage.",
    )


class Passage(BaseModel):
    """Model for article passage content."""
    info: PassageInfo | None = Field(
        None,
        alias="infons",
    )
    text: str | None = None

    @property
    def section_type(self) -> str:
        section_type = None
        if self.info is not None:
            section_type = self.info.section_type or self.info.passage_type
        section_type = section_type or "UNKNOWN"
        return section_type.upper()

    @property
    def is_title(self) -> bool:
        return self.section_type == "TITLE"

    @property
    def is_abstract(self) -> bool:
        return self.section_type == "ABSTRACT"

    @property
    def is_text(self) -> bool:
        return self.section_type in {
            "INTRO",
            "RESULTS",
            "METHODS",
            "DISCUSS",
            "CONCL",
            "FIG",
            "TABLE",
        }


class Article(BaseModel):
    """Model for article data."""
    pmid: int | None = Field(
        None,
        description="PubMed ID of the reference article.",
    )
    pmcid: str | None = Field(
        None,
        description="PubMed Central ID of the reference article.",
    )
    date: str | None = Field(
        None,
        description="Date of the reference article's publication.",
    )
    journal: str | None = Field(
        None,
        description="Journal name.",
    )
    authors: list[str] | None = Field(
        None,
        description="List of authors.",
    )
    passages: list[Passage] = Field(
        ...,
        alias="passages",
        description="List of passages in the reference article.",
        exclude=True,
    )

    @computed_field
    def title(self) -> str:
        lines = []
        for passage in filter(lambda p: p.is_title, self.passages):
            if passage.text:
                lines.append(passage.text)
        return " ... ".join(lines) or f"Article: {self.pmid}"

    @computed_field
    def abstract(self) -> str:
        lines = []
        for passage in filter(lambda p: p.is_abstract, self.passages):
            if passage.text:
                lines.append(passage.text)
        return "\n\n".join(lines) or f"Article: {self.pmid}"

    @computed_field
    def full_text(self) -> str:
        lines = []
        for passage in filter(lambda p: p.is_text, self.passages):
            if passage.text:
                lines.append(passage.text)
        return "\n\n".join(lines) or ""

    @computed_field
    def pubmed_url(self) -> str | None:
        url = None
        if self.pmid:
            url = f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
        return url

    @computed_field
    def pmc_url(self) -> str | None:
        """Generates the PMC URL if PMCID exists."""
        url = None
        if self.pmcid:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{self.pmcid}/"
        return url


class FetchArticlesResponse(BaseModel):
    """Response model for multiple articles."""
    articles: list[Article] = Field(
        ...,
        alias="PubTator3",
        description="List of full texts Articles retrieved from PubTator3.",
    )

    def get_abstract(self, pmid: int | None) -> str | None:
        for article in self.articles:
            if pmid and article.pmid == pmid:
                return str(article.abstract)
        return None


class ArticleResponse(BaseModel):
    """Response model for article data."""
    pmid: int = Field(..., description="PubMed ID")
    title: str = Field(..., description="Article title")
    abstract: str = Field(..., description="Article abstract")
    authors: list[str] = Field(..., description="List of authors")
    journal: str = Field(..., description="Journal name")
    date: str = Field(..., description="Publication date")
    doi: str = Field(..., description="DOI")
    pmcid: str = Field(..., description="PMC ID")


async def call_pubtator_api(
    pmids: list[int],
    full: bool = False,
) -> tuple[ArticleResponse | None, Any]:
    """Call the PubTator API to fetch article data."""
    response, error = await http_client.request_api(
        url=PUBTATOR3_FETCH,
        request={"pmids": pmids, "full": full},
        response_model_type=ArticleResponse,
    )

    return response, error


async def get_article(pmid: int, output_json: bool = False) -> str:
    """Get detailed information about a PubMed article."""
    response, error = await call_pubtator_api([pmid], full=True)

    if error:
        data = [{"error": f"Error {error.code}: {error.message}"}]
    else:
        data = [response.model_dump(mode="json", exclude_none=True)]

    if not output_json:
        return render.to_markdown(data)
    else:
        return json.dumps(data, indent=2) 