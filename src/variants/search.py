"""Search functionality for genetic variants."""

import json
from typing import Any, List

from pydantic import BaseModel, Field, RootModel

from src.utils import const, http_client, render
from src.utils.http_client import RequestError

MYVARIANT_SEARCH_ENDPOINT = f"{const.MYVARIANT_BASE_URL}/query"


class VariantQuery(BaseModel):
    """Search parameters for querying genetic variants."""
    gene: str = Field(..., description="Gene name to search for")
    size: int = Field(default=10, description="Number of results to return")


class VariantSearchResponse(BaseModel):
    """Response model for variant search results."""
    id: str = Field(..., alias="_id", description="Variant ID")
    chrom: str = Field(..., description="Chromosome")
    position: int = Field(..., description="Position")
    ref: str = Field(..., description="Reference allele")
    alt: str = Field(..., description="Alternate allele")
    cadd: dict[str, Any] = Field(..., description="CADD scores")
    clinvar: dict[str, Any] = Field(..., description="ClinVar annotations")
    cosmic: dict[str, Any] = Field(..., description="COSMIC annotations")
    dbsnp: dict[str, Any] = Field(..., description="dbSNP annotations")
    exac: dict[str, Any] = Field(..., description="ExAC annotations")
    gnomad_exome: dict[str, Any] = Field(..., description="gnomAD exome annotations")
    snpeff: dict[str, Any] = Field(..., description="SnpEff annotations")


class VariantSearchResponseList(RootModel[List[VariantSearchResponse]]):
    pass


class MyVariantAPIResponse(BaseModel):
    hits: List[VariantSearchResponse]
    # You can add other fields (e.g., 'took', 'total') if needed


async def search_variants(
    query: VariantQuery,
    output_json: bool = False,
) -> str:
    """Search for genetic variants based on specified criteria."""
    response, error = await http_client.request_api(
        url=MYVARIANT_SEARCH_ENDPOINT,
        request={
            "q": f"gene:{query.gene}",
            "size": query.size,
            "fields": "chrom,position,ref,alt,cadd,clinvar,cosmic,dbsnp,exac,gnomad_exome,snpeff"
        },
        response_model_type=MyVariantAPIResponse,
    )

    if error:
        data = [{"error": f"Error {error.code}: {error.message}"}]
    else:
        data = [variant.model_dump(mode="json", exclude_none=True) for variant in response.hits]

    if not output_json:
        return render.to_markdown(data)
    else:
        return json.dumps(data, indent=2)
