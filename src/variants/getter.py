"""Getter module for retrieving variant details."""

import json
from typing import Any

from pydantic import BaseModel, Field

from src.utils import const, http_client, render
from src.utils.http_client import RequestError

MYVARIANT_QUERY_ENDPOINT = f"{const.MYVARIANT_BASE_URL}/variant"


class VariantResponse(BaseModel):
    """Response model for variant data."""

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


async def get_variant(variant_id: str, output_json: bool = False) -> str:
    """Get detailed information about a genetic variant."""
    response, error = await http_client.request_api(
        url=f"{MYVARIANT_QUERY_ENDPOINT}/{variant_id}",
        response_model_type=VariantResponse,
    )

    if error:
        data = [{"error": f"Error {error.code}: {error.message}"}]
    else:
        data = [response.model_dump(mode="json", exclude_none=True)]

    if not output_json:
        return render.to_markdown(data)
    else:
        return json.dumps(data, indent=2)
