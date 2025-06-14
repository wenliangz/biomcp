from mcp.server.fastmcp import Context
from typing import List

from src.dgidb.getter import search_drugs_for_gene

async def register_dgidb_tools(mcp):
    """
    Register DGIdb-related MCP tools.
    """

    @mcp.tool()
    async def get_drugs_for_gene(
        ctx: Context,
        gene_names: List[str],
    ) -> str:
        """
        Find drugs that interact with specified genes using DGIdb.

        Args:
            ctx: The MCP server provided context
            gene_names: A list of gene names to search for (e.g., ["BRAF", "EGFR"])

        Returns:
            A Markdown formatted string with the drug-gene interaction information or an error message.
        """
        try:
            # Check if gene_names list is empty
            if not gene_names:
                return "Please provide one or more gene names to search for."

            response, error = await search_drugs_for_gene(gene_names)

            if error:
                return f"Error retrieving drug-gene interactions: {error.message}"

            # Check if the response structure is as expected and contains data, and if any genes were found
            if not response or not response.data or not response.data.genes or not response.data.genes.nodes:
                # Explicitly list the gene names that were searched for
                return f"No interactions found for the specified gene(s): {', '.join(gene_names)}. Please check the gene name(s) and try again."

            output = ""
            for gene_node in response.data.genes.nodes:
                gene_name = gene_node.name # Access gene name directly from GeneNode
                if not gene_node.interactions:
                     output += f"Gene: {gene_name} - No interactions found.\n"
                     output += "---\n"
                     continue
                
                output += f"Gene: {gene_name}\n"
                for interaction in gene_node.interactions:
                    output += f"  Drug: {interaction.drug.name} (ID: {interaction.drug.conceptId})\n"
                    output += f"  Interaction Score: {interaction.interactionScore}\n"
                    interaction_types = ", ".join([t.type for t in interaction.interactionTypes]) if interaction.interactionTypes else "N/A"
                    output += f"  Interaction Types: {interaction_types}\n"
                    sources = ", ".join([s.sourceDbName for s in interaction.sources]) if interaction.sources else "N/A"
                    output += f"  Sources: {sources}\n"
                    publications = ", ".join([str(p.pmid) for p in interaction.publications]) if interaction.publications else "N/A"
                    output += f"  Publications: {publications}\n"
                    # Optionally add interaction attributes
                    # attributes = ", ".join([f"{attr.name}: {attr.value}" for attr in interaction.interactionAttributes]) if interaction.interactionAttributes else "N/A"
                    # output += f"  Attributes: {attributes}\n"
                    output += "---\n"

            return output.strip() # Remove trailing newline/separator

        except Exception as e:
            # Catch any other unexpected errors
            return f"An unexpected error occurred: {str(e)}" 