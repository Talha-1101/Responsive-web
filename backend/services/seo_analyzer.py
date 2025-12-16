"""
SEO analyzer service for detecting SEO issues and opportunities
"""

import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page
from bs4 import BeautifulSoup

from config import settings

logger = logging.getLogger(__name__)

class SEOAnalyzer:
    """Service for analyzing SEO elements and detecting issues"""
    
    def __init__(self):
        self.seo_config = settings.seo_checks
    
    async def analyze_page(self, page: Page) -> Dict[str, Any]:
        """Run complete SEO analysis on the page"""
        try:
            logger.info("Starting SEO analysis...")
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Get current URL
            current_url = page.url
            
            # Analyze different SEO aspects
            title_analysis = await self._analyze_title(soup)
            description_analysis = await self._analyze_description(soup)
            heading_analysis = await self._analyze_headings(soup)
            meta_analysis = await self._analyze_meta_tags(soup)
            link_analysis = await self._analyze_links(soup, current_url)
            image_analysis = await self._analyze_images(soup)
            schema_analysis = await self._analyze_schema(soup)
            
            # Combine all data
            seo_data = {
                **title_analysis['data'],
                **description_analysis['data'],
                **heading_analysis['data'],
                **meta_analysis['data'],
                **link_analysis['data'],
                **image_analysis['data'],
                **schema_analysis['data']
            }
            
            # Combine all issues
            issues = []
            issues.extend(title_analysis['issues'])
            issues.extend(description_analysis['issues'])
            issues.extend(heading_analysis['issues'])
            issues.extend(meta_analysis['issues'])
            issues.extend(link_analysis['issues'])
            issues.extend(image_analysis['issues'])
            issues.extend(schema_analysis['issues'])
            
            logger.info(f"SEO analysis completed. Found {len(issues)} issues.")
            
            return {
                "data": seo_data,
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {
                "data": {"error": str(e)},
                "issues": [{
                    "category": "seo",
                    "type": "seo_analysis_error",
                    "severity": "low",
                    "description": f"SEO analysis failed: {e}"
                }]
            }
    
    async def _analyze_title(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page title"""
        data = {}
        issues = []
        
        try:
            title_tag = soup.find('title')
            
            if title_tag and title_tag.string:
                title = title_tag.string.strip()
                data['title'] = title
                data['title_length'] = len(title)
                
                # Check title length
                min_length = self.seo_config['title']['min_length']
                max_length = self.seo_config['title']['max_length']
                
                if len(title) < min_length:
                    issues.append({
                        "category": "seo",
                        "type": "title_too_short",
                        "severity": "medium",
                        "description": f"Title is too short ({len(title)} chars). Recommended: {min_length}-{max_length} characters",
                        "element_selector": "title"
                    })
                elif len(title) > max_length:
                    issues.append({
                        "category": "seo",
                        "type": "title_too_long", 
                        "severity": "medium",
                        "description": f"Title is too long ({len(title)} chars). May be truncated in search results",
                        "element_selector": "title"
                    })
                
                # Check for duplicate words
                words = title.lower().split()
                if len(words) != len(set(words)):
                    issues.append({
                        "category": "seo",
                        "type": "title_duplicate_words",
                        "severity": "low",
                        "description": "Title contains duplicate words, which may reduce SEO effectiveness",
                        "element_selector": "title"
                    })
            
            else:
                data['title'] = None
                data['title_length'] = 0
                if self.seo_config['title']['required']:
                    issues.append({
                        "category": "seo",
                        "type": "missing_title",
                        "severity": "high",
                        "description": "Missing page title. Essential for SEO and user experience",
                        "element_selector": "title"
                    })
        
        except Exception as e:
            logger.error(f"Title analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "title_analysis_error",
                "severity": "low",
                "description": f"Could not analyze title: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    async def _analyze_description(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze meta description"""
        data = {}
        issues = []
        
        try:
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            
            if desc_tag and desc_tag.get('content'):
                description = desc_tag.get('content').strip()
                data['description'] = description
                data['description_length'] = len(description)
                
                # Check description length
                min_length = self.seo_config['description']['min_length']
                max_length = self.seo_config['description']['max_length']
                
                if len(description) < min_length:
                    issues.append({
                        "category": "seo",
                        "type": "description_too_short",
                        "severity": "medium",
                        "description": f"Meta description is too short ({len(description)} chars). Recommended: {min_length}-{max_length} characters",
                        "element_selector": "meta[name='description']"
                    })
                elif len(description) > max_length:
                    issues.append({
                        "category": "seo",
                        "type": "description_too_long",
                        "severity": "medium", 
                        "description": f"Meta description is too long ({len(description)} chars). May be truncated in search results",
                        "element_selector": "meta[name='description']"
                    })
            
            else:
                data['description'] = None
                data['description_length'] = 0
                if self.seo_config['description']['required']:
                    issues.append({
                        "category": "seo",
                        "type": "missing_description",
                        "severity": "high",
                        "description": "Missing meta description. Important for search engine snippets",
                        "element_selector": "meta[name='description']"
                    })
        
        except Exception as e:
            logger.error(f"Description analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "description_analysis_error",
                "severity": "low",
                "description": f"Could not analyze meta description: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    async def _analyze_headings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze heading structure"""
        data = {}
        issues = []
        
        try:
            # Find all headings
            headings = {f'h{i}': [] for i in range(1, 7)}
            
            for i in range(1, 7):
                heading_tags = soup.find_all(f'h{i}')
                for tag in heading_tags:
                    text = tag.get_text().strip()
                    if text:
                        headings[f'h{i}'].append(text)
            
            # Analyze H1 tags
            h1_tags = headings['h1']
            data['h1_tags'] = h1_tags
            data['h1_count'] = len(h1_tags)
            
            if len(h1_tags) == 0:
                if self.seo_config['h1']['required']:
                    issues.append({
                        "category": "seo",
                        "type": "missing_h1",
                        "severity": "medium",
                        "description": "Missing H1 tag. Important for page structure and SEO",
                        "element_selector": "h1"
                    })
            elif len(h1_tags) > self.seo_config['h1']['max_count']:
                issues.append({
                    "category": "seo",
                    "type": "multiple_h1",
                    "severity": "medium",
                    "description": f"Multiple H1 tags found ({len(h1_tags)}). Should have only one H1 per page",
                    "element_selector": "h1"
                })
            
            # Check heading hierarchy
            hierarchy_issues = self._check_heading_hierarchy(headings)
            issues.extend(hierarchy_issues)
            
            # Store all headings data
            data['headings'] = headings
            data['total_headings'] = sum(len(tags) for tags in headings.values())
        
        except Exception as e:
            logger.error(f"Headings analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "headings_analysis_error",
                "severity": "low",
                "description": f"Could not analyze headings: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    def _check_heading_hierarchy(self, headings: Dict[str, List[str]]) -> List[Dict]:
        """Check if heading hierarchy is logical"""
        issues = []
        
        try:
            # Check if headings skip levels (e.g., H1 followed by H3)
            used_levels = []
            for level in range(1, 7):
                if headings[f'h{level}']:
                    used_levels.append(level)
            
            if used_levels:
                for i in range(1, len(used_levels)):
                    if used_levels[i] - used_levels[i-1] > 1:
                        issues.append({
                            "category": "seo",
                            "type": "heading_hierarchy_skip",
                            "severity": "low",
                            "description": f"Heading hierarchy skips from H{used_levels[i-1]} to H{used_levels[i]}. Consider using sequential heading levels",
                            "element_selector": f"h{used_levels[i]}"
                        })
        
        except Exception as e:
            logger.error(f"Heading hierarchy check error: {e}")
        
        return issues
    
    async def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze various meta tags"""
        data = {}
        issues = []
        
        try:
            # Check viewport meta tag
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            data['has_viewport_meta'] = viewport_meta is not None
            
            if not viewport_meta and self.seo_config['viewport_meta']['required']:
                issues.append({
                    "category": "seo",
                    "type": "missing_viewport_meta",
                    "severity": "high",
                    "description": "Missing viewport meta tag. Essential for mobile responsiveness",
                    "element_selector": "meta[name='viewport']"
                })
            
            # Check lang attribute
            html_tag = soup.find('html')
            data['has_lang_attribute'] = html_tag and html_tag.get('lang') is not None
            
            if not data['has_lang_attribute'] and self.seo_config['lang_attribute']['required']:
                issues.append({
                    "category": "seo",
                    "type": "missing_lang_attribute",
                    "severity": "medium",
                    "description": "Missing lang attribute on HTML tag. Important for accessibility and SEO",
                    "element_selector": "html"
                })
            
            # Check robots meta tag
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            data['robots_meta'] = robots_meta.get('content') if robots_meta else None
            
            # Check canonical URL
            canonical_link = soup.find('link', attrs={'rel': 'canonical'})
            data['canonical_url'] = canonical_link.get('href') if canonical_link else None
            
            # Check Open Graph tags
            og_tags = {}
            for og_tag in soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')}):
                property_name = og_tag.get('property')
                content = og_tag.get('content')
                if property_name and content:
                    og_tags[property_name] = content
            
            data['open_graph'] = og_tags
            
            # Check Twitter Card tags
            twitter_tags = {}
            for twitter_tag in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
                name = twitter_tag.get('name')
                content = twitter_tag.get('content')
                if name and content:
                    twitter_tags[name] = content
            
            data['twitter_cards'] = twitter_tags
        
        except Exception as e:
            logger.error(f"Meta tags analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "meta_analysis_error",
                "severity": "low",
                "description": f"Could not analyze meta tags: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    async def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze internal and external links"""
        data = {}
        issues = []
        
        try:
            all_links = soup.find_all('a', href=True)
            
            internal_links = []
            external_links = []
            broken_links = []
            
            base_domain = urlparse(base_url).netloc
            
            for link in all_links:
                href = link.get('href', '').strip()
                if not href or href.startswith('#'):
                    continue
                
                # Make absolute URL
                absolute_url = urljoin(base_url, href)
                link_domain = urlparse(absolute_url).netloc
                
                # Categorize link
                if link_domain == base_domain or not link_domain:
                    internal_links.append({
                        "url": absolute_url,
                        "text": link.get_text().strip()[:100],
                        "title": link.get('title', '')
                    })
                else:
                    external_links.append({
                        "url": absolute_url,
                        "text": link.get_text().strip()[:100],
                        "title": link.get('title', ''),
                        "rel": link.get('rel', [])
                    })
                
                # Check for potentially broken links
                if href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                
                if not href or href in ['#', 'javascript:void(0)', 'javascript:;']:
                    broken_links.append({
                        "href": href,
                        "text": link.get_text().strip()[:50]
                    })
            
            data['internal_links'] = len(internal_links)
            data['external_links'] = len(external_links)
            data['total_links'] = len(all_links)
            data['broken_links'] = len(broken_links)
            
            # Check for issues
            if len(broken_links) > 0:
                issues.append({
                    "category": "seo",
                    "type": "broken_links",
                    "severity": "medium",
                    "description": f"Found {len(broken_links)} potentially broken or empty links",
                    "elements": broken_links[:5]  # Show first 5
                })
            
            # Check external links without rel="nofollow" or rel="noopener"
            unsafe_external = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href and not href.startswith('#'):
                    absolute_url = urljoin(base_url, href)
                    link_domain = urlparse(absolute_url).netloc
                    
                    if link_domain and link_domain != base_domain:
                        rel = link.get('rel', [])
                        if isinstance(rel, str):
                            rel = rel.split()
                        
                        if 'noopener' not in rel or 'noreferrer' not in rel:
                            unsafe_external.append({
                                "url": absolute_url[:100],
                                "text": link.get_text().strip()[:50]
                            })
            
            if unsafe_external:
                issues.append({
                    "category": "seo",
                    "type": "unsafe_external_links",
                    "severity": "low",
                    "description": f"Found {len(unsafe_external)} external links without proper rel attributes (noopener, noreferrer)",
                    "elements": unsafe_external[:3]
                })
        
        except Exception as e:
            logger.error(f"Links analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "links_analysis_error",
                "severity": "low",
                "description": f"Could not analyze links: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    async def _analyze_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze images for SEO issues"""
        data = {}
        issues = []
        
        try:
            all_images = soup.find_all('img')
            
            images_without_alt = []
            images_with_empty_alt = []
            images_without_title = []
            large_images = []
            
            for img in all_images:
                src = img.get('src', '')
                alt = img.get('alt')
                title = img.get('title')
                
                # Check alt text
                if alt is None:
                    images_without_alt.append({
                        "src": src[:100],
                        "selector": f"img[src*='{src.split('/')[-1][:20]}']" if src else "img"
                    })
                elif not alt.strip():
                    images_with_empty_alt.append({
                        "src": src[:100],
                        "selector": f"img[src*='{src.split('/')[-1][:20]}']" if src else "img"
                    })
                
                # Check title attribute
                if not title:
                    images_without_title.append({
                        "src": src[:100],
                        "alt": alt[:50] if alt else ""
                    })
            
            data['total_images'] = len(all_images)
            data['images_without_alt'] = len(images_without_alt)
            data['images_with_empty_alt'] = len(images_with_empty_alt)
            
            # Create issues
            if images_without_alt:
                issues.append({
                    "category": "accessibility",
                    "type": "missing_alt_text",
                    "severity": "high",
                    "description": f"Found {len(images_without_alt)} images without alt text. Critical for accessibility and SEO",
                    "elements": images_without_alt[:5]
                })
            
            if images_with_empty_alt:
                issues.append({
                    "category": "accessibility",
                    "type": "empty_alt_text",
                    "severity": "medium",
                    "description": f"Found {len(images_with_empty_alt)} images with empty alt text",
                    "elements": images_with_empty_alt[:5]
                })
        
        except Exception as e:
            logger.error(f"Images analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "images_analysis_error",
                "severity": "low",
                "description": f"Could not analyze images: {e}"
            })
        
        return {"data": data, "issues": issues}
    
    async def _analyze_schema(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze structured data (Schema.org)"""
        data = {}
        issues = []
        
        try:
            # Look for JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            schema_data = []
            
            for script in json_ld_scripts:
                try:
                    import json
                    schema_content = json.loads(script.string)
                    schema_data.append(schema_content)
                except json.JSONDecodeError:
                    continue
            
            # Look for microdata
            microdata_items = soup.find_all('*', attrs={'itemscope': True})
            
            data['structured_data'] = {
                'json_ld_count': len(json_ld_scripts),
                'microdata_count': len(microdata_items),
                'has_structured_data': len(json_ld_scripts) > 0 or len(microdata_items) > 0
            }
            
            # Suggest structured data if missing
            if not data['structured_data']['has_structured_data']:
                issues.append({
                    "category": "seo",
                    "type": "missing_structured_data",
                    "severity": "low",
                    "description": "No structured data found. Consider adding Schema.org markup for better search engine understanding",
                    "element_selector": "script[type='application/ld+json']"
                })
        
        except Exception as e:
            logger.error(f"Schema analysis error: {e}")
            issues.append({
                "category": "seo",
                "type": "schema_analysis_error",
                "severity": "low",
                "description": f"Could not analyze structured data: {e}"
            })
        
        return {"data": data, "issues": issues}