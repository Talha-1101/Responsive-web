"""
Real AI service with Claude API integration for website analysis insights
"""

import logging
import json
import httpx
from typing import Dict, List, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for REAL AI-powered website analysis and suggestions using Claude API"""
    
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        self.base_url = "https://api.anthropic.com/v1/messages"
        
        # Check if we have a real API key
        self.is_real_ai = self.api_key and self.api_key != "mock-key-for-development"
        
        if self.is_real_ai:
            logger.info("🤖 Real Claude AI initialized and ready")
        else:
            logger.warning("🤖 AI running in mock mode - set CLAUDE_API_KEY for real AI")
    
    async def analyze_website(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive AI analysis of the website using real Claude API"""
        try:
            logger.info("🧠 Starting AI analysis...")
            
            if not self.is_real_ai:
                logger.info("🔄 Using mock AI response (no API key configured)")
                return await self._generate_mock_analysis(analysis_data)
            
            # Create comprehensive prompt for Claude
            prompt = self._build_analysis_prompt(analysis_data)
            
            # Call Claude API
            ai_response = await self._call_claude_api(prompt)
            
            # Parse and structure the response
            structured_analysis = await self._parse_ai_response(ai_response, analysis_data)
            
            logger.info("✅ Real AI analysis completed successfully")
            return structured_analysis
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            # Fallback to mock analysis if real AI fails
            logger.info("🔄 Falling back to mock analysis")
            return await self._generate_mock_analysis(analysis_data)
    
    async def get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Generate AI-powered fix suggestion for a specific issue"""
        try:
            if not self.is_real_ai:
                return self._generate_mock_fix_suggestion(issue)
            
            prompt = self._build_fix_prompt(issue)
            response = await self._call_claude_api(prompt, max_tokens=500)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Fix suggestion generation failed: {e}")
            return self._generate_mock_fix_suggestion(issue)
    
    async def _call_claude_api(self, prompt: str, max_tokens: int = None) -> str:
        """Make actual API call to Claude"""
        if not self.is_real_ai:
            raise Exception("No real API key configured")
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Claude API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["content"][0]["text"]
    
    def _build_analysis_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Build comprehensive prompt for website analysis"""
        url = analysis_data.get("url", "")
        issues = analysis_data.get("issues", [])
        seo_data = analysis_data.get("seo", {})
        platform = analysis_data.get("platform", {})
        
        prompt = f"""You are an expert web developer and UX consultant analyzing a website. Provide a comprehensive analysis.

WEBSITE: {url}
PLATFORM: {platform.get('platform', 'Unknown')} {platform.get('version', '')}

DETECTED ISSUES ({len(issues)} total):
"""
        
        for i, issue in enumerate(issues[:10], 1):  # Limit to first 10 issues
            prompt += f"{i}. {issue.get('category', 'Unknown')} - {issue.get('description', '')}\n"
        
        prompt += f"""

SEO DATA:
- Title: {seo_data.get('title', 'Not found')}
- Description: {seo_data.get('description', 'Not found')}
- H1 tags: {seo_data.get('h1_count', 0)}
- Has viewport meta: {seo_data.get('has_viewport_meta', False)}

ANALYSIS REQUIRED:
Please provide a structured JSON response with these exact keys:

{{
    "overall_assessment": "A 2-3 sentence summary of the website's quality and main issues",
    "responsiveness_feedback": "Specific feedback about responsive design and mobile compatibility",
    "accessibility_feedback": "Assessment of accessibility compliance and barriers",
    "seo_recommendations": ["List of 3-5 specific SEO improvements"],
    "performance_tips": ["List of 3-5 performance optimization suggestions"],
    "priority_fixes": ["Top 3 most critical issues to fix first"],
    "technical_debt": "Assessment of code quality and maintainability",
    "user_experience": "Analysis of UX/UI design effectiveness",
    "security_considerations": "Basic security assessment and recommendations"
}}

Focus on actionable, specific recommendations. Be direct and professional."""
        
        return prompt
    
    def _build_fix_prompt(self, issue: Dict[str, Any]) -> str:
        """Build prompt for specific issue fix suggestion"""
        return f"""You are a senior web developer. Provide a specific, actionable fix for this website issue:

ISSUE DETAILS:
- Category: {issue.get('category', 'Unknown')}
- Type: {issue.get('type', 'Unknown')}
- Severity: {issue.get('severity', 'Unknown')}
- Description: {issue.get('description', 'No description available')}
- Element: {issue.get('element_selector', 'Not specified')}

Provide a concise, actionable solution including:
1. The specific fix needed
2. Code example if applicable (HTML/CSS/JS)
3. Why this fix improves the website

Keep response under 200 words and focus on practical implementation."""
    
    async def _parse_ai_response(self, ai_response: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure AI response"""
        try:
            # Try to parse as JSON first
            if ai_response.strip().startswith('{'):
                parsed = json.loads(ai_response)
                return parsed
            
            # If not JSON, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
            
            # If no JSON found, create structured response from text
            return {
                "overall_assessment": ai_response[:200] + "...",
                "responsiveness_feedback": "AI analysis provided comprehensive feedback",
                "accessibility_feedback": "Accessibility improvements recommended",
                "seo_recommendations": ["Implement AI-suggested SEO improvements"],
                "performance_tips": ["Follow AI-recommended performance optimizations"],
                "priority_fixes": ["Address AI-identified critical issues"],
                "technical_debt": "Code quality assessment completed",
                "user_experience": "UX analysis performed",
                "security_considerations": "Basic security review completed",
                "raw_ai_response": ai_response
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            # Return fallback structure
            return await self._generate_mock_analysis(analysis_data)
    
    async def _generate_mock_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock AI analysis for development/testing when no API key"""
        url = data.get("url", "the website")
        issues = data.get("issues", [])
        seo_data = data.get("seo", {})
        platform = data.get("platform", {}).get("platform", "Unknown")
        
        # Count issues by severity
        high_issues = len([i for i in issues if i.get("severity") == "high"])
        medium_issues = len([i for i in issues if i.get("severity") == "medium"])
        total_issues = len(issues)
        
        # Generate assessment based on issues
        if total_issues == 0:
            assessment = f"This {platform} website demonstrates excellent web standards with no major issues detected. The site appears well-optimized for modern web requirements."
        elif high_issues == 0 and medium_issues <= 2:
            assessment = f"This {platform} website shows good overall quality with only minor issues detected. With small improvements, it could achieve excellent standards."
        elif high_issues <= 2:
            assessment = f"This {platform} website has room for improvement with {high_issues} high-priority and {medium_issues} medium-priority issues. Addressing these will significantly enhance user experience."
        else:
            assessment = f"This {platform} website requires attention with {high_issues} critical issues identified. Immediate action is recommended to improve accessibility and user experience."
        
        return {
            "overall_assessment": assessment,
            "responsiveness_feedback": f"The website shows {'excellent' if total_issues <= 3 else 'moderate' if total_issues <= 6 else 'poor'} responsive design implementation. {'Continue monitoring for edge cases.' if total_issues <= 3 else 'Focus on mobile-first design principles and flexible layouts.'}",
            "accessibility_feedback": f"Accessibility compliance is {'strong' if high_issues == 0 else 'moderate' if high_issues <= 2 else 'concerning'}. {'Great foundation for inclusive design.' if high_issues == 0 else 'Address accessibility barriers to ensure compliance with WCAG guidelines.'}",
            "seo_recommendations": [
                "Optimize page titles and meta descriptions for target keywords",
                "Implement structured data markup for rich snippets",
                "Improve internal linking structure and navigation",
                "Add comprehensive alt text to all images",
                "Optimize page loading speed and Core Web Vitals"
            ],
            "performance_tips": [
                "Implement lazy loading for images and videos",
                "Minify and compress CSS, JavaScript, and HTML files",
                "Use modern image formats (WebP, AVIF) for better compression",
                "Enable browser caching and CDN implementation",
                "Optimize database queries and server response times"
            ],
            "priority_fixes": [
                f"Address {high_issues} high-priority accessibility issues" if high_issues > 0 else "Maintain current high accessibility standards",
                "Implement missing viewport meta tag for mobile optimization" if not seo_data.get('has_viewport_meta') else "Optimize responsive breakpoints",
                "Improve SEO meta information and structured data" if not seo_data.get('title') else "Enhance content optimization"
            ],
            "technical_debt": f"The codebase appears to be built on {platform} with {'minimal' if total_issues <= 3 else 'moderate' if total_issues <= 6 else 'significant'} technical debt. {'Focus on maintaining current standards.' if total_issues <= 3 else 'Consider refactoring problematic areas for better maintainability.'}",
            "user_experience": f"User experience is {'excellent' if total_issues <= 2 else 'good' if total_issues <= 5 else 'needs improvement'} based on detected issues. {'Continue focusing on user-centered design.' if total_issues <= 2 else 'Prioritize fixing usability issues to improve user satisfaction.'}",
            "security_considerations": "Implement HTTPS across all pages, ensure proper content security policies, keep platform and plugins updated, and consider implementing proper authentication measures.",
            "analysis_type": "mock_analysis",
            "issue_summary": {
                "total_issues": total_issues,
                "high_priority": high_issues,
                "medium_priority": medium_issues,
                "low_priority": total_issues - high_issues - medium_issues
            }
        }
    
    def _generate_mock_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Generate mock fix suggestion based on issue type"""
        issue_type = issue.get("type", "")
        category = issue.get("category", "")
        
        # Real-looking suggestions based on issue type
        fixes = {
            "missing_alt_text": "Add descriptive alt attributes to images: `<img src='image.jpg' alt='Descriptive text about image content'>`. For decorative images, use `alt=''` to mark them as decorative.",
            "missing_viewport_meta": "Add viewport meta tag to HTML head: `<meta name='viewport' content='width=device-width, initial-scale=1.0'>` to ensure proper mobile rendering.",
            "missing_meta_description": "Add meta description: `<meta name='description' content='Compelling description in 150-160 characters'>` to improve search engine snippets.",
            "missing_title": "Add unique page title: `<title>Descriptive Page Title - Brand Name</title>` keeping it 50-60 characters for optimal SEO.",
            "missing_h1": "Add a single H1 heading that clearly describes the page content: `<h1>Main Page Heading</h1>`. Use only one H1 per page.",
            "small_touch_targets": "Increase touch target size to minimum 44x44px: `button { min-width: 44px; min-height: 44px; }` to improve mobile usability.",
            "poor_contrast": "Improve color contrast to meet WCAG AA standards (4.5:1 ratio): Use darker text or lighter backgrounds to ensure readability.",
            "horizontal_scroll": "Fix horizontal scrolling by using responsive design: `max-width: 100%; overflow-x: hidden;` and implement proper breakpoints."
        }
        
        return fixes.get(issue_type, f"To fix this {category} issue, review the {issue.get('description', 'problem')} and implement best practices for {category} compliance. Consider consulting WCAG guidelines for accessibility or modern web standards for performance improvements.")

# Global AI service instance
ai_service = AIService()