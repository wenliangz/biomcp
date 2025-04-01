"""BioMCP Command Line Interface for clinical trials."""

import asyncio
from typing import Annotated

import typer

from ..trials.getter import Module, get_trial
from ..trials.search import (
    AgeGroup,
    DateField,
    InterventionType,
    PrimaryPurpose,
    RecruitingStatus,
    SortOrder,
    SponsorType,
    StudyDesign,
    StudyType,
    TrialPhase,
    TrialQuery,
    search_trials,
)

trial_app = typer.Typer(help="Clinical trial operations")


@trial_app.command("get")
def get_trial_cli(
    nct_id: str,
    module: Annotated[
        Module | None,
        typer.Argument(
            help="Module to retrieve: Protocol, Locations, References, or Outcomes",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = Module.PROTOCOL,
    output_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Render in JSON format",
            case_sensitive=False,
        ),
    ] = False,
):
    """Get trial information by NCT ID and optional module."""
    result = asyncio.run(
        get_trial(nct_id, module or Module.PROTOCOL, output_json)
    )
    typer.echo(result)


@trial_app.command("search")
def search_trials_cli(
    condition: Annotated[
        list[str] | None,
        typer.Option(
            "--condition",
            "-c",
            help="Medical condition to search for (can specify multiple)",
        ),
    ] = None,
    intervention: Annotated[
        list[str] | None,
        typer.Option(
            "--intervention",
            "-i",
            help="Treatment or intervention to search for (can specify multiple)",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    term: Annotated[
        list[str] | None,
        typer.Option(
            "--term",
            "-t",
            help="General search terms (can specify multiple)",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    nct_id: Annotated[
        list[str] | None,
        typer.Option(
            "--nct-id",
            "-n",
            help="Clinical trial NCT ID (can specify multiple)",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    recruiting_status: Annotated[
        RecruitingStatus | None,
        typer.Option(
            "--status",
            "-s",
            help="Recruiting status.",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    study_type: Annotated[
        StudyType | None,
        typer.Option(
            "--type",
            help="Study type",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    phase: Annotated[
        TrialPhase | None,
        typer.Option(
            "--phase",
            "-p",
            help="Trial phase",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    sort_order: Annotated[
        SortOrder | None,
        typer.Option(
            "--sort",
            help="Sort order",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    age_group: Annotated[
        AgeGroup | None,
        typer.Option(
            "--age-group",
            "-a",
            help="Age group filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    primary_purpose: Annotated[
        PrimaryPurpose | None,
        typer.Option(
            "--purpose",
            help="Primary purpose filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    min_date: Annotated[
        str | None,
        typer.Option(
            "--min-date",
            help="Minimum date for filtering (YYYY-MM-DD format)",
        ),
    ] = None,
    max_date: Annotated[
        str | None,
        typer.Option(
            "--max-date",
            help="Maximum date for filtering (YYYY-MM-DD format)",
        ),
    ] = None,
    date_field: Annotated[
        DateField | None,
        typer.Option(
            "--date-field",
            help="Date field to filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = DateField.STUDY_START,
    intervention_type: Annotated[
        InterventionType | None,
        typer.Option(
            "--intervention-type",
            help="Intervention type filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    sponsor_type: Annotated[
        SponsorType | None,
        typer.Option(
            "--sponsor-type",
            help="Sponsor type filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    study_design: Annotated[
        StudyDesign | None,
        typer.Option(
            "--study-design",
            help="Study design filter",
            show_choices=True,
            show_default=True,
            case_sensitive=False,
        ),
    ] = None,
    next_page_hash: Annotated[
        str | None,
        typer.Option(
            "--next-page",
            help="Next page hash for pagination",
        ),
    ] = None,
    latitude: Annotated[
        float | None,
        typer.Option(
            "--lat",
            help="Latitude for location-based search",
        ),
    ] = None,
    longitude: Annotated[
        float | None,
        typer.Option(
            "--lon",
            help="Longitude for location-based search",
        ),
    ] = None,
    distance: Annotated[
        int | None,
        typer.Option(
            "--distance",
            "-d",
            help="Distance in miles for location-based search",
        ),
    ] = None,
    output_json: Annotated[
        bool,
        typer.Option(
            "--json",
            "-j",
            help="Render in JSON format",
            case_sensitive=False,
        ),
    ] = False,
):
    """Search for clinical trials."""
    query = TrialQuery(
        conditions=condition,
        interventions=intervention,
        terms=term,
        nct_ids=nct_id,
        recruiting_status=recruiting_status,
        study_type=study_type,
        phase=phase,
        sort=sort_order,
        age_group=age_group,
        primary_purpose=primary_purpose,
        min_date=min_date,
        max_date=max_date,
        date_field=date_field,
        intervention_type=intervention_type,
        sponsor_type=sponsor_type,
        study_design=study_design,
        next_page_hash=next_page_hash,
        lat=latitude,
        long=longitude,
        distance=distance,
    )

    result = asyncio.run(search_trials(query, output_json))
    typer.echo(result)
