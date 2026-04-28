from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator

class SeverityClass(Enum):
    NONE = 0
    MINOR = 1
    MODERATE = 2
    SEVERE = 3
    MAJOR = 4


class IncidentRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    narrative: str = Field(
        min_length=50,
        description="Full incident narrative from a health and social care care home setting."
    )
    confirmed_hc_domain: bool = Field(
        description="User confirms this incident is from a health and social care care home setting."
    )

    @field_validator("confirmed_hc_domain")
    @classmethod
    def must_confirm_domain(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "This API only accepts incidents from health and social care care home settings. "
                "Set confirmed_hc_domain to True to confirm the incident is from this domain."
            )
        return v

class ConfirmedFactsRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    injury_type: str
    persons_involved: str
    circumstances: str
    known_severity: str
    predicted_incapacitation: str = Field(
        default="unknown",
        description="Predicted incapacitation label from severity tool, confirmed by user."
    )
    
class SeverityPrediction(BaseModel):
    model_config = ConfigDict(frozen=True)

    probabilities: dict[str, float] = Field(
        description="Probability distribution across all five severity classes."
    )
    predicted_class: SeverityClass = Field(
        description="Predicted severity class."
    )
    confidence: float = Field(
        description="Confidence score for the predicted class."
    )
    needlestick_flag: bool = Field(
        default=False,
        description="True if needle-related terms detected. Mandatory human review required."
    )
    
    predicted_label: str = Field(
    description="Human-readable severity label including indicative absence duration."
    )
    
    middle_severity_flag: bool = Field(
        default=False,
        description=(
            "True if predicted class is Moderate or Severe. These classes have higher uncertainty and "
            "potentially more serious outcomes. Mandatory human review recommended."
        )
    )


class RiddorCategory(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: str = Field(description="RIDDOR 2013 category name.")
    description: str = Field(description="Description of the category.")
    information_needed: list[str] = Field(
        description="Additional information needed to confirm or rule out this category."
    )
    reporting_deadline: str = Field(
        description="Reporting deadline if this category applies."
    )


class RiddorAdvisory(BaseModel):
    model_config = ConfigDict(frozen=True)

    potentially_applicable: list[RiddorCategory] = Field(
        description="RIDDOR categories that may potentially apply."
    )
    follow_up_questions: list[str] = Field(
        description="Questions the user should pursue to confirm applicability."
    )
    disclaimer: str = Field(
        default=(
            "This output is advisory only. A competent person must make the final "
            "RIDDOR determination when full information is available."
        ),
        description="Mandatory advisory disclaimer."
    )


class CausalFactor(BaseModel):
    model_config = ConfigDict(frozen=True)

    cause_type: str = Field(
        description="Category of cause — primary activity, environmental factor, or injury mechanism."
    )
    description: str = Field(description="Description of the identified cause.")
    hsg220_section: str = Field(description="Relevant HSG220 section reference.")
    mitigation_actions: list[str] = Field(
        description="Possible mitigation actions to investigate."
    )


class CausalAnalysis(BaseModel):
    model_config = ConfigDict(frozen=True)

    identified_causes: list[CausalFactor] = Field(
        description="All contributing causes identified in the narrative."
    )
    disclaimer: str = Field(
        default=(
            "These are directions for investigation only. Determination of root cause "
            "requires full investigation by a competent person."
        ),
        description="Mandatory investigation disclaimer."
    )


class SimilarIncident(BaseModel):
    model_config = ConfigDict(frozen=True)

    narrative_excerpt: str = Field(description="Excerpt from a similar historical incident.")
    severity_outcome: SeverityClass = Field(description="Severity outcome of the similar incident.")


class PatternAnalysis(BaseModel):
    model_config = ConfigDict(frozen=True)

    similar_incidents: list[SimilarIncident] = Field(
        description="Top similar incidents from the H&C OSHA dataset."
    )
    severity_distribution: dict[str, float] = Field(
        description="Base rate severity distribution across all five classes for the identified injury mechanism."
    )
    injury_mechanism: str = Field(
        description="Identified injury mechanism used for distribution lookup."
    )


class TriageResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    severity_prediction: SeverityPrediction
    riddor_advisory: RiddorAdvisory
    causal_analysis: CausalAnalysis
    pattern_analysis: PatternAnalysis
    domain_disclaimer: str = Field(
        default=(
            "DOMAIN CONSTRAINT: This system was trained exclusively on OSHA Health and Social Care "
            "sector data from care home settings. It has not been validated outside this domain. "
            "All outputs are decision-support tools only, not compliance determinations."
        )
    )