import openai
import os
from typing import Dict, List, Any
import asyncio

class TranslatorService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Supported languages
        self.supported_languages = {
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "ur": "Urdu"
        }
    
    async def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Dict[str, Any]:
        """Translate text to target language"""
        try:
            if target_language not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            target_lang_name = self.supported_languages[target_language]
            
            # Use OpenAI for translation
            prompt = f"Translate the following text to {target_lang_name}. Maintain the original meaning and context:\n\n{text}"
            
            response = await self._call_openai(prompt)
            
            return {
                "original_text": text,
                "translated_text": response,
                "source_language": source_language,
                "target_language": target_language,
                "target_language_name": target_lang_name
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "original_text": text,
                "translated_text": text,  # Fallback to original
                "source_language": source_language,
                "target_language": target_language
            }
    
    async def translate_article(self, article: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate an entire article"""
        translated_article = article.copy()
        
        # Translate title
        if article.get('title'):
            title_result = await self.translate_text(article['title'], target_language)
            translated_article['title'] = title_result['translated_text']
        
        # Translate description
        if article.get('description'):
            desc_result = await self.translate_text(article['description'], target_language)
            translated_article['description'] = desc_result['translated_text']
        
        # Add translation metadata
        translated_article['translation_info'] = {
            "target_language": target_language,
            "target_language_name": self.supported_languages.get(target_language, target_language),
            "translated_at": datetime.now().isoformat()
        }
        
        return translated_article
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API for translation"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Provide accurate translations while maintaining context and meaning."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages