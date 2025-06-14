"""MCP tools for article search functionality."""

from mcp.server.fastmcp import Context

from src.articles.search import PubmedRequest, search_articles
from src.articles.getter import get_article

async def register_article_tools(mcp):
    """Register article-related MCP tools."""
    
    @mcp.tool()
    async def search_articles_tool(
        ctx: Context,
        chemicals="",
        diseases="",
        genes="",
        keywords="",
        variants=""
    ) -> str:
        """Search PubMed articles for research papers, therapies, and clinical studies.

        This tool is specifically for searching research articles, therapies, and clinical studies
        in the PubMed database. It is NOT for searching genetic variants directly.
        Use search_variants_tool for searching genetic variants.

        Examples of appropriate searches:
        - CAR-T cell therapy research
        - Recent advances in immunotherapy
        - Clinical trials for blood cancer
        - Gene therapy approaches
        - Drug development for specific diseases

        Args:
            ctx: The MCP server provided context
            chemicals: Comma-separated list of chemicals/drugs to search for
            diseases: Comma-separated list of diseases to search for
            genes: Comma-separated list of genes to search for
            keywords: Comma-separated list of keywords to search for
            variants: Comma-separated list of genetic variants to search for
        """
        try:
            def ensure_list(val):
                if not val:
                    return []
                if isinstance(val, list):
                    return val
                return [v.strip() for v in val.split(",") if v.strip()]
            request = PubmedRequest(
                chemicals=ensure_list(chemicals),
                diseases=ensure_list(diseases),
                genes=ensure_list(genes),
                keywords=ensure_list(keywords),
                variants=ensure_list(variants)
            )
            return await search_articles(request, output_json=True)
        except Exception as e:
            return f"Error searching articles: {str(e)}"

    @mcp.tool()
    async def article_details_tool(ctx: Context, pmid: int) -> str:
        """Get detailed information about a specific PubMed article.

        This tool retrieves the full details of a specific research article from PubMed.
        It is NOT for searching genetic variants directly.
        Use search_variants_tool for searching genetic variants.

        Args:
            ctx: The MCP server provided context
            pmid: PubMed ID of the article to retrieve (e.g., 12345678)
        """
        try:
            return await get_article(pmid)
        except Exception as e:
            return f"Error retrieving article: {str(e)}" 