"""
Engagement suggestion generator for relevant posts
"""
from openai import OpenAI
from typing import Dict
from config import Config
import google.generativeai as genai
from ai_scorer import AIScorer

class EngagementGenerator:
    """Generate personalized engagement suggestions"""
    
    def __init__(self):
        """Initialize AI client based on provider"""
        self.provider = Config.AI_PROVIDER
        
        # Provider-specific initialization
        if self.provider == 'openrouter':
            api_key = Config.OPENROUTER_API_KEY or Config.OPENAI_API_KEY
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            self.model = Config.AI_MODEL or "google/gemini-pro-1.5:free"
        elif self.provider == 'groq':
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=Config.GROQ_API_KEY
            )
            self.model = Config.AI_MODEL or "llama-3.1-8b-instant"
        elif self.provider == 'together':
            self.client = OpenAI(
                base_url="https://api.together.xyz/v1",
                api_key=Config.TOGETHER_API_KEY
            )
            self.model = Config.AI_MODEL or "meta-llama/Llama-3-8b-chat-hf"
        elif self.provider == 'gemini':
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.client = None
            self.model = Config.AI_MODEL or "gemini-pro"
        else:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.AI_MODEL or "gpt-4o-mini"
    
    def generate_suggestion(self, post_data: Dict, classification: Dict) -> Dict:
        """
        Generate engagement suggestion based on post and classification
        
        Args:
            post_data: Post information
            classification: AI classification results
            
        Returns:
            Dictionary with engagement suggestions
        """
        post_text = post_data.get('full_text', '')
        intent = classification.get('intent', 'unknown')
        relevance_score = classification.get('relevance_score', 0.0)
        
        # Different approaches based on intent
        if intent == 'question':
            suggestion_type = 'helpful_comment'
            tone = 'helpful and educational'
        elif intent == 'vendor_search':
            suggestion_type = 'solution_pitch'
            tone = 'professional and solution-oriented'
        elif intent == 'advice_seeking':
            suggestion_type = 'consultative_comment'
            tone = 'friendly and consultative'
        elif intent == 'complaint':
            suggestion_type = 'empathetic_response'
            tone = 'empathetic and solution-focused'
        else:
            suggestion_type = 'value_add_comment'
            tone = 'engaging and value-adding'
        
        prompt = f"""Generate a personalized Reddit comment or engagement suggestion for this post.

Post Title: {post_data.get('title', '')}
Post Content: {post_data.get('content', '')[:1000]}
Post Intent: {intent}
Relevance Score: {relevance_score}

Guidelines:
- Type: {suggestion_type}
- Tone: {tone}
- Length: 2-4 sentences (concise and valuable)
- Do NOT be overly salesy or pushy
- Add genuine value to the conversation
- If relevant, subtly mention how we help with similar challenges
- Be authentic and Reddit-native (use casual, helpful language)

Generate:
1. A comment draft (2-4 sentences)
2. A brief DM draft (if appropriate for this intent)
3. Engagement strategy (one sentence on approach)

Respond in JSON format:
{{
    "comment_draft": "<draft comment text>",
    "dm_draft": "<draft DM text or null>",
    "strategy": "<brief engagement strategy>",
    "priority": "high|medium|low"
}}"""
        
        try:
            # Google Gemini uses different API
            if self.provider == 'gemini':
                return self._generate_with_gemini(post_data, classification, prompt)

        except Exception as e:
            print(f"Error generating engagement suggestion: {str(e)}")
            return self._fallback_suggestion(post_data, classification)
    
    def _generate_with_gemini(self, post_data: Dict, classification: Dict, prompt: str) -> Dict:
        try:
            self.client=AIScorer().client
            resp = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a growth marketing expert. Respond ONLY with JSON matching the schema. {prompt}"
            )
            import json, re
            raw = (resp.text or "").strip()
            if not raw:
                return self._fallback_suggestion(post_data, classification)
            try:
                engagement = json.loads(raw)
            except Exception:
                m = re.search(r"\{[\s\S]*\}", raw)
                if m:
                    engagement = json.loads(m.group(0))
                else:
                    return self._fallback_suggestion(post_data, classification)

            relevance_score = classification.get('relevance_score', 0.0)
            intent = classification.get('intent', 'unknown')
            if relevance_score >= 0.9 or intent in ['vendor_search', 'advice_seeking']:
                engagement['priority'] = 'high'
            elif relevance_score >= 0.75:
                engagement['priority'] = 'medium'
            else:
                engagement['priority'] = 'low'
            return engagement
        except Exception as e:
            print(f"Error generating engagement with Gemini: {str(e)}")
            return self._fallback_suggestion(post_data, classification)

    def _fallback_suggestion(self, post_data: Dict, classification: Dict) -> Dict:
        """Fallback engagement suggestion"""
        title = post_data.get('title', '')
        
        return {
            'comment_draft': f"Thanks for sharing this, {title.split()[0] if title else 'there'}. This is an interesting topic. Would love to learn more about your specific situation and see if we can help.",
            'dm_draft': f"Hi! Saw your post about {title[:50]}. We work with companies facing similar challenges. Would you be open to a quick chat?",
            'strategy': 'Engage with helpful context first, then offer value-based follow-up',
            'priority': 'medium'
        }

