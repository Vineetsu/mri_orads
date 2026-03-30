import groq
import json
import logging
from config import Config
from utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self):
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL
    
    def analyze_mri_image(self, image_features, image_description=None):
        """Send image analysis request to Groq API"""
        try:
            # Create the prompt with image features
            prompt = PromptTemplates.get_analysis_prompt(image_features, image_description)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized radiologist AI assistant for ovarian MRI analysis. Provide accurate O-RADS scoring based on image characteristics."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent medical analysis
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = response.choices[0].message.content
            analysis = json.loads(result)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self):
        """Return fallback analysis if API fails"""
        return {
            "orads_score": 3,
            "cancer_risk": "1-10%",
            "cancer_detected": False,
            "confidence": "Medium",
            "analysis": {
                "lesion_type": "Unable to determine accurately",
                "characteristics": "Analysis requires manual review"
            },
            "recommendations": {
                "next_steps": "Please consult with a radiologist for proper evaluation",
                "consulting_places": "Contact your local hospital's radiology department",
                "additional_tests": "Manual review recommended",
                "follow_up": "Schedule appointment with specialist"
            }
        }