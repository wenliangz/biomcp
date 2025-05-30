"""MCP tools for protein structures."""

from mcp.server.fastmcp import Context
from pydantic import BaseModel
import pandas as pd

from src.utils.gene_mappings import get_gene_mappings


async def register_proteins_tools(mcp):
    """Register protein structure-related MCP tools."""

    class Alphafold(BaseModel):
        uniprot_accession: str
        url: str

    @mcp.tool()
    async def get_protein_structure(ctx: Context, query: str) -> Alphafold | None:
        """
        The endpoint takes a gene name and returns the alphafold structure url.
        This function should be used when the user asks for a structure of a gene or a protein.
        """
        gm = await get_gene_mappings(query, raise_if_empty=True)
        uniprot_accession = gm[0].uniprot_accession
        url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_accession}"
        df = pd.read_json(url)
        if df.empty:
            return None
        return Alphafold(
            uniprot_accession=uniprot_accession,
            url=df.loc[0, "pdbUrl"],
        )
