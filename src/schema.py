from pydantic import BaseModel, Field #let's use it to provide early-validation (coming from LLM)
from typing import Literal


class FinancialHealth(BaseModel):
    leverage: Literal["low", "medium", "high"]
    liquidity: Literal["strong", "weak"]
    comment: str


class EarningsQuality(BaseModel):
    stability: Literal["stable", "volatile"]
    trend: Literal["growing", "declining"]
    comment: str


class GrahamScorecard(BaseModel):
    company: str
    year: int
    financial_health: FinancialHealth
    earnings_quality: EarningsQuality
    moat_signals: list[str]
    red_flags: list[str]
    graham_score_llm: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
