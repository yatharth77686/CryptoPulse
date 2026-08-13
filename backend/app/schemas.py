from datetime import datetime
from typing import Any

from pydantic import BaseModel


class APIStatus(BaseModel):
    message: str
    status: str


class AnalysisResponse(BaseModel):
    count: int
    results: list[dict[str, Any]]


class SentimentSummary(BaseModel):
    model: str
    summary: dict[str, int]
    total_posts: int


class CryptoAnalysisResponse(BaseModel):
    symbol: str
    count: int
    results: list[dict[str, Any]]


class MarketReactionResponse(BaseModel):
    symbol: str
    count: int
    reactions: list[dict[str, Any]]


class AnalyzeRequest(BaseModel):
    text: str
    timestamp: datetime
    followers: int = 0
    likes: int = 0
    retweets: int = 0

class AssetInfo(BaseModel):
    primary: str | None
    mentioned: list[str]        


class AnalyzeResponse(BaseModel):
    text: str
    assets: AssetInfo
    sentiment: dict[str, Any]
    social_influence: dict[str, Any]
    signal_strength: float
    market_reaction: dict[str, Any]


