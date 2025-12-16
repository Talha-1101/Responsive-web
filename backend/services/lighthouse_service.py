"""
Lighthouse service for performance, accessibility, and SEO auditing
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import settings

logger = logging.getLogger(__name__)

class LighthouseService:
    """Service for running Lighthouse audits"""
    
    def __init__(self):
        self.lighthouse_available = self._check_lighthouse_availability()
    
    def _check_lighthouse_availability(self) -> bool:
        """Check if Lighthouse is available in the system"""
        try:
            result = subprocess.run(
                ["lighthouse", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Lighthouse available: {result.stdout.strip()}")
                return True
            else:
                logger.warning("Lighthouse not found in system")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Lighthouse not available - will use mock data")
            return False
    
    async def audit_performance(self, url: str) -> Dict[str, Any]:
        """Run comprehensive Lighthouse audit"""
        try:
            logger.info(f"Starting Lighthouse audit for: {url}")
            
            if not self.lighthouse_available:
                logger.info("Using mock Lighthouse data")
                return await self._generate_mock_audit(url)
            
            # Run actual Lighthouse audit
            audit_result = await self._run_lighthouse_audit(url)
            
            if audit_result:
                # Process results
                processed_results = await self._process_lighthouse_results(audit_result)
                return processed_results
            else:
                # Fallback to mock data
                return await self._generate_mock_audit(url)
                
        except Exception as e:
            logger.error(f"Lighthouse audit failed: {e}")
            return {
                "data": {
                    "lighthouse_scores": {},
                    "error": str(e)
                },
                "issues": [{
                    "category": "performance",
                    "type": "lighthouse_audit_error",
                    "severity": "low",
                    "description": f"Performance audit failed: {e}"
                }]
            }
    
    async def _run_lighthouse_audit(self, url: str) -> Optional[Dict]:
        """Run actual Lighthouse audit using subprocess"""
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                output_path = tmp_file.name
            
            # Lighthouse command
            cmd = [
                "lighthouse",
                url,
                "--output=json",
                f"--output-path={output_path}",
                "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage",
                "--quiet",
                "--max-wait-for-load=30000",
                "--timeout=60000"
            ]
            
            # Run Lighthouse
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            
            if process.returncode == 0:
                # Read results
                with open(output_path, 'r') as f:
                    results = json.load(f)
                
                # Clean up temp file
                Path(output_path).unlink(missing_ok=True)
                
                return results
            else:
                logger.error(f"Lighthouse failed: {stderr.decode()}")
                return None
                
        except asyncio.TimeoutError:
            logger.error("Lighthouse audit timed out")
            return None
        except Exception as e:
            logger.error(f"Error running Lighthouse: {e}")
            return None
    
    async def _process_lighthouse_results(self, lighthouse_data: Dict) -> Dict[str, Any]:
        """Process raw Lighthouse results into our format"""
        try:
            # Extract scores
            categories = lighthouse_data.get("categories", {})
            scores = {}
            
            if "performance" in categories:
                scores["performance"] = round(categories["performance"]["score"] * 100, 1)
            if "accessibility" in categories:
                scores["accessibility"] = round(categories["accessibility"]["score"] * 100, 1)
            if "seo" in categories:
                scores["seo"] = round(categories["seo"]["score"] * 100, 1)
            if "best-practices" in categories:
                scores["best_practices"] = round(categories["best-practices"]["score"] * 100, 1)
            
            # Extract metrics
            audits = lighthouse_data.get("audits", {})
            metrics = {}
            
            # Core Web Vitals and other metrics
            metric_mapping = {
                "first-contentful-paint": "first_contentful_paint",
                "largest-contentful-paint": "largest_contentful_paint",
                "cumulative-layout-shift": "cumulative_layout_shift",
                "total-blocking-time": "total_blocking_time",
                "speed-index": "speed_index",
                "interactive": "time_to_interactive"
            }
            
            for audit_key, metric_key in metric_mapping.items():
                if audit_key in audits and audits[audit_key].get("numericValue") is not None:
                    value = audits[audit_key]["numericValue"]
                    # Convert to seconds if in milliseconds
                    if audit_key in ["first-contentful-paint", "largest-contentful-paint", "speed-index", "interactive", "total-blocking-time"]:
                        value = value / 1000
                    metrics[metric_key] = round(value, 2)
            
            # Extract opportunities (performance improvements)
            opportunities = []
            for audit_key, audit_data in audits.items():
                if (audit_data.get("scoreDisplayMode") == "numeric" and
                    audit_data.get("score", 0) < 0.9 and
                    audit_data.get("details", {}).get("overallSavingsMs", 0) > 500):
                    
                    opportunities.append({
                        "audit": audit_key,
                        "title": audit_data.get("title", ""),
                        "description": audit_data.get("description", ""),
                        "savings_ms": audit_data.get("details", {}).get("overallSavingsMs", 0)
                    })
            
            # Generate issues based on poor scores and failed audits
            issues = []
            
            # Performance issues
            if scores.get("performance", 0) < 50:
                issues.append({
                    "category": "performance",
                    "type": "poor_performance_score",
                    "severity": "high",
                    "description": f"Poor performance score ({scores.get('performance', 0)}). Users may experience slow loading times"
                })
            elif scores.get("performance", 0) < 75:
                issues.append({
                    "category": "performance",
                    "type": "moderate_performance_score",
                    "severity": "medium",
                    "description": f"Moderate performance score ({scores.get('performance', 0)}). There's room for improvement"
                })
            
            # Accessibility issues
            if scores.get("accessibility", 0) < 75:
                issues.append({
                    "category": "accessibility",
                    "type": "poor_accessibility_score",
                    "severity": "high",
                    "description": f"Poor accessibility score ({scores.get('accessibility', 0)}). May not meet WCAG guidelines"
                })
            
            # SEO issues
            if scores.get("seo", 0) < 75:
                issues.append({
                    "category": "seo",
                    "type": "poor_seo_score",
                    "severity": "medium",
                    "description": f"Poor SEO score ({scores.get('seo', 0)}). May affect search engine visibility"
                })
            
            # Core Web Vitals issues
            if metrics.get("largest_contentful_paint", 0) > 2.5:
                issues.append({
                    "category": "performance",
                    "type": "poor_lcp",
                    "severity": "high",
                    "description": f"Largest Contentful Paint is {metrics.get('largest_contentful_paint')}s (should be ≤2.5s)"
                })
            
            if metrics.get("cumulative_layout_shift", 0) > 0.1:
                issues.append({
                    "category": "performance",
                    "type": "poor_cls",
                    "severity": "medium",
                    "description": f"Cumulative Layout Shift is {metrics.get('cumulative_layout_shift')} (should be ≤0.1)"
                })
            
            # Add top opportunities as issues
            for opp in opportunities[:3]:  # Top 3 opportunities
                issues.append({
                    "category": "performance",
                    "type": "performance_opportunity",
                    "severity": "medium",
                    "description": f"Opportunity: {opp['title']} (potential savings: {opp['savings_ms']}ms)",
                    "suggestion": opp["description"]
                })
            
            data = {
                "lighthouse_scores": scores,
                "metrics": metrics,
                "opportunities": opportunities[:5],  # Top 5 opportunities
                "audit_url": lighthouse_data.get("finalUrl", ""),
                "fetch_time": lighthouse_data.get("fetchTime", ""),
                "user_agent": lighthouse_data.get("userAgent", "")
            }
            
            return {"data": data, "issues": issues}
            
        except Exception as e:
            logger.error(f"Error processing Lighthouse results: {e}")
            return {
                "data": {"error": f"Failed to process Lighthouse results: {e}"},
                "issues": []
            }
    
    async def _generate_mock_audit(self, url: str) -> Dict[str, Any]:
        """Generate mock Lighthouse audit data for development"""
        import random
        
        # Generate realistic mock scores
        base_performance = random.randint(65, 95)
        base_accessibility = random.randint(80, 98)
        base_seo = random.randint(75, 95)
        base_best_practices = random.randint(85, 100)
        
        scores = {
            "performance": base_performance,
            "accessibility": base_accessibility,
            "seo": base_seo,
            "best_practices": base_best_practices
        }
        
        # Generate mock metrics
        metrics = {
            "first_contentful_paint": round(random.uniform(1.2, 3.5), 2),
            "largest_contentful_paint": round(random.uniform(2.1, 4.8), 2),
            "cumulative_layout_shift": round(random.uniform(0.05, 0.25), 3),
            "total_blocking_time": round(random.uniform(50, 300), 0),
            "speed_index": round(random.uniform(2.8, 6.2), 2),
            "time_to_interactive": round(random.uniform(3.1, 7.5), 2)
        }
        
        # Generate mock opportunities
        opportunities = [
            {
                "audit": "unused-css-rules",
                "title": "Remove unused CSS",
                "description": "Remove dead rules from stylesheets to reduce unnecessary bytes consumed by network activity",
                "savings_ms": random.randint(200, 800)
            },
            {
                "audit": "render-blocking-resources",
                "title": "Eliminate render-blocking resources",
                "description": "Resources are blocking the first paint of your page. Consider delivering critical JS/CSS inline",
                "savings_ms": random.randint(300, 600)
            },
            {
                "audit": "unused-javascript",
                "title": "Remove unused JavaScript",
                "description": "Remove unused JavaScript to reduce bytes consumed by network activity",
                "savings_ms": random.randint(400, 1200)
            }
        ]
        
        # Generate issues based on scores
        issues = []
        
        if scores["performance"] < 70:
            issues.append({
                "category": "performance",
                "type": "poor_performance_score",
                "severity": "high",
                "description": f"Performance score is {scores['performance']}/100. Users may experience slow loading times"
            })
        
        if scores["accessibility"] < 85:
            issues.append({
                "category": "accessibility",
                "type": "accessibility_improvements_needed",
                "severity": "medium",
                "description": f"Accessibility score is {scores['accessibility']}/100. Consider improving for better inclusivity"
            })
        
        if metrics["largest_contentful_paint"] > 2.5:
            issues.append({
                "category": "performance",
                "type": "poor_lcp",
                "severity": "high",
                "description": f"Largest Contentful Paint is {metrics['largest_contentful_paint']}s (should be ≤2.5s for good user experience)"
            })
        
        if metrics["cumulative_layout_shift"] > 0.1:
            issues.append({
                "category": "performance",
                "type": "layout_shift_issues",
                "severity": "medium",
                "description": f"Cumulative Layout Shift is {metrics['cumulative_layout_shift']} (should be ≤0.1 to avoid visual instability)"
            })
        
        # Add opportunity-based issues
        for opp in opportunities:
            if opp["savings_ms"] > 500:
                issues.append({
                    "category": "performance",
                    "type": "performance_opportunity",
                    "severity": "medium",
                    "description": f"{opp['title']} - potential time savings: {opp['savings_ms']}ms",
                    "suggestion": opp["description"]
                })
        
        data = {
            "lighthouse_scores": scores,
            "metrics": metrics,
            "opportunities": opportunities,
            "audit_url": url,
            "fetch_time": "2025-01-01T12:00:00.000Z",
            "user_agent": "Mozilla/5.0 (Lighthouse Mock Data)",
            "note": "This is mock data for development - real Lighthouse integration requires Node.js setup"
        }
        
        logger.info(f"Generated mock Lighthouse audit: Performance {scores['performance']}, Accessibility {scores['accessibility']}")
        
        return {"data": data, "issues": issues}