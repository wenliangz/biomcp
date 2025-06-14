from typing import List, Optional
from pydantic import BaseModel, Field

from src.utils import http_client, render
from src.utils.http_client import RequestError

DGIDB_API_URL = "https://dgidb.org/api/graphql"

class Source(BaseModel):
    sourceDbName: str = Field(..., alias="sourceDbName")

class Publication(BaseModel):
    pmid: int = Field(..., alias="pmid")

class InteractionAttribute(BaseModel):
    name: str = Field(..., alias="name")
    value: str = Field(..., alias="value")

class InteractionType(BaseModel):
    type: str = Field(..., alias="type")
    directionality: Optional[str] = Field(None, alias="directionality")

class Drug(BaseModel):
    name: str = Field(..., alias="name")
    conceptId: str = Field(..., alias="conceptId")

class Interaction(BaseModel):
    drug: Drug = Field(..., alias="drug")
    interactionScore: float = Field(..., alias="interactionScore")
    interactionTypes: List[InteractionType] = Field(..., alias="interactionTypes")
    interactionAttributes: List[InteractionAttribute] = Field(..., alias="interactionAttributes")
    publications: List[Publication] = Field(..., alias="publications")
    sources: List[Source] = Field(..., alias="sources")

class GeneNode(BaseModel):
    name: str = Field(..., alias="name")
    conceptId: str = Field(..., alias="conceptId")
    interactions: List[Interaction] = Field(..., alias="interactions")

class Genes(BaseModel):
    nodes: List[GeneNode] = Field(..., alias="nodes")

class DGIDbData(BaseModel):
    genes: Optional[Genes] = Field(None, alias="genes") # genes can be null or contain nodes: []

class DGIDbGraphQLResponse(BaseModel):
    data: Optional[DGIDbData] = Field(None, alias="data")
    # We might also need to handle errors, but focusing on the data structure first

async def search_drugs_for_gene(gene_names: List[str]) -> tuple[DGIDbGraphQLResponse | None, RequestError | None]:
    """
    Search DGIdb for drugs interacting with specified genes.
    """
    # Construct the GraphQL query
    query = """
    query($names: [String!]) {
      genes(names: $names) {
        nodes {
          # Added gene name and conceptId to GeneNode based on DGIDb docs
          name
          conceptId
          interactions {
            drug {
              name
              conceptId
            }
            interactionScore
            interactionTypes {
              type
              directionality
            }
            interactionAttributes {
              name
              value
            }
            publications {
              pmid
            }
            sources {
              sourceDbName
            }
          }
        }
      }
    }
    """

    variables = {"names": gene_names}

    # Make the API request
    response, error = await http_client.request_api(
        url=DGIDB_API_URL,
        request={"query": query, "variables": variables},
        response_model_type=DGIDbGraphQLResponse,
        method="POST", # GraphQL queries are typically POST requests
    )

    return response, error 