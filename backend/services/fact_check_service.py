import httpx
import openai
import os
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class FactCheckService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    async def verify_claim(self, claim: str) -> Dict:
        """Verify a claim using multiple sources"""
        try:
            # Search for evidence
            evidence = await self._search_evidence(claim)
            
            # Analyze evidence with AI
            analysis = await self._analyze_evidence(claim, evidence)
            
            return {
                "claim": claim,
                "verdict": analysis.get("verdict", "unverified"),
                "confidence_score": analysis.get("confidence", 0.5),
                "evidence": evidence[:5],  # Top 5 evidence pieces
                "sources": analysis.get("sources", []),
                "explanation": analysis.get("explanation", "Unable to verify claim.")
            }
        except Exception as e:
            return {
                "claim": claim,
                "verdict": "unverified",
                "confidence_score": 0.0,
                "evidence": [],
                "sources": [],
                "explanation": f"Error during verification: {str(e)}"
            }
    
    async def _search_evidence(self, claim: str) -> List[str]:
        """Search for evidence using Google Custom Search"""
        if not self.google_api_key or not self.google_cse_id:
            return [f"Search for: {claim}"]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": self.google_api_key,
                        "cx": self.google_cse_id,
                        "q": claim,
                        "num": 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [item.get("snippet", "") for item in data.get("items", [])]
                else:
                    return [f"Search for: {claim}"]
        except Exception:
            return [f"Search for: {claim}"]
    
    async def _analyze_evidence(self, claim: str, evidence: List[str]) -> Dict:
        """Analyze evidence using OpenAI"""
        try:
            evidence_text = "\n".join(evidence[:5])
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact-checker. Analyze the claim and evidence to determine if it's true, false, misleading, or unverified. Return JSON with: verdict (true/false/misleading/unverified), confidence (0-1), explanation, sources."
                    },
                    {
                        "role": "user",
                        "content": f"Claim: {claim}\n\nEvidence:\n{evidence_text}"
                    }
                ],
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except:
                return {
                    "verdict": "unverified",
                    "confidence": 0.5,
                    "explanation": "Unable to analyze evidence.",
                    "sources": []
                }
        except Exception as e:
            return {
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": f"Error in analysis: {str(e)}",
                "sources": []
            }
    
    async def extract_text_from_file(self, file_content: bytes) -> str:
        """Extract text from uploaded file (simplified version)"""
        # For now, return a placeholder
        return "Text extraction from files requires Pillow. Please install Visual C++ Build Tools and try again."
    
    async def extract_content_from_url(self, url: str) -> str:
        """Extract content from URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text[:2000]  # First 2000 characters
                else:
                    return f"Unable to access URL: {url}"
        except Exception as e:
            return f"Error accessing URL: {str(e)}"
    
    async def verify_multiple_claims(self, claims: List[str]) -> List[Dict]:
        """Verify multiple claims"""
        results = []
        for claim in claims:
            result = await self.verify_claim(claim)
            results.append(result)
        return results
    
    def _calculate_confidence_score(self, evidence_count: int, source_quality: float) -> float:
        """Calculate confidence score based on evidence"""
        base_score = min(evidence_count / 5.0, 1.0)
        return min(base_score * source_quality, 1.0)
