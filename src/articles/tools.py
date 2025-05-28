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
        """
        Search PubMed articles using structured criteria.
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
        """Get detailed information about a PubMed article.

        Args:
            ctx: The MCP server provided context
            pmid: PubMed ID of the article to retrieve

        Returns:
            A Markdown formatted string containing the article content
        """
        try:
            return await get_article(pmid)
        except Exception as e:
            return f"Error retrieving article: {str(e)}" 