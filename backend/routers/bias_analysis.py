from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Article, BiasAnalysis
from services.bias_service_simple import BiasAnalysisService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class BiasAnalysisRequest(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None

class BiasAnalysisResponse(BaseModel):
    bias_score: float
    bias_direction: str
    biased_words: List[str]
    emotional_tone: str
    confidence_score: float
    neutral_summary: str
    recommendations: List[str]

class NeutralSummaryRequest(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None

class NeutralSummaryResponse(BaseModel):
    neutral_summary: str

@router.post("/analyze", response_model=BiasAnalysisResponse)
async def analyze_bias(request: BiasAnalysisRequest):
    """Analyze bias in an article"""
    try:
        if not request.url and not request.content:
            raise HTTPException(status_code=400, detail="URL or content is required")
        
        bias_service = BiasAnalysisService()
        
        # Analyze bias
        analysis_result = await bias_service.analyze_article_bias(
            request.content or "", 
            0.0  # Default bias score
        )
        
        return BiasAnalysisResponse(
            bias_score=analysis_result["bias_score"],
            bias_direction=analysis_result["bias_direction"],
            biased_words=analysis_result["biased_words"],
            emotional_tone=analysis_result["emotional_tone"],
            confidence_score=analysis_result["confidence_score"],
            neutral_summary=analysis_result["neutral_summary"],
            recommendations=analysis_result["recommendations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing bias: {str(e)}")

@router.post("/summarize", response_model=NeutralSummaryResponse)
async def generate_neutral_summary(request: NeutralSummaryRequest):
    """Generate a neutral summary of biased content"""
    try:
        if not request.url and not request.content:
            raise HTTPException(status_code=400, detail="URL or content is required")
        
        bias_service = BiasAnalysisService()
        
        neutral_summary = await bias_service.generate_neutral_summary(
            request.content or "",
            0.0  # Default bias score
        )
        
        return NeutralSummaryResponse(
            neutral_summary=neutral_summary["neutral_summary"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating neutral summary: {str(e)}")

@router.get("/{article_id}", response_model=BiasAnalysisResponse)
async def get_bias_analysis(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get bias analysis for a specific article"""
    analysis = db.query(BiasAnalysis).filter(BiasAnalysis.article_id == article_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Bias analysis not found")
    
    return BiasAnalysisResponse(
        bias_score=analysis.bias_score,
        bias_direction="neutral",
        biased_words=analysis.biased_words.split(",") if analysis.biased_words else [],
        emotional_tone=analysis.emotional_tone,
        confidence_score=0.8,
        neutral_summary=analysis.neutral_summary,
        recommendations=[]
    )

@router.get("/blindspots")
async def detect_blindspots(db: Session = Depends(get_db)):
    """Detect news stories that are only covered by one side of the media"""
    try:
        bias_service = BiasAnalysisService()
        blindspots = await bias_service.detect_blindspots(db)
        return {"blindspots": blindspots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting blindspots: {str(e)}")
