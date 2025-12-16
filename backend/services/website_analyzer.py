"""
Windows-Compatible Website Analyzer - Final Solution
Handles Windows Playwright subprocess issues with multiple fallback strategies
"""
from bs4 import BeautifulSoup

import asyncio
import logging
import json
import base64
import sys
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

# Check for required dependencies
try:
    import httpx
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("httpx or BeautifulSoup not available")

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available")

from config import settings
from utils.real_screenshot_service import RealScreenshotService

SHOPIFY_PREVIEW_PATTERNS = (
    "shopifypreview.com",
    ".myshopify.com",
)


class WindowsCompatibleWebsiteAnalyzer:
    """Website analyzer with Windows subprocess compatibility fixes"""
    
    def __init__(self):
        self.session_id = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.viewport_results = []
        self.all_issues = []
        self.analysis_mode = "unknown"  # browser, http, or minimal
        self._successful_browser_method: Optional[str] = None
        self._chromium_retry_attempted = False
        self.network_condition: Optional[str] = None
    
    async def _simulate_network_condition(self, page: Page, condition: str):
        """Simulate network conditions using Chrome DevTools Protocol"""
        if condition not in settings.network_profiles:
            return

        profile = settings.network_profiles[condition]
        
        try:
            # Connect to CDP session
            client = await page.context.new_cdp_session(page)
            
            if profile["offline"]:
                await client.send("Network.enable")
                await client.send("Network.emulateNetworkConditions", {
                    "offline": True,
                    "latency": 0,
                    "downloadThroughput": 0,
                    "uploadThroughput": 0,
                })
            else:
                await client.send("Network.enable")
                await client.send("Network.emulateNetworkConditions", {
                    "offline": False,
                    "latency": profile["latency"],
                    "downloadThroughput": profile["downloadThroughput"],
                    "uploadThroughput": profile["uploadThroughput"],
                })
            logger.info(f"📶 Network simulated: {condition}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to simulate network {condition}: {e}")
        
    async def analyze_website(self, url: str, session_id: str = None, progress_callback=None, network_condition: str = None) -> Dict[str, Any]:
        """Perform website analysis with Windows compatibility"""
        self.session_id = session_id
        self.network_condition = network_condition
        start_time = datetime.now()
        
        try:
            logger.info(f"🔍 Starting Windows-compatible analysis for: {url}")

            if any(pattern in url for pattern in SHOPIFY_PREVIEW_PATTERNS):
                logger.warning("🛑 Shopify preview URL detected - skipping real browser analysis")
                if REQUESTS_AVAILABLE:
                    self.analysis_mode = "http"
                    return await self._run_http_analysis(
                        url,
                        session_id,
                        start_time,
                        fallback_reason="Shopify preview domains block real browsers; using HTTP-only mode.",
                    )
                logger.warning("⚠️ HTTP client unavailable; falling back to minimal analysis")
                self.analysis_mode = "minimal"
                return await self._run_minimal_analysis(
                    url,
                    session_id,
                    start_time,
                    fallback_reason="HTTP client unavailable for Shopify preview URL.",
                )
            
            # Try browser analysis first
            if await self._try_browser_analysis():
                logger.info("✅ Using browser-based analysis")
                self.analysis_mode = "browser"
                return await self._run_browser_analysis(url, session_id, start_time, progress_callback)
            
            # Fall back to HTTP-only analysis
            elif REQUESTS_AVAILABLE:
                logger.info("🌐 Using HTTP-only analysis")
                self.analysis_mode = "http"
                return await self._run_http_analysis(
                    url,
                    session_id,
                    start_time,
                    fallback_reason="Browser engine unavailable; running HTTP-only analysis.",
                )
            
            # Last resort: minimal analysis
            else:
                logger.warning("⚠️ Using minimal analysis")
                self.analysis_mode = "minimal"
                return await self._run_minimal_analysis(
                    url,
                    session_id,
                    start_time,
                    fallback_reason="Browser analysis unavailable and HTTP client missing.",
                )
                
        except Exception as e:
            logger.error(f"❌ All analysis methods failed for {url}: {e}")
            return self._generate_error_result(url, session_id, start_time, str(e))
        finally:
            await self._cleanup()
    
    async def _try_browser_analysis(self) -> bool:
        """Test if browser analysis is possible on this system"""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        # On non-Windows (macOS/Linux), try WebKit first then fall back to Chromium
        if not sys.platform.startswith("win"):
            if await self._test_browser_engine("webkit"):
                return True
            logger.warning("⚠️ WebKit test failed or unstable, trying Chromium...")
            if await self._test_browser_engine("chromium"):
                return True
            return False
        
        # Windows-specific strategies
        if await self._test_browser_with_selector_policy():
            return True
        
        if await self._test_browser_with_direct_chrome():
            return True
        
        if await self._test_browser_minimal_subprocess():
            return True
        
        return False
    
    async def _test_browser_with_selector_policy(self) -> bool:
        """Test browser with Windows Selector Event Loop Policy"""
        try:
            logger.info("🔧 Testing browser with WindowsSelectorEventLoopPolicy...")
            
            # Temporarily change event loop policy
            original_policy = asyncio.get_event_loop_policy()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            # Create new event loop for this test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                # Quick test
                page = await self.browser.new_page()
                await page.goto('data:text/html,<h1>Test</h1>')
                await page.close()
                
                self._successful_browser_method = "selector_policy"
                logger.info("✅ WindowsSelectorEventLoopPolicy browser test successful")
                return True
                
            finally:
                # Restore original policy
                if self.browser:
                    await self.browser.close()
                if self.playwright:
                    await self.playwright.stop()
                asyncio.set_event_loop_policy(original_policy)
                
        except Exception as e:
            logger.warning(f"⚠️ WindowsSelectorEventLoopPolicy test failed: {e}")
            return False

    async def _test_browser_engine(self, engine: str) -> bool:
        """Shared test helper for non-Windows platforms."""
        if engine not in {"webkit", "chromium"}:
            return False
        try:
            pretty = engine.title()
            logger.info(f"🔧 Testing browser with {pretty} on non-Windows platform...")
            self.playwright = await async_playwright().start()
            launcher = getattr(self.playwright, engine)
            browser = await launcher.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            page = await browser.new_page()
            await page.goto("data:text/html,<h1>Test</h1>")
            await page.close()
            await browser.close()
            self._successful_browser_method = engine
            logger.info(f"✅ {pretty} browser test successful")
            return True
        except Exception as e:
            logger.warning(f"⚠️ {pretty} browser test failed: {e}")
            return False
        finally:
            try:
                if self.playwright:
                    await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None
    
    async def _test_browser_with_direct_chrome(self) -> bool:
        """Test browser with direct Chrome executable"""
        try:
            logger.info("🔧 Testing browser with direct Chrome executable...")
            
            # Find Chrome installation
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
            ]
            
            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break
            
            if not chrome_exe:
                logger.warning("⚠️ Chrome executable not found")
                return False
            
            logger.info(f"📍 Found Chrome at: {chrome_exe}")
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                executable_path=chrome_exe,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--single-process']
            )
            
            # Quick test
            page = await self.browser.new_page()
            await page.goto('data:text/html,<h1>Test</h1>')
            await page.close()
            
            self._successful_browser_method = "direct_chrome"
            logger.info("✅ Direct Chrome executable test successful")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Direct Chrome test failed: {e}")
            return False
    
    async def _test_browser_minimal_subprocess(self) -> bool:
        """Test browser with minimal subprocess configuration"""
        try:
            logger.info("🔧 Testing browser with minimal subprocess...")
            
            # Use threading instead of subprocess for Windows
            import threading
            
            def run_playwright_in_thread():
                """Run Playwright in a separate thread to avoid subprocess issues"""
                try:
                    # This is a simplified test - in practice we'd need more complex thread handling
                    return True
                except:
                    return False
            
            # For now, just return False to skip this complex implementation
            logger.info("⚠️ Minimal subprocess test skipped (complex implementation)")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Minimal subprocess test failed: {e}")
            return False
    
    async def _run_browser_analysis(self, url: str, session_id: str, start_time: datetime, progress_callback=None) -> Dict[str, Any]:
        """Run full browser-based analysis.
        If browser analysis fails (e.g., target crashes), gracefully fall back to HTTP/minimal analysis
        instead of returning a hard error so the frontend still gets usable results."""
        try:
            # Since browser setup succeeded in test, set it up again for actual analysis
            await self._setup_browser_for_analysis()
            
            # Simulate network condition if specified
            if self.network_condition:
                await self._simulate_network_condition(self.page, self.network_condition)
            
            # Run comprehensive analysis
            if progress_callback: await progress_callback(20, "Loading website content...", "loading")
            
            # Load website
            await self._load_website(url)
            
            if progress_callback: await progress_callback(30, "Testing responsive viewports...", "responsive_testing")
            
            # Run comprehensive analysis
            results = await self._run_comprehensive_browser_analysis(url, progress_callback)
            
            # Add metadata
            results.update({
                "url": url,
                "session_id": session_id,
                "timestamp": start_time.isoformat(),
                "analysis_duration": (datetime.now() - start_time).total_seconds(),
                "analysis_type": "browser_analysis",
                "analysis_mode": self.analysis_mode
            })
            
            return results
        except Exception as e:
            error_message = str(e)
            logger.error(f"Browser analysis failed for {url}: {error_message}")

            # Retry once with Chromium on macOS/Linux if WebKit crashes
            if (
                "Target crashed" in error_message
                and not sys.platform.startswith("win")
                and not self._chromium_retry_attempted
            ):
                logger.warning("Playwright target crashed with WebKit - retrying once with Chromium")
                self._chromium_retry_attempted = True
                self._successful_browser_method = "chromium"
                await self._cleanup()
                return await self._run_browser_analysis(url, session_id, start_time)

            fallback_reason = f"Browser analysis failed: {error_message}"
            # Fall back to HTTP-only analysis if possible, else minimal
            if REQUESTS_AVAILABLE:
                return await self._run_http_analysis(url, session_id, start_time, fallback_reason=fallback_reason)
            return await self._run_minimal_analysis(url, session_id, start_time, fallback_reason=fallback_reason)
    
    async def _setup_browser_for_analysis(self):
        """Setup browser for actual analysis based on successful test method"""
        # Use the successful engine on non-Windows platforms (macOS/Linux)
        if not sys.platform.startswith("win"):
            engine = self._successful_browser_method or "webkit"
            self.playwright = await async_playwright().start()
            if engine == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                )
            else:
                self.browser = await self.playwright.webkit.launch(headless=True)
                engine = "webkit"
                self._successful_browser_method = engine
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
            )
            self.page = await self.context.new_page()
            return
        
        # Windows-specific setup
        if hasattr(self, '_successful_browser_method'):
            method = self._successful_browser_method
        else:
            method = "standard"
        
        self.playwright = await async_playwright().start()
        
        if method == "selector_policy":
            # Use WindowsSelectorEventLoopPolicy method (policy already set in test)
            pass
        
        # Standard setup with Windows-compatible args
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--single-process',
                '--disable-gpu',
                '--disable-web-security'
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = await self.context.new_page()
    
    async def _load_website(self, url: str):
        """Load website with error handling"""
        try:
            response = await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
            if response and response.status >= 400:
                raise Exception(f"HTTP {response.status}")
            await asyncio.sleep(2)  # Allow content to load
        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            raise
    
    async def _run_comprehensive_browser_analysis(self, url: str, progress_callback=None) -> Dict[str, Any]:
        """Run comprehensive analysis with browser"""
        results = {}
        
        # Test responsive design with screenshots
        results["viewports"] = await self._test_responsive_viewports()
        
        if progress_callback: await progress_callback(50, "Analyzing page content and SEO...", "analyzing_content")

        # Analyze page content
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        results["seo"] = self._analyze_seo_from_soup(soup)
        
        if progress_callback: await progress_callback(60, "Checking accessibility compliance...", "analyzing_accessibility")
        results["accessibility"] = self._analyze_accessibility_from_soup(soup)
        results["images"] = self._analyze_images_from_soup(soup)
        results["links"] = self._analyze_links_from_soup(soup, url)
        results["platform"] = self._detect_platform_from_content(content)
        
        # Performance metrics from browser
        try:
            performance = await self.page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        loadTime: timing.loadEventEnd - timing.navigationStart,
                        domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                        resourceCount: performance.getEntriesByType('resource').length
                    };
                }
            """)
            results["performance"] = performance
        except:
            results["performance"] = {"note": "Performance metrics unavailable"}
        
        results["issues"] = self.all_issues
        results["scores"] = self._calculate_scores(results)
        
        return results
    
    async def _test_responsive_viewports(self) -> List[Dict[str, Any]]:
        """Test responsive design across viewports using True Emulation"""
        viewports = [
            {"name": "Mobile Small", "width": 375, "height": 667},
            {"name": "Mobile", "width": 390, "height": 844},
            {"name": "Tablet", "width": 820, "height": 1180},
            {"name": "Tablet Landscape", "width": 1180, "height": 820},
            {"name": "Desktop", "width": 1440, "height": 900},
            {"name": "Desktop Large", "width": 1920, "height": 1080}
        ]
        
        results = []
        
        for viewport in viewports:
            context = None
            page = None
            try:
                # Determine if we should use True Emulation (new context) or simple resize
                is_emulated = viewport["name"] in settings.device_profiles
                
                if is_emulated:
                    logger.info(f"📱 Using True Emulation for {viewport['name']}...")
                    device_config = settings.device_profiles[viewport["name"]]
                    
                    try:
                        # Create a new isolated context for this device
                        context = await self.browser.new_context(
                            user_agent=device_config["user_agent"],
                            viewport=device_config["viewport"],
                            device_scale_factor=device_config["device_scale_factor"],
                            is_mobile=device_config["is_mobile"],
                            has_touch=device_config["has_touch"]
                        )
                        page = await context.new_page()
                        # Go to URL in this new context
                        await page.goto(self.page.url, wait_until='domcontentloaded', timeout=15000)
                    except Exception as em_error:
                        logger.warning(f"⚠️ True Emulation failed for {viewport['name']}, falling back to resize: {em_error}")
                        if context: await context.close()
                        context = None
                        page = None
                
                # Fallback or Standard Desktop Mode
                if not page:
                    logger.info(f"💻 Using standard viewport resize for {viewport['name']}...")
                    page = self.page  # Use shared page
                    await page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
                    await asyncio.sleep(0.5) # Allow layout to settle

                # Take Screenshot
                screenshot = await page.screenshot(type='png')
                screenshot_b64 = base64.b64encode(screenshot).decode()
                
                # Check for horizontal scroll (Layout Shift)
                scroll_width = await page.evaluate("document.documentElement.scrollWidth")
                client_width = await page.evaluate("document.documentElement.clientWidth")
                has_horizontal_scroll = scroll_width > client_width + 2
                
                issues = []
                if has_horizontal_scroll:
                    # Identify the element causing the scroll
                    widest_element = await page.evaluate("""() => {
                        let widest = null;
                        let maxRight = 0;
                        document.querySelectorAll('*').forEach(el => {
                            const rect = el.getBoundingClientRect();
                            if (rect.right > maxRight) {
                                maxRight = rect.right;
                                widest = el;
                            }
                        });
                        if (!widest) return "Unknown element";
                        return widest.tagName.toLowerCase() + 
                               (widest.id ? '#' + widest.id : '') + 
                               (widest.className ? '.' + widest.className.split(' ')[0] : '');
                    }""")
                    
                    issues.append({
                        "category": "responsiveness",
                        "type": "horizontal_scroll",
                        "issue_type": "horizontal_scroll",
                        "severity": "high",
                        "description": f"Horizontal scroll detected in {viewport['name']}. Caused by: {widest_element}",
                        "context": widest_element,
                        "viewport": viewport['name']
                    })
                
                results.append({
                    "name": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "screenshot_data": screenshot_b64,
                    "screenshot_captured": True,
                    "issues": issues,
                    "responsive_score": 100 if not issues else 80,
                    "emulation_mode": "True Device" if is_emulated else "Viewport Resize"
                })
                
                self.all_issues.extend(issues)
                
            except Exception as e:
                logger.error(f"Viewport test failed for {viewport['name']}: {e}")
                 # If the Playwright target/browser crashed, bubble up so we can fall back
                crash_markers = ("Target crashed", "Target page, context or browser has been closed")
                if any(marker in str(e) for marker in crash_markers):
                   if context: await context.close()
                   raise RuntimeError("Playwright target crashed during viewport tests") from e

                results.append({
                    "name": viewport["name"],
                    "width": viewport["width"],
                    "height": viewport["height"],
                    "error": str(e),
                    "screenshot_captured": False
                })
            finally:
                # Close the emulated context to free memory
                if context:
                    await context.close()
        
        return results
    
    async def _run_http_analysis(
        self,
        url: str,
        session_id: str,
        start_time: datetime,
        fallback_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run HTTP-only analysis when browser fails"""
        logger.info("🌐 Running HTTP-only analysis...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                content = response.text
            
            soup = BeautifulSoup(content, 'html.parser')
            
            results = {
                "url": url,
                "session_id": session_id,
                "timestamp": start_time.isoformat(),
                "analysis_type": "http_analysis",
                "analysis_mode": self.analysis_mode,
                "viewports": self._generate_mock_viewports(),
                "seo": self._analyze_seo_from_soup(soup),
                "accessibility": self._analyze_accessibility_from_soup(soup),
                "images": self._analyze_images_from_soup(soup),
                "links": self._analyze_links_from_soup(soup, url),
                "platform": self._detect_platform_from_content(content),
                "performance": {"note": "Performance analysis requires browser"},
                "issues": self.all_issues,
                "analysis_duration": (datetime.now() - start_time).total_seconds(),
                "analysis_notes": fallback_reason or "HTTP-only analysis executed due to browser limitations",
            }
            
            results["scores"] = self._calculate_scores(results)
            return results
            
        except Exception as e:
            logger.error(f"HTTP analysis failed: {e}")
            return await self._run_minimal_analysis(
                url,
                session_id,
                start_time,
                fallback_reason="HTTP analysis failed; returning minimal diagnostics.",
            )
    
    def _generate_mock_viewports(self) -> List[Dict[str, Any]]:
        """Generate mock viewport data for HTTP analysis"""
        unavailable_msg = "Screenshots unavailable because analysis ran in HTTP-only mode"
        placeholder_path = RealScreenshotService.get_http_only_placeholder_path()
        return [
            {
                "name": "Mobile Small", "width": 375, "height": 667,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            },
            {
                "name": "Mobile", "width": 390, "height": 844,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            },
            {
                "name": "Tablet", "width": 820, "height": 1180,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            },
            {
                "name": "Tablet Landscape", "width": 1180, "height": 820,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            },
            {
                "name": "Desktop", "width": 1440, "height": 900,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            },
            {
                "name": "Desktop Large", "width": 1920, "height": 1080,
                "screenshot_captured": False, "screenshot_path": placeholder_path,
                "error": unavailable_msg, "note": unavailable_msg, "responsive_score": 75
            }
        ]
    
    async def _run_minimal_analysis(
        self,
        url: str,
        session_id: str,
        start_time: datetime,
        fallback_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Minimal analysis when all other methods fail"""
        logger.warning("⚠️ Running minimal analysis - limited functionality")
        
        return {
            "url": url,
            "session_id": session_id,
            "timestamp": start_time.isoformat(),
            "analysis_type": "minimal_analysis",
            "analysis_mode": self.analysis_mode,
            "message": fallback_reason or "Limited analysis due to system compatibility issues",
            "analysis_notes": fallback_reason,
            "viewports": self._generate_mock_viewports(),
            "seo": {"note": "SEO analysis unavailable"},
            "accessibility": {"note": "Accessibility analysis unavailable"},
            "performance": {"note": "Performance analysis unavailable"},
            "platform": {"platform": "Unknown", "confidence": 0},
            "issues": [
                {
                    "category": "system",
                    "type": "limited_analysis",
                    "issue_type": "limited_analysis",
                    "severity": "medium",
                    "description": "Browser analysis unavailable on this system"
                }
            ],
            "scores": {"overall": 50, "responsiveness": 50, "seo": 50, "accessibility": 50, "performance": 50},
            "analysis_duration": (datetime.now() - start_time).total_seconds()
        }
    
    def _analyze_seo_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze SEO from BeautifulSoup"""
        seo_data = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
            seo_data['title'] = title
            seo_data['title_length'] = len(title)
        else:
            seo_data['title'] = None
            seo_data['title_length'] = 0
            self.all_issues.append({
                "category": "seo",
                "type": "missing_title",
                "issue_type": "missing_title",
                "severity": "high",
                "description": "Missing page title",
                "suggestion": "Add a concise <title> tag (50-60 characters) that summarizes the page content."
            })
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            desc = desc_tag.get('content').strip()
            seo_data['description'] = desc
            seo_data['description_length'] = len(desc)
        else:
            seo_data['description'] = None
            seo_data['description_length'] = 0
            self.all_issues.append({
                "category": "seo",
                "type": "missing_description",
                "issue_type": "missing_description",
                "severity": "high",
                "description": "Missing meta description",
                "suggestion": "Add a <meta name=\"description\"> tag (140-160 characters) describing the page benefits."
            })
        
        # H1 tags
        h1_tags = soup.find_all('h1')
        seo_data['h1_count'] = len(h1_tags)
        
        if len(h1_tags) == 0:
            self.all_issues.append({
                "category": "seo",
                "type": "missing_h1",
                "issue_type": "missing_h1",
                "severity": "medium",
                "description": "Missing H1 tag",
                "suggestion": "Add a single <h1> that clearly states the primary topic of the page."
            })
        
        return seo_data
    
    def _analyze_accessibility_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze accessibility from BeautifulSoup"""
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        
        if images_without_alt:
            examples = [img.get('src', 'unknown').split('/')[-1] for img in images_without_alt[:3]]
            example_str = ", ".join(examples)
            
            self.all_issues.append({
                "category": "accessibility",
                "type": "missing_alt_text",
                "issue_type": "missing_alt_text",
                "severity": "high",
                "description": f"Found {len(images_without_alt)} images without alt text (e.g., {example_str})",
                "context": examples,
                "suggestion": "Provide meaningful alt text that explains the purpose of each image for screen readers."
            })
        
        return {
            "images_total": len(images),
            "images_without_alt": len(images_without_alt)
        }
    
    def _analyze_images_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze images from BeautifulSoup"""
        images = soup.find_all('img')
        return {
            "total": len(images),
            "withAlt": len([img for img in images if img.get('alt')]),
            "withoutAlt": len([img for img in images if not img.get('alt')])
        }
    
    def _analyze_links_from_soup(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze links from BeautifulSoup"""
        links = soup.find_all('a', href=True)
        base_domain = urlparse(base_url).netloc
        
        internal = external = 0
        for link in links:
            href = link.get('href')
            if href.startswith('http'):
                if base_domain in href:
                    internal += 1
                else:
                    external += 1
            else:
                internal += 1
        
        return {
            "total": len(links),
            "internal": internal,
            "external": external
        }
    
    def _detect_platform_from_content(self, content: str) -> Dict[str, Any]:
        """Detect platform from content"""
        platforms = {
            "WordPress": ["/wp-content/", "wp-json"],
            "Shopify": ["cdn.shopify.com", "Shopify"],
            "React": ["react", "__REACT_DEVTOOLS_GLOBAL_HOOK__"]
        }
        
        for platform, patterns in platforms.items():
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    return {"platform": platform, "confidence": 0.8}
        
        return {"platform": "Unknown", "confidence": 0.0}
    
    def _calculate_scores(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate scores"""
        scores = {}
        
        # SEO score
        seo_score = 100
        seo_issues = [i for i in self.all_issues if i.get('category') == 'seo']
        for issue in seo_issues:
            if issue.get('severity') == 'high':
                seo_score -= 25
            elif issue.get('severity') == 'medium':
                seo_score -= 15
        scores['seo'] = max(0, seo_score)
        
        # Accessibility score
        accessibility_score = 100
        accessibility_issues = [i for i in self.all_issues if i.get('category') == 'accessibility']
        for issue in accessibility_issues:
            if issue.get('severity') == 'high':
                accessibility_score -= 30
        scores['accessibility'] = max(0, accessibility_score)
        
        # Responsiveness score
        viewport_scores = [v.get('responsive_score', 75) for v in results.get('viewports', [])]
        scores['responsiveness'] = int(sum(viewport_scores) / len(viewport_scores) if viewport_scores else 75)
        
        # Performance score  
        scores['performance'] = 80 if self.analysis_mode == "browser" else 60
        
        # Overall score
        scores['overall'] = int((scores['seo'] + scores['accessibility'] + scores['responsiveness'] + scores['performance']) / 4)
        
        return scores
    
    def _generate_error_result(self, url: str, session_id: str, start_time: datetime, error: str) -> Dict[str, Any]:
        """Generate error result"""
        return {
            "url": url,
            "session_id": session_id,
            "timestamp": start_time.isoformat(),
            "analysis_type": "error",
            "error": error,
            "message": "Analysis failed due to system compatibility issues",
            "scores": {"overall": 0, "responsiveness": 0, "seo": 0, "accessibility": 0, "performance": 0},
            "analysis_duration": (datetime.now() - start_time).total_seconds()
        }
    
    async def _cleanup(self):
        """Clean up resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Backward compatibility
class WebsiteAnalyzer(WindowsCompatibleWebsiteAnalyzer):
    """Main analyzer class"""
    pass
