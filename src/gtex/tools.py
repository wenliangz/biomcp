from __future__ import annotations

import requests

from mcp.server.fastmcp import Context
from src.utils.gene_mappings import get_gene_mappings
from src import WedaitaBaseModel, ToolError


class GtexExpression(WedaitaBaseModel):
    data: list[float]
    datasetId: str
    gencodeId: str
    geneSymbol: str
    ontologyId: str
    subsetGroup: str | None = None
    tissueSiteDetailId: str
    unit: str


async def register_gtex_tools(mcp):
    """
    Register gtex-related MCP tools.
    """
    @mcp.tool()
    async def gtex_gene_expression(
        query: str
        ) -> list[GtexExpression]:
        """
        The endpoint takes a gene name and the expression of that gene in bulk rna seq expression from the GTEX portal.
        The GTEX samples are all normal samples.

        Args:
            query: The gene name to query GTEX for expression data.
        """
        gm = await get_gene_mappings(query, raise_if_empty=True)
        ensembl = gm[0].ensembl_gene
        ensembl_versioned = _get_versioned_ensembl_for_gtex(ensembl)

        url = (
            f"https://gtexportal.org/api/v2/expression/geneExpression?gencodeId={ensembl_versioned}&page=0&itemsPerPage=250"
        )
        response = requests.get(url)
        if response.status_code != 200:
            return []
        data = response.json().get("data")
        if not data:
            return []
        return list(map(GtexExpression.model_validate, data))


    def _get_versioned_ensembl_for_gtex(ensembl: str):
        url = f"https://gtexportal.org/api/v2/reference/geneSearch?geneId={ensembl}&page=0&itemsPerPage=1"
        response = requests.get(url)
        if response.status_code == 200:
            j = response.json()
            return j.get("data")[0]["gencodeId"]
        else:
            return None
