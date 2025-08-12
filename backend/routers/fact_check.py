from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Article, FactCheck
from services.fact_check_service import FactCheckService
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter()

class FactCheckRequest(BaseModel):
    claim: Optional[str] = None
    url: Optional[str] = None

class FactCheckResponse(BaseModel):
    id: int
    claim: str
    verdict: str  # real, fake, needs_context
    confidence_score: float
    evidence: List[str]
    fact_check_date: datetime
    
    class Config:
        from_attributes = True

class FactCheckResult(BaseModel):
    claim: str
    verdict: str
    confidence_score: float
    evidence: List[str]
    sources: List[str]
    explanation: str

@router.post("/verify", response_model=FactCheckResult)
async def verify_claim(request: FactCheckRequest):
    """Verify a news claim using Google Search API and AI analysis"""
    try:
        if not request.claim and not request.url:
            raise HTTPException(status_code=400, detail="Claim or URL is required")
        
        fact_check_service = FactCheckService()
        
        # Verify the claim
        claim_text = request.claim or request.url or ""
        result = await fact_check_service.verify_claim(claim_text)
        
        return FactCheckResult(
            claim=claim_text,
            verdict=result["verdict"],
            confidence_score=result["confidence_score"],
            evidence=result["evidence"],
            sources=result.get("sources", []),
            explanation=result["explanation"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying claim: {str(e)}")

@router.post("/upload")
async def fact_check_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Fact-check content from uploaded image or PDF"""
    try:
        fact_check_service = FactCheckService()
        
        # Extract text from uploaded file
        content = await fact_check_service.extract_text_from_file(file)
        
        # Verify the extracted content
        result = await fact_check_service.verify_claim(content)
        
        return {
            "extracted_content": content,
            "verdict": result["verdict"],
            "confidence_score": result["confidence_score"],
            "evidence": result["evidence"],
            "explanation": result["explanation"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing uploaded file: {str(e)}")

@router.post("/url")
async def fact_check_url(
    url: str,
    db: Session = Depends(get_db)
):
    """Fact-check content from a URL"""
    try:
        fact_check_service = FactCheckService()
        
        # Extract content from URL
        content = await fact_check_service.extract_content_from_url(url)
        
        # Verify the extracted content
        result = await fact_check_service.verify_claim(content)
        
        return {
            "url": url,
            "extracted_content": content,
            "verdict": result["verdict"],
            "confidence_score": result["confidence_score"],
            "evidence": result["evidence"],
            "explanation": result["explanation"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

@router.get("/{fact_check_id}", response_model=FactCheckResponse)
async def get_fact_check(
    fact_check_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific fact-check by ID"""
    fact_check = db.query(FactCheck).filter(FactCheck.id == fact_check_id).first()
    if not fact_check:
        raise HTTPException(status_code=404, detail="Fact check not found")
    
    return FactCheckResponse(
        id=fact_check.id,
        claim=fact_check.claim,
        verdict=fact_check.verdict,
        confidence_score=fact_check.confidence_score,
        evidence=json.loads(fact_check.evidence) if fact_check.evidence else [],
        fact_check_date=fact_check.fact_check_date
    )

@router.get("/article/{article_id}", response_model=List[FactCheckResponse])
async def get_article_fact_checks(
    article_id: int,
    db: Session = Depends(get_db)
):
    """Get all fact-checks for a specific article"""
    fact_checks = db.query(FactCheck).filter(FactCheck.article_id == article_id).all()
    
    return [
        FactCheckResponse(
            id=fc.id,
            claim=fc.claim,
            verdict=fc.verdict,
            confidence_score=fc.confidence_score,
            evidence=json.loads(fc.evidence) if fc.evidence else [],
            fact_check_date=fc.fact_check_date
        )
        for fc in fact_checks
    ]
