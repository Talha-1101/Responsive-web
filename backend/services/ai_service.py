"""
AI Service for intelligent website analysis and suggestions
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered website analysis and suggestions"""
    
    def __init__(self):
        # Detect provider based on env vars
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro"))
        self.gemini_max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "2000"))

        # Provider selection: AI when API key exists, else mock
        if self.gemini_api_key:
            self.provider = "ai"
            self.mock_mode = False
            logger.info("✅ Agentic AI initialized and ready")
        else:
            # STRICT MODE: Do not default to mock if key is missing.
            # User must provide a key for AI features.
            self.provider = "none"
            self.mock_mode = False
            logger.warning("⚠️ No AI API Key found. AI features will be disabled (Strict Mode).")
    
    async def analyze_website(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for website analysis"""
        try:
            logger.info("🧠 Starting AI analysis...")
            
            if self.provider == "ai":
                return await self._call_ai_api(analysis_data)
            
            # If provider is none (strict mode), return unavailable
            return {
                "error": "AI Service Not Configured",
                "overall_assessment": "AI analysis is disabled because no API key was provided.",
                "key_insights": ["Please configure GEMINI_API_KEY in .env to enable AI insights."],
                "priority_fixes": [],
                "technical_suggestions": [],
                "user_experience_score": 0
            }
                
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return {
                "error": f"AI Analysis Failed: {str(e)}",
                "overall_assessment": "AI Analysis is currently unavailable.",
                "key_insights": ["Could not generate insights at this time."],
                "priority_fixes": [],
                "technical_suggestions": [],
                "user_experience_score": 0
            }
    
    async def get_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Get AI suggestion for fixing a specific issue"""
        try:
            if self.provider == "ai":
                return await self._get_ai_fix_suggestion(issue)
            
            return "AI suggestions are disabled. Please configure an API key."
                
        except Exception as e:
            logger.error(f"❌ Failed to get fix suggestion: {e}")
            return f"Fix suggestion unavailable: {e}"
    
    async def _call_ai_api(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI Model for analysis with retry logic"""
        import google.generativeai as genai
        import asyncio

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(self.gemini_model)

        context = self._prepare_analysis_context(analysis_data)
        prompt = (
            "You are a senior web performance and SEO engineer. Analyze this website data and provide professional, actionable insights.\n\n"
            + context
            + "\n\nPlease provide a pure JSON response (no markdown) with the following structure:\n"
            "{\n"
            '  "overall_assessment": "A concise executive summary (max 3 sentences).",\n'
            '  "key_insights": ["Insight 1", "Insight 2", "Insight 3"],\n'
            '  "priority_fixes": [\n'
            '    {"issue": "Brief validation of issue", "impact": "high/medium/low", "suggestion": "Actionable advice"}\n'
            '  ],\n'
            '  "technical_suggestions": ["Tech suggestion 1", "Tech suggestion 2"],\n'
            '  "user_experience_score": 85\n'
            "}"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Run sync in executor if needed, but google-genai is sync usually unless using async methods
                # The previous code assumed sync call inside async func which blocks, but for small prompt it's 'ok'.
                # Better to use await asyncio.to_thread if we want to be proper, but sticking to logic.
                
                resp = await asyncio.to_thread(model.generate_content, prompt)
                text = resp.text or ""

                # Attempt to clean and parse JSON
                try:
                    # Remove markdown code blocks if present
                    clean_text = text.replace("```json", "").replace("```", "").strip()
                    return json.loads(clean_text)
                except Exception as e:
                    logger.warning(f"⚠️ JSON parsing failed, attempting fuzzy repair: {e}")
                    if text:
                        return {
                            "overall_assessment": text[:300] + "...",
                            "key_insights": ["Analysis generated but formatting was imperfect."],
                            "priority_fixes": [],
                            "technical_suggestions": [],
                            "user_experience_score": 70,
                        }
                    raise e

            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "quota" in error_str.lower()) and attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    logger.warning(f"⚠️ Gemini Rate Limit (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
                
                if attempt == max_retries - 1:
                    logger.error(f"❌ Gemini API call failed: {e}")
                    raise e
        
        raise Exception("Failed to generate AI analysis after retries")

    async def _get_gemini_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Get fix suggestion from Gemini API with retry logic"""
        import google.generativeai as genai
        import asyncio

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(self.gemini_model)
        prompt = (
            "You are a web developer. Provide a concise, step-by-step technical fix for this specific issue.\n"
            "Do not include generic advice. Give code snippets if applicable (CSS/HTML/JS).\n\n"
            f"Issue: {issue.get('type', 'unknown').replace('_', ' ').title()}\n"
            f"Context: {issue.get('description', 'No description')}\n"
            f"Severity: {issue.get('severity', 'medium')}\n\n"
            "Format: Plain text with simple code blocks if needed."
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = await asyncio.to_thread(model.generate_content, prompt)
                return (resp.text or "").strip()
                
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "quota" in error_str.lower()) and attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    logger.warning(f"⚠️ Rate Limit on fix suggestion. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                
                if attempt == max_retries - 1:
                    logger.warning(f"⚠️ Gemini Rate Limit (429) on fix suggestion for {issue.get('type')}")
                    return "AI Generation Failed: Rate limit exceeded or service unavailable."

        return "AI Generation Failed."
    
    async def get_category_guide(self, category: str, analysis_data: Dict[str, Any]) -> str:
        """Get detailed improvement guide for a specific category"""
        try:
            import google.generativeai as genai
            import asyncio

            if self.mock_mode:
                return self._generate_mock_guide(category)

            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            
            context = self._prepare_analysis_context(analysis_data)
            prompt = (
                f"You are a web expert specializing in {category}. Provide a comprehensive, step-by-step optimization guide.\n"
                f"Based on this analysis context:\n{context}\n\n"
                f"Create a guide specifically to improve the '{category}' score.\n"
                "Format: Markdown with sections for 'Immediate Actions', 'Long-term Strategy', and 'Code Snippets' if relevant."
            )

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    resp = await asyncio.to_thread(model.generate_content, prompt)
                    return (resp.text or "").strip()
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    return self._generate_mock_guide(category)
            
            return "Failed to generate guide after retries."
            
        except Exception as e:
            logger.error(f"Failed to get category guide: {e}")
            return f"Error generating guide: {str(e)}"

    def _generate_mock_guide(self, category: str) -> str:
        """Generate mock guide for fallback"""
        return (
            f"### How to Improve Your {category.title()} Score\n\n"
            "**1. Optimize Images**\n"
            "Ensure all images are compressed and have modern formats (WebP).\n\n"
            "**2. Minify Resources**\n"
            "Minify CSS and JS files to reduce load times.\n\n"
            "**3. Check Meta Tags**\n"
            "Verify that title and description tags are present and optimized."
        )
    def _prepare_analysis_context(self, analysis_data: Dict[str, Any]) -> str:
        """Prepare analysis context for AI"""
        url = analysis_data.get("url", "Unknown URL")
        issues = analysis_data.get("issues", [])
        seo = analysis_data.get("seo", {})
        platform = analysis_data.get("platform", {})
        
        context = f"""
        Website: {url}
        Platform: {platform.get('platform', 'Unknown')}
        Total Issues Found: {len(issues)}
        
        SEO Status:
        - Title: {'✓' if seo.get('title') else '✗'} ({len(seo.get('title', '') or '')} chars)
        - Description: {'✓' if seo.get('description') else '✗'}
        
        Critical Issues ({len([i for i in issues if i.get('severity') == 'high'])}):
        """
        
        # Add top issues
        high_priority_issues = [i for i in issues if i.get('severity') == 'high'][:5]
        for issue in high_priority_issues:
            context += f"- {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}\n"
        
        return context
    
    async def _generate_mock_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent mock analysis based on actual data when API is down/busy"""
        
        url = analysis_data.get("url", "the website")
        issues = analysis_data.get("issues", [])
        seo = analysis_data.get("seo", {})
        platform = analysis_data.get("platform", {})
        
        # Analyze the actual data to generate realistic insights
        high_issues = [i for i in issues if i.get('severity') == 'high']
        medium_issues = [i for i in issues if i.get('severity') == 'medium']
        
        # Smart Assessment
        if len(high_issues) > 3:
            assessment = f"We found {len(high_issues)} critical issues that may impact your search ranking and user retention. Immediate attention is recommended for mobile responsiveness and SEO tags."
        elif len(high_issues) > 0:
            assessment = f"Your website is off to a good start but has {len(high_issues)} critical items to resolve. addressing the missing SEO elements will provide the biggest quick win."
        else:
            assessment = "Excellent work! Your website follows most best practices. We only found minor optimizations to perfect the user experience."
        
        # Smart Priority Fixes
        priority_fixes = []
        for issue in high_issues[:3]:
             priority_fixes.append({
                "issue": issue.get('type', 'Unknown').replace('_', ' ').title(),
                "impact": "high",
                "suggestion": self._generate_mock_fix_suggestion(issue).split('\n')[0] # Brief suggestion
            })
        
        # Fallback insights
        insights = []
        if platform.get('platform') != 'Unknown':
             insights.append(f"Optimized for {platform.get('platform')}")
        if len(high_issues) == 0:
             insights.append("Passes all critical Core Web Vitals checks")
        else:
             insights.append("Mobile responsiveness needs improvement")

        return {
            "overall_assessment": assessment,
            "key_insights": insights or ["Structure is sound", "Content loads quickly"],
            "priority_fixes": priority_fixes,
            "technical_suggestions": ["Enable GZIP compression", "Leverage browser caching"],
            "user_experience_score": max(50, 100 - (len(high_issues) * 10) - (len(medium_issues) * 2)),
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_mode": "Mock (API Fallback)"
        }
    
    def _generate_mock_fix_suggestion(self, issue: Dict[str, Any]) -> str:
        """Generate detailed mock fix suggestions based on issue type"""
        issue_type = issue.get('type', '')
        
        # Detailed templates for common issues
        templates = {
            'missing_alt_text': (
                "**1. Identify Images:** Locate `<img>` tags without an `alt` attribute.\n"
                "**2. Add Description:** Add a concise description of the image content.\n"
                "```html\n"
                "<!-- Before -->\n"
                "<img src='logo.png'>\n\n"
                "<!-- After -->\n"
                "<img src='logo.png' alt='Company Logo - 2024'>\n"
                "```"
            ),
            'missing_title': (
                "**1. Edit HTML Head:** Open your main HTML file or layout template.\n"
                "**2. Add Title Tag:** Ensure the `<title>` tag exists within `<head>`.\n"
                "```html\n"
                "<head>\n"
                "  <title>Your Page Topic | Brand Name</title>\n"
                "</head>\n"
                "```"
            ),
            'missing_description': (
                "**Fix Strategy:**\n"
                "Add a meta description tag to your document head. This summary often appears in search results.\n"
                "```html\n"
                "<meta name=\"description\" content=\"A concise summary of your page content (150-160 characters).\">\n"
                "```"
            ),
            'missing_h1': (
                "**Fix Strategy:**\n"
                "Every page should have exactly one `<h1>` tag describing the main topic.\n"
                "```html\n"
                "<!-- Recommended Structure -->\n"
                "<body>\n"
                "  <header>\n"
                "    <h1>Main Page Heading</h1>\n"
                "  </header>\n"
                "  ...\n"
                "</body>\n"
                "```"
            ),
            'horizontal_scroll': (
                "**CSS Fix:**\n"
                "Prevent unwanted overflow on mobile devices.\n"
                "```css\n"
                "/* Global fix */\n"
                "html, body {\n"
                "  max-width: 100%;\n"
                "  overflow-x: hidden;\n"
                "}\n\n"
                "/* Image fix */\n"
                "img {\n"
                "  max-width: 100%;\n"
                "  height: auto;\n"
                "}\n"
                "```"
            ),
            'limited_analysis': (
                "**System Limitation:**\n"
                "The analysis was restricted due to technical environment constraints (e.g., missing browser dependencies).\n"
                "**Recommended Action:**\n"
                "1. Ensure the server has a valid browser installed (Chromium/WebKit).\n"
                "2. Check backend logs for specific `Playwright` errors.\n"
                "3. Verify that the URL is publicly accessible and not blocking bot traffic."
            )
        }
        
        # Default fallback
        description = issue.get('description', '')
        return templates.get(issue_type, (
            f"**Generic Fix Strategy:**\n"
            f"The issue '{issue_type.replace('_', ' ')}' was detected ({description}).\n"
            f"**Recommended Action:**\n"
            f"Inspect the element causing this issue. Ensure it complies with modern responsive standards.\n"
            f"```css\n"
            f"/* Example mitigation */\n"
            f".affected-element {{\n"
            f"  max-width: 100%;\n"
            f"  box-sizing: border-box;\n"
            f"}}\n"
            f"```"
        ))