"""
Platform detection service for identifying CMS and frameworks
"""

import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from playwright.async_api import Page

from config import settings

logger = logging.getLogger(__name__)

class PlatformDetector:
    """Service for detecting website platforms, CMS, and frameworks"""
    
    def __init__(self):
        self.patterns = settings.platform_patterns
    
    async def detect_platform(self, page: Page, url: str) -> Dict[str, Any]:
        """Detect the platform/CMS used by the website"""
        try:
            logger.info("Starting platform detection...")
            
            # Get page content and sources
            content = await page.content()
            
            # Get all script and link sources
            sources = await self._get_external_sources(page)
            
            # Get meta tags
            meta_tags = await self._get_meta_tags(page)
            
            # Get response headers
            response = await page.goto(url) if page.url != url else None
            headers = response.headers if response else {}
            
            # Run detection methods
            detections = {}
            
            for platform_name in self.patterns.keys():
                detection_result = await self._detect_single_platform(
                    platform_name, content, sources, meta_tags, headers, url
                )
                if detection_result["confidence"] > 0:
                    detections[platform_name] = detection_result
            
            # Determine the most likely platform
            best_match = self._get_best_match(detections)
            
            result = {
                "platform": best_match["name"],
                "confidence": best_match["confidence"],
                "indicators": best_match["indicators"],
                "version": best_match.get("version"),
                "all_detections": detections,
                "additional_info": best_match.get("additional_info", {})
            }
            
            logger.info(f"Platform detection completed: {best_match['name']} ({best_match['confidence']:.2f} confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Platform detection failed: {e}")
            return {
                "platform": "Unknown",
                "confidence": 0.0,
                "indicators": [],
                "error": str(e)
            }
    
    async def _get_external_sources(self, page: Page) -> Dict[str, List[str]]:
        """Get all external script and stylesheet sources"""
        try:
            sources = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
                    const stylesheets = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href);
                    const images = Array.from(document.querySelectorAll('img[src]')).slice(0, 50).map(i => i.src); // Limit images
                    
                    return {
                        scripts: scripts,
                        stylesheets: stylesheets,
                        images: images
                    };
                }
            """)
            return sources
        except Exception as e:
            logger.error(f"Error getting external sources: {e}")
            return {"scripts": [], "stylesheets": [], "images": []}
    
    async def _get_meta_tags(self, page: Page) -> Dict[str, str]:
        """Get all meta tags"""
        try:
            meta_tags = await page.evaluate("""
                () => {
                    const metas = Array.from(document.querySelectorAll('meta'));
                    const metaData = {};
                    
                    metas.forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property') || meta.getAttribute('http-equiv');
                        const content = meta.getAttribute('content');
                        
                        if (name && content) {
                            metaData[name.toLowerCase()] = content;
                        }
                    });
                    
                    return metaData;
                }
            """)
            return meta_tags
        except Exception as e:
            logger.error(f"Error getting meta tags: {e}")
            return {}
    
    async def _detect_single_platform(self, platform_name: str, content: str, sources: Dict, meta_tags: Dict, headers: Dict, url: str) -> Dict[str, Any]:
        """Detect a specific platform"""
        indicators = []
        confidence = 0.0
        version = None
        additional_info = {}
        
        try:
            patterns = self.patterns[platform_name]
            
            # Check patterns in content
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    indicators.append(f"Content contains: {pattern}")
                    confidence += 0.2
            
            # Check patterns in external sources
            all_sources = " ".join(sources.get("scripts", []) + sources.get("stylesheets", []) + sources.get("images", []))
            for pattern in patterns:
                if pattern.lower() in all_sources.lower():
                    indicators.append(f"External source contains: {pattern}")
                    confidence += 0.25
            
            # Check patterns in meta tags
            meta_content = " ".join(meta_tags.values()).lower()
            for pattern in patterns:
                if pattern.lower() in meta_content:
                    indicators.append(f"Meta tag contains: {pattern}")
                    confidence += 0.3
            
            # Platform-specific detection logic
            if platform_name == "WordPress":
                additional_info.update(await self._detect_wordpress_details(content, sources, meta_tags))
                if additional_info.get("version"):
                    version = additional_info["version"]
                    confidence += 0.2
            
            elif platform_name == "Shopify":
                additional_info.update(await self._detect_shopify_details(content, sources, url))
                if additional_info.get("shop_id"):
                    confidence += 0.3
            
            elif platform_name == "React":
                additional_info.update(await self._detect_react_details(content, sources))
                if additional_info.get("react_version"):
                    version = additional_info["react_version"]
                    confidence += 0.15
            
            elif platform_name == "Vue":
                additional_info.update(await self._detect_vue_details(content, sources))
                if additional_info.get("vue_version"):
                    version = additional_info["vue_version"]
                    confidence += 0.15
            
            elif platform_name == "Angular":
                additional_info.update(await self._detect_angular_details(content, sources))
                if additional_info.get("angular_version"):
                    version = additional_info["angular_version"]
                    confidence += 0.15
            
            # Cap confidence at 1.0
            confidence = min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error detecting {platform_name}: {e}")
        
        return {
            "confidence": confidence,
            "indicators": indicators,
            "version": version,
            "additional_info": additional_info
        }
    
    async def _detect_wordpress_details(self, content: str, sources: Dict, meta_tags: Dict) -> Dict[str, Any]:
        """Detect WordPress-specific details"""
        details = {}
        
        try:
            # Try to find WordPress version
            version_patterns = [
                r'wp-includes.*?ver=([0-9.]+)',
                r'wordpress[^0-9]*([0-9.]+)',
                r'generator.*?wordpress[^0-9]*([0-9.]+)'
            ]
            
            search_text = content + " ".join(sources.get("scripts", []))
            
            for pattern in version_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["version"] = match.group(1)
                    break
            
            # Check for common WordPress themes
            theme_indicators = [
                "twentytwentyone", "twentytwenty", "twentynineteen", "astra", "generatepress", 
                "oceanwp", "neve", "kadence", "customify", "hestia"
            ]
            
            for theme in theme_indicators:
                if theme in search_text.lower():
                    details["theme"] = theme
                    break
            
            # Check for common plugins
            plugin_indicators = [
                "woocommerce", "yoast", "elementor", "contact-form-7", "akismet",
                "jetpack", "wordfence", "wpbakery", "slider-revolution"
            ]
            
            detected_plugins = []
            for plugin in plugin_indicators:
                if plugin in search_text.lower():
                    detected_plugins.append(plugin)
            
            if detected_plugins:
                details["plugins"] = detected_plugins[:5]  # Limit to 5
            
        except Exception as e:
            logger.error(f"Error detecting WordPress details: {e}")
        
        return details
    
    async def _detect_shopify_details(self, content: str, sources: Dict, url: str) -> Dict[str, Any]:
        """Detect Shopify-specific details"""
        details = {}
        
        try:
            # Extract shop ID from Shopify indicators
            shopify_patterns = [
                r'shop_id["\']?\s*:\s*["\']?(\d+)',
                r'Shopify\.shop\s*=\s*["\']([^"\']+)',
                r'myshopify\.com/([^/"\']+)'
            ]
            
            search_text = content + " ".join(sources.get("scripts", []))
            
            for pattern in shopify_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["shop_id"] = match.group(1)
                    break
            
            # Check for Shopify theme
            theme_patterns = [
                r'Shopify\.theme\s*=\s*["\']([^"\']+)',
                r'theme["\']?\s*:\s*["\']([^"\']+)'
            ]
            
            for pattern in theme_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["theme"] = match.group(1)
                    break
            
            # Check for Shopify Plus
            if "shopify-plus" in search_text.lower() or "shopifyplus" in search_text.lower():
                details["shopify_plus"] = True
            
        except Exception as e:
            logger.error(f"Error detecting Shopify details: {e}")
        
        return details
    
    async def _detect_react_details(self, content: str, sources: Dict) -> Dict[str, Any]:
        """Detect React-specific details"""
        details = {}
        
        try:
            # Try to find React version
            version_patterns = [
                r'react[^0-9]*([0-9.]+)',
                r'React\.version.*?([0-9.]+)',
                r'react.*?@([0-9.]+)'
            ]
            
            search_text = content + " ".join(sources.get("scripts", []))
            
            for pattern in version_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["react_version"] = match.group(1)
                    break
            
            # Check for React frameworks
            frameworks = ["next.js", "gatsby", "create-react-app"]
            for framework in frameworks:
                if framework.replace(".", "").replace("-", "") in search_text.lower().replace(".", "").replace("-", ""):
                    details["framework"] = framework
                    break
            
        except Exception as e:
            logger.error(f"Error detecting React details: {e}")
        
        return details
    
    async def _detect_vue_details(self, content: str, sources: Dict) -> Dict[str, Any]:
        """Detect Vue.js-specific details"""
        details = {}
        
        try:
            # Try to find Vue version
            version_patterns = [
                r'vue[^0-9]*([0-9.]+)',
                r'Vue\.version.*?([0-9.]+)',
                r'vue.*?@([0-9.]+)'
            ]
            
            search_text = content + " ".join(sources.get("scripts", []))
            
            for pattern in version_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["vue_version"] = match.group(1)
                    break
            
            # Check for Vue frameworks
            if "nuxt" in search_text.lower():
                details["framework"] = "Nuxt.js"
            elif "quasar" in search_text.lower():
                details["framework"] = "Quasar"
            elif "vuetify" in search_text.lower():
                details["ui_framework"] = "Vuetify"
            
        except Exception as e:
            logger.error(f"Error detecting Vue details: {e}")
        
        return details
    
    async def _detect_angular_details(self, content: str, sources: Dict) -> Dict[str, Any]:
        """Detect Angular-specific details"""
        details = {}
        
        try:
            # Try to find Angular version
            version_patterns = [
                r'angular[^0-9]*([0-9.]+)',
                r'@angular/core.*?([0-9.]+)',
                r'ng-version.*?([0-9.]+)'
            ]
            
            search_text = content + " ".join(sources.get("scripts", []))
            
            for pattern in version_patterns:
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    details["angular_version"] = match.group(1)
                    break
            
            # Check for Angular CLI
            if "angular-cli" in search_text.lower() or "ng build" in search_text.lower():
                details["built_with_cli"] = True
            
        except Exception as e:
            logger.error(f"Error detecting Angular details: {e}")
        
        return details
    
    def _get_best_match(self, detections: Dict[str, Dict]) -> Dict[str, Any]:
        """Get the platform with the highest confidence"""
        if not detections:
            return {
                "name": "Unknown",
                "confidence": 0.0,
                "indicators": []
            }
        
        # Sort by confidence
        sorted_detections = sorted(
            detections.items(), 
            key=lambda x: x[1]["confidence"], 
            reverse=True
        )
        
        best_platform, best_data = sorted_detections[0]
        
        return {
            "name": best_platform,
            "confidence": best_data["confidence"],
            "indicators": best_data["indicators"],
            "version": best_data.get("version"),
            "additional_info": best_data.get("additional_info", {})
        }