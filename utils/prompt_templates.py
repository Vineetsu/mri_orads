class PromptTemplates:
    @staticmethod
    def get_analysis_prompt(image_features, image_description=None):
        """Generate comprehensive prompt for MRI analysis"""
        
        features_text = ""
        if image_features:
            features_text = f"""
Image Features Extracted:
- Mean Intensity: {image_features.get('mean_intensity', 'N/A')}
- Intensity Variation: {image_features.get('std_intensity', 'N/A')}
- Edge Density: {image_features.get('edge_density', 'N/A')}
- Texture Contrast: {image_features.get('contrast', 'N/A')}
- Tissue Homogeneity: {image_features.get('homogeneity', 'N/A')}
- Image Dimensions: {image_features.get('dimensions', 'N/A')}
"""
        
        prompt = f"""
Analyze this ovarian MRI image and provide a detailed O-RADS assessment.

{features_text}

Based on MRI imaging characteristics, evaluate:
1. Lesion composition (solid/cystic/complex)
2. Wall characteristics (smooth/irregular/thickened)
3. Septations (thin/thick/nodular)
4. Solid components presence and morphology
5. Enhancement patterns
6. Presence of ascites
7. Peritoneal involvement

Provide a comprehensive O-RADS score analysis in JSON format with the following structure:

{{
    "orads_score": integer (1-5),
    "cancer_risk": string,
    "cancer_detected": boolean,
    "confidence": string (High/Medium/Low),
    "analysis": {{
        "lesion_type": string,
        "characteristics": string,
        "key_findings": [list of strings]
    }},
    "recommendations": {{
        "next_steps": string,
        "consulting_places": string,
        "additional_tests": string,
        "follow_up": string
    }}
}}

Make the analysis specific, professional, and actionable for both patients and healthcare providers.
"""
        return prompt
    
    @staticmethod
    def get_multiple_images_prompt(images_data):
        """Generate prompt for multiple image analysis"""
        prompt = f"""
Analyze the following {len(images_data)} MRI images of the same patient and provide a comprehensive O-RADS assessment.

For each image, note the characteristics. Then synthesize findings across all images to determine:
1. Most suspicious findings
2. Consistency of features
3. Overall O-RADS score

Provide a consolidated analysis in JSON format with:
- Overall O-RADS score (1-5)
- Cancer risk percentage
- Key findings across all images
- Comprehensive recommendations
- Next steps for patient care

Make the analysis specific, actionable, and medically appropriate.
"""
        return prompt