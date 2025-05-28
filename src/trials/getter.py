"""Getter module for retrieving clinical trial details."""

import json
from typing import Any
from enum import StrEnum

from pydantic import BaseModel, Field

from src.utils import const, http_client, render
from src.utils.http_client import RequestError

CLINICALTRIALS_API_BASE = f"{const.CT_GOV_STUDIES}/study/"


class Module(StrEnum):
    """Enum for clinical trial module types."""
    PROTOCOL = "Protocol"
    LOCATIONS = "Locations"
    REFERENCES = "References"
    OUTCOMES = "Outcomes"


modules: dict[Module, list[str]] = {
    Module.PROTOCOL: [
        "IdentificationModule",
        "StatusModule",
        "SponsorCollaboratorsModule",
        "OversightModule",
        "DescriptionModule",
        "ConditionsModule",
        "DesignModule",
        "ArmsInterventionsModule",
        "EligibilityModule",
    ],
    Module.LOCATIONS: ["ContactsLocationsModule"],
    Module.REFERENCES: ["ReferencesModule"],
    Module.OUTCOMES: ["OutcomesModule", "ResultsSection"],
}


class TrialResponse(BaseModel):
    """Response model for clinical trial data."""
    NCTNumber: str = Field(..., description="NCT number of the trial")
    BriefTitle: str = Field(..., description="Brief title of the trial")
    OfficialTitle: str = Field(..., description="Official title of the trial")
    Status: str = Field(..., description="Current status of the trial")
    Phase: str = Field(..., description="Trial phase")
    Enrollment: int = Field(..., description="Number of participants")
    Condition: list[str] = Field(..., description="List of conditions")
    Intervention: list[str] = Field(..., description="List of interventions")
    Location: list[str] = Field(..., description="List of locations")
    Sponsor: str = Field(..., description="Trial sponsor")
    StartDate: str = Field(..., description="Trial start date")
    CompletionDate: str = Field(..., description="Trial completion date")
    LastUpdateDate: str = Field(..., description="Last update date")
    BriefSummary: str = Field(..., description="Brief summary of the trial")
    DetailedDescription: str = Field(..., description="Detailed description")
    EligibilityCriteria: str = Field(..., description="Eligibility criteria")
    StudyType: str = Field(..., description="Type of study")
    StudyDesign: str = Field(..., description="Study design")
    PrimaryOutcome: list[str] = Field(..., description="Primary outcomes")
    SecondaryOutcome: list[str] = Field(..., description="Secondary outcomes")
    OtherOutcome: list[str] = Field(..., description="Other outcomes")
    Arms: list[dict[str, Any]] = Field(..., description="Study arms")
    Publications: list[str] = Field(..., description="Related publications")


async def get_trial(nct_id: str, module: Module | None = None, output_json: bool = False) -> str:
    """Get detailed information about a clinical trial by NCT ID.
    
    Args:
        nct_id: The NCT ID of the trial to retrieve
        module: Optional module type to filter the response
        output_json: Whether to return JSON format instead of Markdown
        
    Returns:
        A string containing the trial information in the requested format
    """
    response, error = await http_client.request_api(
        url=f"{CLINICALTRIALS_API_BASE}{nct_id}",
        request={},
        response_model_type=TrialResponse,
    )

    if error:
        data = [{"error": f"Error {error.code}: {error.message}"}]
    else:
        data = [response.model_dump(mode="json", exclude_none=True)]

    if not output_json:
        return render.to_markdown(data)
    else:
        return json.dumps(data, indent=2)
