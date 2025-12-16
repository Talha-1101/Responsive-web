"""
Real Website Analyzer - Complete Implementation
This replaces the mock analyzer with actual website testing
Place this file at: services/website_analyzer.py
"""

import asyncio
import logging
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
import httpx

from config import settings

logger = logging.getLogger(__name__)

class RealWebsiteAnalyzer:
    """Complete website analyzer that performs actual testing"""
    
    def __init__(self):
        self.session_id = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.viewport_results = []
        self.all_issues = []
        
    async def analyze_website(self, url: str, session_id: str = None) -> Dict[str, Any]:
        """Perform comprehensive real website analysis"""
        self.session_id = session_id
        start_time = datetime.now()
        
        try:
            logger.info(f"🔍 Starting REAL analysis for: {url}")
            
            # Initialize browser
            await self._setup_browser()
            
            # Load the website
            await self._load_website(url)
            
            # Run all analyses in parallel where possible
            results = await self._run_comprehensive_analysis(url)
            
            # Calculate final scores
            results["scores"] = self._calculate_scores(results)
            
            # Add metadata
            results.update({
                "url": url,
                "session_id": session_id,
                "timestamp": start_time.isoformat(),
                "analysis_duration": (datetime.now() - start_time).total_seconds(),
                "analysis_type": "real_analysis"
            })
            
            logger.info(f"✅ Real analysis completed for: {url}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _setup_browser(self):
        """Initialize Playwright browser with optimal settings"""
        playwright = await async_playwright().start()
        
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9'
            }
        )
        
        self.page = await self.context.new_page()
        
        # Set reasonable timeouts
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
    
    async def _load_website(self, url: str):
        """Load the website and wait for it to be ready"""
        try:
            logger.info(f"🌐 Loading website: {url}")
            
            # Navigate to the website
            response = await self.page.goto(url, wait_until='networkidle')
            
            if not response or response.status >= 400:
                raise Exception(f"Failed to load website. Status: {response.status if response else 'No response'}")
            
            # Wait for page to be interactive
            await self.page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Allow dynamic content to load
            
            logger.info("✅ Website loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load website: {e}")
            raise
    
    async def _run_comprehensive_analysis(self, url: str) -> Dict[str, Any]:
        """Run all analysis components"""
        results = {}
        
        # 1. Responsive Design Testing
        logger.info("📱 Testing responsive design...")
        results["viewports"] = await self._test_responsive_design()
        
        # 2. SEO Analysis  
        logger.info("🔍 Analyzing SEO...")
        results["seo"] = await self._analyze_seo()
        
        # 3. Accessibility Testing
        logger.info("♿ Testing accessibility...")
        results["accessibility"] = await self._test_accessibility()
        
        # 4. Performance Analysis
        logger.info("⚡ Analyzing performance...")
        results["performance"] = await self._analyze_performance()
        
        # 5. Form Testing
        logger.info("📝 Testing forms...")
        results["forms"] = await self._test_forms()
        
        # 6. Platform Detection
        logger.info("🔧 Detecting platform...")
        results["platform"] = await self._detect_platform()
        
        # 7. Image Analysis
        logger.info("🖼️ Analyzing images...")
        results["images"] = await self._analyze_images()
        
        # 8. Link Analysis
        logger.info("🔗 Analyzing links...")
        results["links"] = await self._analyze_links(url)
        
        # Compile all issues
        results["issues"] = self.all_issues
        
        return results
    
    async def _test_responsive_design(self) -> List[Dict[str, Any]]:
        """Test website across different viewport sizes"""
        viewport_configs = [
            {"name": "Mobile Small", "width": 320, "height": 568},
            {"name": "Mobile Medium", "width": 375, "height": 667},
            {"name": "Mobile Large", "width": 425, "height": 812},
            {"name": "Tablet", "width": 768, "height": 1024},
            {"name": "Tablet Landscape", "width": 1024, "height": 768},
            {"name": "Desktop", "width": 1440, "height": 900},
            {"name": "Desktop Large", "width": 2560, "height": 1440},
        ]
        
        viewport_results = []
        
        for viewport in viewport_configs:
            try:
                logger.info(f"📱 Testing {viewport['name']} ({viewport['width']}x{viewport['height']})")
                
                # Set viewport size
                await self.page.set_viewport_size(
                    width=viewport['width'], 
                    height=viewport['height']
                )
                
                # Wait for layout adjustment
                await asyncio.sleep(1)
                
                # Take screenshot
                screenshot = await self.page.screenshot(
                    full_page=True,
                    type='png'
                )
                
                # Convert to base64 for storage
                screenshot_b64 = base64.b64encode(screenshot).decode()
                
                # Check for responsive issues
                issues = await self._check_viewport_issues(viewport)
                
                result = {
                    "name": viewport['name'],
                    "width": viewport['width'],
                    "height": viewport['height'],
                    "screenshot_data": screenshot_b64,
                    "screenshot_captured": True,
                    "issues": issues,
                    "responsive_score": self._calculate_viewport_score(issues)
                }
                
                viewport_results.append(result)
                self.all_issues.extend(issues)
                
            except Exception as e:
                logger.error(f"❌ Failed to test {viewport['name']}: {e}")
                viewport_results.append({
                    "name": viewport['name'],
                    "width": viewport['width'],
                    "height": viewport['height'],
                    "error": str(e),
                    "screenshot_captured": False,
                    "issues": []
                })
        
        return viewport_results
    
    async def _check_viewport_issues(self, viewport: Dict) -> List[Dict[str, Any]]:
        """Check for issues in current viewport"""
        issues = []
        
        try:
            # Check for horizontal scroll
            scroll_width = await self.page.evaluate("document.documentElement.scrollWidth")
            client_width = await self.page.evaluate("document.documentElement.clientWidth")
            
            if scroll_width > client_width + 5:  # 5px tolerance
                issues.append({
                    "category": "layout",
                    "type": "horizontal_scroll",
                    "severity": "high",
                    "description": f"Horizontal scrollbar detected in {viewport['name']} viewport",
                    "viewport": viewport['name']
                })
            
            # Check for small touch targets (mobile only)
            if viewport['width'] <= 768:
                small_targets = await self.page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('button, a, input[type="submit"], input[type="button"]');
                        const smallTargets = [];
                        
                        elements.forEach(el => {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0 && 
                                (rect.width < 44 || rect.height < 44)) {
                                smallTargets.push({
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    text: el.textContent?.trim().substring(0, 30) || ''
                                });
                            }
                        });
                        
                        return smallTargets;
                    }
                """)
                
                if small_targets and len(small_targets) > 0:
                    issues.append({
                        "category": "accessibility",
                        "type": "small_touch_targets",
                        "severity": "medium",
                        "description": f"Found {len(small_targets)} touch targets smaller than 44x44px",
                        "viewport": viewport['name'],
                        "count": len(small_targets)
                    })
            
            # Check for text overflow
            overflow_elements = await self.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    let overflowCount = 0;
                    
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        if (style.overflow === 'visible' && el.scrollWidth > el.clientWidth) {
                            overflowCount++;
                        }
                    });
                    
                    return overflowCount;
                }
            """)
            
            if overflow_elements > 5:  # Threshold for significant overflow
                issues.append({
                    "category": "layout",
                    "type": "content_overflow",
                    "severity": "medium",
                    "description": f"Multiple elements have content overflow in {viewport['name']}",
                    "viewport": viewport['name'],
                    "count": overflow_elements
                })
        
        except Exception as e:
            logger.error(f"Error checking viewport issues: {e}")
        
        return issues
    
    async def _analyze_seo(self) -> Dict[str, Any]:
        """Analyze SEO elements"""
        try:
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            seo_data = {}
            
            # Title analysis
            title_tag = soup.find('title')
            if title_tag and title_tag.string:
                title = title_tag.string.strip()
                seo_data['title'] = title
                seo_data['title_length'] = len(title)
                
                if len(title) < 30:
                    self.all_issues.append({
                        "category": "seo",
                        "type": "title_too_short",
                        "severity": "medium",
                        "description": f"Title is too short ({len(title)} chars). Recommended: 30-60 characters"
                    })
                elif len(title) > 60:
                    self.all_issues.append({
                        "category": "seo",
                        "type": "title_too_long",
                        "severity": "medium",
                        "description": f"Title is too long ({len(title)} chars). May be truncated in search results"
                    })
            else:
                seo_data['title'] = None
                seo_data['title_length'] = 0
                self.all_issues.append({
                    "category": "seo",
                    "type": "missing_title",
                    "severity": "high",
                    "description": "Missing page title. Essential for SEO"
                })
            
            # Meta description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                description = desc_tag.get('content').strip()
                seo_data['description'] = description
                seo_data['description_length'] = len(description)
                
                if len(description) < 120:
                    self.all_issues.append({
                        "category": "seo",
                        "type": "description_too_short",
                        "severity": "medium",
                        "description": f"Meta description too short ({len(description)} chars). Recommended: 120-160 characters"
                    })
                elif len(description) > 160:
                    self.all_issues.append({
                        "category": "seo",
                        "type": "description_too_long",
                        "severity": "medium",
                        "description": f"Meta description too long ({len(description)} chars). May be truncated"
                    })
            else:
                seo_data['description'] = None
                seo_data['description_length'] = 0
                self.all_issues.append({
                    "category": "seo",
                    "type": "missing_description",
                    "severity": "high",
                    "description": "Missing meta description. Important for search snippets"
                })
            
            # Heading analysis
            h1_tags = soup.find_all('h1')
            seo_data['h1_count'] = len(h1_tags)
            seo_data['h1_tags'] = [tag.get_text().strip() for tag in h1_tags]
            
            if len(h1_tags) == 0:
                self.all_issues.append({
                    "category": "seo",
                    "type": "missing_h1",
                    "severity": "medium",
                    "description": "Missing H1 tag. Important for page structure"
                })
            elif len(h1_tags) > 1:
                self.all_issues.append({
                    "category": "seo",
                    "type": "multiple_h1",
                    "severity": "medium",
                    "description": f"Multiple H1 tags found ({len(h1_tags)}). Should have only one"
                })
            
            # Meta tags
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            seo_data['has_viewport_meta'] = viewport_meta is not None
            
            if not viewport_meta:
                self.all_issues.append({
                    "category": "seo",
                    "type": "missing_viewport_meta",
                    "severity": "high",
                    "description": "Missing viewport meta tag. Essential for mobile SEO"
                })
            
            # Language attribute
            html_tag = soup.find('html')
            seo_data['has_lang_attribute'] = html_tag and html_tag.get('lang') is not None
            
            if not seo_data['has_lang_attribute']:
                self.all_issues.append({
                    "category": "seo",
                    "type": "missing_lang_attribute",
                    "severity": "medium",
                    "description": "Missing lang attribute on HTML tag"
                })
            
            return seo_data
            
        except Exception as e:
            logger.error(f"SEO analysis error: {e}")
            return {"error": str(e)}
    
    async def _test_accessibility(self) -> Dict[str, Any]:
        """Test accessibility compliance"""
        try:
            # Check for images without alt text
            images_without_alt = await self.page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    const withoutAlt = [];
                    
                    images.forEach((img, index) => {
                        if (!img.alt || img.alt.trim() === '') {
                            withoutAlt.push({
                                src: img.src.substring(0, 100),
                                index: index
                            });
                        }
                    });
                    
                    return {
                        total: images.length,
                        withoutAlt: withoutAlt
                    };
                }
            """)
            
            if images_without_alt['withoutAlt']:
                self.all_issues.append({
                    "category": "accessibility",
                    "type": "missing_alt_text",
                    "severity": "high",
                    "description": f"Found {len(images_without_alt['withoutAlt'])} images without alt text",
                    "count": len(images_without_alt['withoutAlt'])
                })
            
            # Check for form labels
            form_issues = await self.page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
                    const unlabeled = [];
                    
                    inputs.forEach((input, index) => {
                        const id = input.id;
                        const hasLabel = id && document.querySelector(`label[for="${id}"]`);
                        const hasAriaLabel = input.getAttribute('aria-label');
                        
                        if (!hasLabel && !hasAriaLabel) {
                            unlabeled.push(index);
                        }
                    });
                    
                    return {
                        totalInputs: inputs.length,
                        unlabeled: unlabeled.length
                    };
                }
            """)
            
            if form_issues['unlabeled'] > 0:
                self.all_issues.append({
                    "category": "accessibility",
                    "type": "unlabeled_form_fields",
                    "severity": "high",
                    "description": f"Found {form_issues['unlabeled']} form fields without proper labels",
                    "count": form_issues['unlabeled']
                })
            
            # Color contrast check (basic)
            contrast_issues = await self.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, a, button');
                    let lowContrastCount = 0;
                    
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                        const color = style.color;
                        const backgroundColor = style.backgroundColor;
                        
                        // Basic check - more sophisticated contrast checking would require color parsing
                        if (color && backgroundColor && 
                            color !== 'rgba(0, 0, 0, 0)' && 
                            backgroundColor !== 'rgba(0, 0, 0, 0)') {
                            // Simplified contrast check
                            if (color.includes('rgb(128') || color.includes('rgb(169')) {
                                lowContrastCount++;
                            }
                        }
                    });
                    
                    return lowContrastCount;
                }
            """)
            
            if contrast_issues > 5:
                self.all_issues.append({
                    "category": "accessibility",
                    "type": "poor_contrast",
                    "severity": "medium",
                    "description": f"Potential color contrast issues detected ({contrast_issues} elements)",
                    "count": contrast_issues
                })
            
            return {
                "images_total": images_without_alt['total'],
                "images_without_alt": len(images_without_alt['withoutAlt']),
                "form_inputs_total": form_issues['totalInputs'],
                "unlabeled_inputs": form_issues['unlabeled'],
                "potential_contrast_issues": contrast_issues
            }
            
        except Exception as e:
            logger.error(f"Accessibility analysis error: {e}")
            return {"error": str(e)}
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze basic performance metrics"""
        try:
            # Measure page load timing
            timing = await self.page.evaluate("""
                () => {
                    const timing = performance.timing;
                    const navigation = performance.getEntriesByType('navigation')[0];
                    
                    return {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        firstPaint: navigation ? navigation.domContentLoadedEventEnd : null,
                        resourceCount: performance.getEntriesByType('resource').length
                    };
                }
            """)
            
            # Check for large images
            large_images = await self.page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    const largeImages = [];
                    
                    images.forEach(img => {
                        const rect = img.getBoundingClientRect();
                        if (rect.width > 1000 || rect.height > 1000) {
                            largeImages.push({
                                src: img.src.substring(0, 100),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            });
                        }
                    });
                    
                    return largeImages;
                }
            """)
            
            if len(large_images) > 0:
                self.all_issues.append({
                    "category": "performance",
                    "type": "large_images",
                    "severity": "medium",
                    "description": f"Found {len(large_images)} large images that may slow loading",
                    "count": len(large_images)
                })
            
            # Check for external resources
            external_resources = await self.page.evaluate("""
                () => {
                    const resources = performance.getEntriesByType('resource');
                    const external = resources.filter(r => 
                        !r.name.includes(location.hostname) && 
                        (r.initiatorType === 'script' || r.initiatorType === 'css')
                    );
                    return external.length;
                }
            """)
            
            if external_resources > 10:
                self.all_issues.append({
                    "category": "performance",
                    "type": "many_external_resources",
                    "severity": "low",
                    "description": f"Many external resources ({external_resources}) may impact loading speed"
                })
            
            return {
                "dom_content_loaded": timing['domContentLoaded'],
                "load_complete": timing['loadComplete'],
                "resource_count": timing['resourceCount'],
                "large_images_count": len(large_images),
                "external_resources": external_resources
            }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {"error": str(e)}
    
    async def _test_forms(self) -> Dict[str, Any]:
        """Test forms on the page"""
        try:
            forms_data = await self.page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    const formsInfo = [];
                    
                    forms.forEach((form, index) => {
                        const inputs = form.querySelectorAll('input, select, textarea');
                        const submitButtons = form.querySelectorAll('input[type="submit"], button[type="submit"], button:not([type])');
                        
                        formsInfo.push({
                            index: index,
                            action: form.action || '',
                            method: form.method || 'GET',
                            inputCount: inputs.length,
                            hasSubmitButton: submitButtons.length > 0,
                            id: form.id || '',
                            className: form.className || ''
                        });
                    });
                    
                    return formsInfo;
                }
            """)
            
            # Check for forms without submit buttons
            forms_without_submit = [f for f in forms_data if not f['hasSubmitButton']]
            if forms_without_submit:
                self.all_issues.append({
                    "category": "forms",
                    "type": "missing_submit_button",
                    "severity": "medium",
                    "description": f"Found {len(forms_without_submit)} forms without submit buttons"
                })
            
            # Check for forms using GET with sensitive data
            insecure_forms = [f for f in forms_data if f['method'].upper() == 'GET' and f['inputCount'] > 2]
            if insecure_forms:
                self.all_issues.append({
                    "category": "forms",
                    "type": "insecure_form_method",
                    "severity": "medium",
                    "description": f"Found {len(insecure_forms)} forms using GET method for multiple inputs"
                })
            
            return {
                "forms_found": len(forms_data),
                "forms_with_submit": len([f for f in forms_data if f['hasSubmitButton']]),
                "forms_data": forms_data
            }
            
        except Exception as e:
            logger.error(f"Form analysis error: {e}")
            return {"error": str(e)}
    
    async def _detect_platform(self) -> Dict[str, Any]:
        """Detect CMS and technology platform"""
        try:
            content = await self.page.content()
            
            # Platform detection patterns
            platforms = {
                "WordPress": ["/wp-content/", "/wp-includes/", "wp-json", "WordPress"],
                "Shopify": ["cdn.shopify.com", "Shopify.theme", "shopify-section"],
                "React": ["react", "__REACT_DEVTOOLS_GLOBAL_HOOK__", "data-reactroot"],
                "Vue": ["vue.js", "__VUE__", "v-"],
                "Angular": ["angular", "ng-", "_ngcontent"],
                "Webflow": ["webflow.com", "data-wf-"],
                "Wix": ["wix.com", "_wixCIDX"],
                "Squarespace": ["squarespace.com", "sqs-block"]
            }
            
            detected_platforms = {}
            
            for platform, patterns in platforms.items():
                confidence = 0
                indicators = []
                
                for pattern in patterns:
                    if pattern.lower() in content.lower():
                        confidence += 0.3
                        indicators.append(pattern)
                
                if confidence > 0:
                    detected_platforms[platform] = {
                        "confidence": min(confidence, 1.0),
                        "indicators": indicators
                    }
            
            # Get the platform with highest confidence
            if detected_platforms:
                best_platform = max(detected_platforms.items(), key=lambda x: x[1]["confidence"])
                return {
                    "platform": best_platform[0],
                    "confidence": best_platform[1]["confidence"],
                    "indicators": best_platform[1]["indicators"],
                    "all_detections": detected_platforms
                }
            else:
                return {
                    "platform": "Unknown",
                    "confidence": 0.0,
                    "indicators": []
                }
                
        except Exception as e:
            logger.error(f"Platform detection error: {e}")
            return {"platform": "Unknown", "error": str(e)}
    
    async def _analyze_images(self) -> Dict[str, Any]:
        """Analyze images on the page"""
        try:
            images_data = await self.page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    const imageInfo = {
                        total: images.length,
                        withAlt: 0,
                        withoutAlt: 0,
                        lazy: 0,
                        large: 0
                    };
                    
                    images.forEach(img => {
                        // Alt text check
                        if (img.alt && img.alt.trim() !== '') {
                            imageInfo.withAlt++;
                        } else {
                            imageInfo.withoutAlt++;
                        }
                        
                        // Lazy loading check
                        if (img.loading === 'lazy' || img.getAttribute('data-src')) {
                            imageInfo.lazy++;
                        }
                        
                        // Size check
                        const rect = img.getBoundingClientRect();
                        if (rect.width > 800 || rect.height > 600) {
                            imageInfo.large++;
                        }
                    });
                    
                    return imageInfo;
                }
            """)
            
            return images_data
            
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {"error": str(e)}
    
    async def _analyze_links(self, base_url: str) -> Dict[str, Any]:
        """Analyze links on the page"""
        try:
            links_data = await self.page.evaluate("""
                (baseUrl) => {
                    const links = document.querySelectorAll('a[href]');
                    const linkInfo = {
                        total: links.length,
                        internal: 0,
                        external: 0,
                        empty: 0,
                        nofollow: 0
                    };
                    
                    const baseDomain = new URL(baseUrl).hostname;
                    
                    links.forEach(link => {
                        const href = link.href;
                        
                        if (!href || href === '#' || href.startsWith('javascript:')) {
                            linkInfo.empty++;
                            return;
                        }
                        
                        try {
                            const linkUrl = new URL(href);
                            if (linkUrl.hostname === baseDomain) {
                                linkInfo.internal++;
                            } else {
                                linkInfo.external++;
                            }
                        } catch {
                            linkInfo.internal++; // Assume relative URLs are internal
                        }
                        
                        // Check for nofollow
                        if (link.rel && link.rel.includes('nofollow')) {
                            linkInfo.nofollow++;
                        }
                    });
                    
                    return linkInfo;
                }
            """, base_url)
            
            if links_data['empty'] > 5:
                self.all_issues.append({
                    "category": "seo",
                    "type": "empty_links",
                    "severity": "low",
                    "description": f"Found {links_data['empty']} empty or placeholder links"
                })
            
            return links_data
            
        except Exception as e:
            logger.error(f"Link analysis error: {e}")
            return {"error": str(e)}
    
    def _calculate_viewport_score(self, issues: List[Dict]) -> int:
        """Calculate score for a specific viewport"""
        base_score = 100
        
        for issue in issues:
            if issue['severity'] == 'high':
                base_score -= 20
            elif issue['severity'] == 'medium':
                base_score -= 10
            else:
                base_score -= 5
        
        return max(0, base_score)
    
    def _calculate_scores(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate overall scores based on analysis results"""
        scores = {}
        
        # Responsiveness score (average of viewport scores)
        viewport_scores = [v.get('responsive_score', 50) for v in results.get('viewports', [])]
        scores['responsiveness'] = int(sum(viewport_scores) / len(viewport_scores) if viewport_scores else 50)
        
        # SEO score
        seo_score = 100
        seo_issues = [i for i in self.all_issues if i['category'] == 'seo']
        for issue in seo_issues:
            if issue['severity'] == 'high':
                seo_score -= 25
            elif issue['severity'] == 'medium':
                seo_score -= 15
            else:
                seo_score -= 5
        scores['seo'] = max(0, seo_score)
        
        # Accessibility score
        accessibility_score = 100
        accessibility_issues = [i for i in self.all_issues if i['category'] == 'accessibility']
        for issue in accessibility_issues:
            if issue['severity'] == 'high':
                accessibility_score -= 30
            elif issue['severity'] == 'medium':
                accessibility_score -= 15
            else:
                accessibility_score -= 5
        scores['accessibility'] = max(0, accessibility_score)
        
        # Performance score (basic calculation)
        performance_score = 100
        performance_issues = [i for i in self.all_issues if i['category'] == 'performance']
        for issue in performance_issues:
            if issue['severity'] == 'high':
                performance_score -= 25
            elif issue['severity'] == 'medium':
                performance_score -= 15
            else:
                performance_score -= 10
        scores['performance'] = max(0, performance_score)
        
        # Overall score (weighted average)
        scores['overall'] = int(
            (scores['responsiveness'] * 0.3 + 
             scores['accessibility'] * 0.25 + 
             scores['seo'] * 0.25 + 
             scores['performance'] * 0.2)
        )
        
        return scores
    
    async def _cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Replace the existing WebsiteAnalyzer class with this real implementation
class WebsiteAnalyzer(RealWebsiteAnalyzer):
    """Main analyzer class that uses the real implementation"""
    pass