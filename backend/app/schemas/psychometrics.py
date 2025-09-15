from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class BigFiveTrait(BaseModel):
    score: int
    rationale: str
    strategy: str


class BigFiveProfile(BaseModel):
    openness: BigFiveTrait
    conscientiousness: BigFiveTrait
    extraversion: BigFiveTrait
    agreeableness: BigFiveTrait
    neuroticism: BigFiveTrait


class DiscTrait(BaseModel):
    score: int
    rationale: str
    strategy: str


class DiscProfile(BaseModel):
    dominance: DiscTrait
    influence: DiscTrait
    steadiness: DiscTrait
    compliance: DiscTrait


class SchwartzValue(BaseModel):
    value_name: str
    strength: int
    rationale: str
    strategy: str
    is_present: bool


class CustomerArchetype(BaseModel):
    key: str
    name: str
    confidence: int
    description: str


class EvolutionTrend(BaseModel):
    big_five_trends: Dict[str, Any]
    disc_trends: Dict[str, Any]
    schwartz_trends: Dict[str, Any]


class PsychometricData(BaseModel):
    confidence_score: int
    summary: str
    big_five: Dict[str, BigFiveTrait]
    archetype: CustomerArchetype
    disc_profile: Dict[str, DiscTrait]
    schwartz_values: List[SchwartzValue]
    evolution_trend: EvolutionTrend

    model_config = {"from_attributes": True}