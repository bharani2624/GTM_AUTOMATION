"""
AI-powered scoring and classification module using OpenAI-compatible APIs
Supports: OpenAI, OpenRouter, Groq, Together AI, Google Gemini
"""
from openai import OpenAI
from typing import Dict, Tuple
from config import Config
# import google.generativeai as genai
from google import genai

from test import response


class AIScorer:
    """Classify and score posts using AI"""
    
    def __init__(self):
        """Initialize AI client based on provider"""

        self.client = genai.Client(api_key="AIzaSyDSULfAB4OQw4KbW7k4VavycmOvSp-0zOU")
        self.provider = 'gemini'

    def classify_and_score(self, post_data: Dict) -> Dict:
        """
        Classify post relevance and score by intent
        
        Args:
            post_data: Dictionary containing post information
            
        Returns:
            Dictionary with classification results
        """
        post_text = post_data.get('full_text', '')
        title = post_data.get('title', '')
        
        if not post_text:
            return {
                'is_relevant': False,
                'relevance_score': 0.0,
                'intent': 'unknown',
                'intent_score': 0.0,
                'reasoning': 'Empty post content'
            }
        
        # Prepare classification prompt
        classification_prompt = f"""Analyze the following Reddit post and provide:
1. Relevance score (0.0-1.0): How relevant is this post to GTM (Go-To-Market), growth marketing, customer retention, or business growth topics?
2. Intent classification: One of ["question", "complaint", "vendor_search", "general_chatter", "case_study", "advice_seeking"]
3. Intent score (0.0-1.0): Confidence in the intent classification
4. Brief reasoning: 1-2 sentences explaining your assessment

Post Title: {title}
Post Content: {post_text[:1000]}  # Limit to first 1000 chars

Respond in this exact JSON format:
{{
    "relevance_score": <float 0.0-1.0>,
    "is_relevant": <boolean>,
    "intent": "<one of: question, complaint, vendor_search, general_chatter, case_study, advice_seeking>",
    "intent_score": <float 0.0-1.0>,
    "reasoning": "<brief explanation>"
}}"""
        
        try:
            if True:
                return self._classify_with_gemini(post_data, classification_prompt)
            
            result = response.choices[0].message.content
            import json
            try:
                classification = json.loads(result)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse JSON response: {str(e)}")
                print(f"Response was: {result[:200]}")
                return self._fallback_classification(post_data)
            
            # Ensure relevance threshold
            is_relevant = classification.get('is_relevant', False) or \
                         classification.get('relevance_score', 0.0) >= Config.RELEVANCE_THRESHOLD
            
            return {
                'is_relevant': is_relevant,
                'relevance_score': float(classification.get('relevance_score', 0.0)),
                'intent': classification.get('intent', 'unknown'),
                'intent_score': float(classification.get('intent_score', 0.0)),
                'reasoning': classification.get('reasoning', 'No reasoning provided')
            }
        
        except Exception as e:
            print(f"Error in AI classification: {str(e)}")
            # Fallback: simple keyword-based relevance
            return self._fallback_classification(post_data)
    
    def _fallback_classification(self, post_data: Dict) -> Dict:
        """Fallback classification using keyword matching"""
        text = post_data.get('full_text', '').lower()
        keywords = [k.lower() for k in Config.KEYWORDS]
        
        matches = sum(1 for keyword in keywords if keyword in text)
        relevance = min(matches / len(keywords) if keywords else 0, 1.0)
        
        return {
            'is_relevant': relevance >= Config.RELEVANCE_THRESHOLD,
            'relevance_score': relevance,
            'intent': 'general_chatter',
            'intent_score': 0.5,
            'reasoning': 'Fallback classification based on keyword matching'
        }
    
    def _classify_with_gemini(self, post_data: Dict, prompt: str) -> Dict:
        """Classify using Google Gemini API"""
        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are an expert GTM analyst. Respond ONLY with a JSON object matching the required schema. {prompt}"
            )
            import json, re
            raw = (response.text or "").strip()
            if not raw:
                return self._fallback_classification(post_data)
            try:
                classification = json.loads(raw)
            except Exception:
                m = re.search(r"\{[\s\S]*\}", raw)
                if m:
                    classification = json.loads(m.group(0))
                else:
                    return self._fallback_classification(post_data)
            
            is_relevant = classification.get('is_relevant', False) or \
                         classification.get('relevance_score', 0.0) >= Config.RELEVANCE_THRESHOLD
            
            return {
                'is_relevant': is_relevant,
                'relevance_score': float(classification.get('relevance_score', 0.0)),
                'intent': classification.get('intent', 'unknown'),
                'intent_score': float(classification.get('intent_score', 0.0)),
                'reasoning': classification.get('reasoning', 'No reasoning provided')
            }
        except Exception as e:
            print(f"Error in Gemini classification: {str(e)}")
            return self._fallback_classification(post_data)
    
    def generate_summary(self, post_data: Dict, max_length: int = 200) -> str:
        """Generate a concise summary of the post"""
        post_text = post_data.get('full_text', '')
        
        if len(post_text) <= max_length:
            return post_text
        
        prompt = f"""Summarize the following Reddit post in {max_length} characters or less. Focus on the main question or topic:{post_text[:1500]} Summary:"""
        
        try:
            # Gemini uses different API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{prompt}"
            )
            import json, re
            raw = (response.text or "").strip()
            m = re.search(r"\{[\s\S]*\}", raw)
            if m != None:
                response=json.loads(m.group(0))
            else:
                response=raw
            return response
        
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            # Fallback: truncate
            return post_text[:max_length] + "..."

    def generate_sentiment(self,post):
        try:
            import json, re
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Find the sentiment and sentiment level [0-10] of this {post} give it as json struct"
            )
            raw = (response.text or "").strip()
            m = re.search(r"\{[\s\S]*\}", raw)
            if m != None:
                response=json.loads(m.group(0))
            else:
                response=raw
            return response
        except Exception as e:
            print(f"Error generating sentiment: {str(e)}")
            return ""

