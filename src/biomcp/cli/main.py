import typer

from .articles import article_app
from .server import run_server
from .trials import trial_app
from .variants import variant_app

app = typer.Typer(
    help="BioMCP: Biomedical Model Context Protocol",
    no_args_is_help=True,
)

app.add_typer(
    trial_app,
    name="trial",
    no_args_is_help=True,
)

app.add_typer(
    article_app,
    name="article",
    no_args_is_help=True,
)

app.add_typer(
    variant_app,
    name="variant",
    no_args_is_help=True,
)


@app.command("run")
def run():
    """Run the BioMCP server"""
    return run_server()


if __name__ == "__main__":
    app()
