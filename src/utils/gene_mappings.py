from __future__ import annotations

from biothings_client import get_client

from pydantic import BaseModel
from src import WedaitaBaseModel, ToolError




class GeneMapping(WedaitaBaseModel):
    entrezgene: int
    uniprot_accession: str
    name: str
    symbol: str
    ensembl_gene: str



async def get_gene_mappings(query: str, *, raise_if_empty: bool = False) -> list[GeneMapping]:
    """
    The endpoint takes a gene name and returns the gene mappings for entrez, hgnc, ensembl, uniprot.
    """
    mg = get_client("gene")

    df = mg.query(
        query,
        as_dataframe=True,
        species=9606,
        fields="name,entrezgene,symbol,uniprot.Swiss-Prot,ensembl.gene",
    )
    df = df.dropna(subset=["symbol", "entrezgene", "uniprot.Swiss-Prot", "ensembl.gene"])
    df = df.rename(
        columns={
            "uniprot.Swiss-Prot": "uniprot_accession",
            "ensembl.gene": "ensembl_gene",
        }
    )
    m = list(map(GeneMapping.model_validate, df.to_dict(orient="records")))
    if raise_if_empty and not m:
        raise ToolError("Gene not found")
    return m
