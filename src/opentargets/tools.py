from __future__ import annotations

import numpy as np
import pandas as pd
import requests
import logging
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

from src.utils.gene_mappings import get_gene_mappings
from src import WedaitaBaseModel, ToolError

__all__ = ["register_opentargets_tools"]

logger = logging.getLogger(__name__)

# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=0.5,  # wait 0.5, 1, 2 seconds between retries
    status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

class OTDiseaseAssociation(WedaitaBaseModel):
    disease_id: str
    disease_name: str
    chembl_score: float | None = None
    crispr_screen_score: float | None = None
    europepmc_score: float | None = None
    eva_score: float | None = None
    expression_atlas_score: float | None = None
    ot_genetics_portal_score: float | None = None
    slapenrich_score: float | None = None

class OTTargetAssociation(WedaitaBaseModel):
    symbol: str
    score: float
    affected_pathway_score: float | None = None
    animal_model_score: float | None = None
    genetic_association_score: float | None = None
    known_drug_score: float | None = None
    literature_score: float | None = None
    somatic_mutation_score: float | None = None
    rna_expression_score: float | None = None

async def register_opentargets_tools(mcp):
    """
    Register OpenTargets-related MCP tools.
    """

    @mcp.tool()
    async def query_diseases_for_gene(query: str) -> list[OTDiseaseAssociation]:
        """
        The endpoint takes a gene name, converts it to the ensembl gene, and returns the associated
        diseases from the OpenTargets GraphQL API.
        """
        gm = await get_gene_mappings(query, raise_if_empty=True)
        ensembl_id = gm[0].ensembl_gene

        url = "https://api.platform.opentargets.org/api/v4/graphql"
        graphql_query = (
            """
            query associatedDiseases {
              target(ensemblId: \"%s\") {
                id
                approvedSymbol
                associatedDiseases {
                  count
                  rows {
                    disease {
                      id
                      name
                    }
                    datasourceScores {
                      id
                      score
                    }
                  }
                }
              }
            }
            """
            % ensembl_id
        )

        response = requests.post(url, json={"query": graphql_query})

        if response.status_code != 200:
            raise ToolError("Failed to fetch data from OpenTargets GraphQL API")
        j = response.json()
        df = pd.json_normalize(j.get("data").get("target").get("associatedDiseases").get("rows"))
        df.columns = df.columns.str.replace(".", "_")

        df = pd.concat([df, df.apply(_reformat_ot, axis=1)], axis=1)
        df = df.replace([np.nan], [None])
        return list(map(OTDiseaseAssociation.model_validate, df.to_dict(orient="records")))

    @mcp.tool()
    async def fetch_disease_targets(query: str) -> list[OTTargetAssociation]:
        """
        The endpoint takes a disease name and returns the associated targets from the OpenTargets GraphQL API.
        """
        try:
            disease = _get_closest_disease_ontology_term(query)
            if disease is None:
                raise ToolError(f"Could not find closest disease for {query!r}")
            
            try:
                obo_id = disease["obo_id"].replace(":", "_")
            except KeyError:
                raise ToolError(f"Could not find obo_id for {query!r}")

            url = "https://api.platform.opentargets.org/api/v4/graphql"
            graphql_query = (
                """
                query associatedTargets {
                  disease(efoId: \"%s\") {
                    id
                    name
                    associatedTargets {
                      count
                      rows {
                        target {
                          id
                          approvedSymbol
                        }
                        score
                        datatypeScores{
                          id
                          score
                        }
                      }
                    }
                  }
                }
                """
                % obo_id
            )

            response = requests.post(url, json={"query": graphql_query}, timeout=30)
            if response.status_code != 200:
                raise ToolError("Failed to fetch data from OpenTargets GraphQL API")

            j = response.json()
            df = pd.json_normalize(j.get("data").get("disease").get("associatedTargets").get("rows"))
            df.columns = df.columns.str.replace(".", "_")

            df = pd.concat([df, df.apply(lambda x: _reformat_ot(x, "datatypeScores"), axis=1)], axis=1)
            df = df.replace([np.nan], [None])
            df = df.rename(
                columns={
                    "target_approvedSymbol": "symbol",
                }
            )
            return list(map(OTTargetAssociation.model_validate, df.to_dict(orient="records")))
        except requests.Timeout:
            logger.error("Request to OpenTargets API timed out")
            raise ToolError("Request timed out while fetching disease targets")
        except requests.RequestException as e:
            logger.error(f"Error making request to OpenTargets API: {str(e)}")
            raise ToolError(f"Error fetching disease targets: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_associated_targets_for_disease: {str(e)}")
            raise ToolError(f"Unexpected error: {str(e)}")

# Helper functions remain at module level

def _get_closest_disease_ontology_term(query: str) -> Optional[dict[str, str]]:
    try:
        # First try exact match
        response = session.get(
            "https://www.ebi.ac.uk/ols4/api/search",
            params={
                "q": query,
                "ontology": "EFO",
                "obsoletes": "false",
                "local": "false",
                "allChildrenOf": "EFO_0000408",
                "rows": "10",  # Reduced from 100 to 10 for faster response
                "start": "0",
                "format": "json",
                "lang": "en",
                "exact": "true"  # Try exact match first
            },
            timeout=15  # Reduced timeout
        )
        response.raise_for_status()
        
        docs = response.json().get("response", {}).get("docs", [])
        if docs:
            # If we found an exact match, return it immediately
            return {"obo_id": docs[0]["obo_id"], "label": docs[0]["label"]}
            
        # If no exact match, try fuzzy search
        response = session.get(
            "https://www.ebi.ac.uk/ols4/api/search",
            params={
                "q": query,
                "ontology": "EFO",
                "obsoletes": "false",
                "local": "false",
                "allChildrenOf": "EFO_0000408",
                "rows": "10",  # Reduced from 100 to 10
                "start": "0",
                "format": "json",
                "lang": "en",
            },
            timeout=15
        )
        response.raise_for_status()
        
        docs = response.json().get("response", {}).get("docs", [])
        if not docs:
            return None

        # Only get embeddings for top 5 matches to reduce API calls
        df = pd.DataFrame(docs)
        disease_terms = df["label"].head(5).tolist()
        embeddings = _get_terms_embeddings(disease_terms)
        if not embeddings:
            return None
        query_embedding = _get_terms_embeddings([query])  # Pass as list to reuse function
        if not query_embedding:
            return None

        df = df.head(5)  # Only consider top 5 matches
        df["cosine_distance"] = np.dot(embeddings, query_embedding[0])
        df = df.nlargest(1, "cosine_distance")
        return df[["obo_id", "label"]].iloc[0].to_dict()
        
    except requests.Timeout:
        logger.error("Request to EBI OLS API timed out")
        return None
    except requests.RequestException as e:
        logger.error(f"Error making request to EBI OLS API: {str(e)}")
        return None


def _get_terms_embeddings(terms: list[str]) -> Optional[list[list[float]]]:
    url = "http://192.168.1.235:11434/api/embeddings"
    embeddings = []
    
    # Batch process terms to reduce API calls
    batch_size = 3
    for i in range(0, len(terms), batch_size):
        batch = terms[i:i + batch_size]
        try:
            response = session.post(
                url,
                json={"model": "nomic-embed-text", "prompt": batch},
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json().get("embedding")
            if not data or not isinstance(data, list) or not data:
                logger.error(f"Invalid embedding data for batch: {batch!r}")
                return None
            embeddings.extend(data)
            
        except requests.Timeout:
            logger.error(f"Timeout for batch: {batch!r}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error making request to Ollama API: {str(e)}")
            return None
            
    return embeddings


def _reformat_ot(row, key="datasourceScores"):
    d = {}
    for score in row[key]:
        d[f"{score.get('id')}_score"] = score.get("score")
    return pd.Series(d)
