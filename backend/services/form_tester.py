"""
Form testing service for detecting and testing website forms
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

from playwright.async_api import Page

from config import settings

logger = logging.getLogger(__name__)

class FormTester:
    """Service for detecting and testing website forms"""
    
    def __init__(self):
        self.test_data = settings.form_test_data
    
    async def analyze_forms(self, page: Page) -> Dict[str, Any]:
        """Analyze and test all forms on the page"""
        try:
            logger.info("Starting form analysis...")
            
            forms = await self._find_all_forms(page)
            logger.info(f"Found {len(forms)} forms on the page")
            
            data = {
                "forms_found": len(forms),
                "forms_tested": 0,
                "email_fields": 0,
                "required_fields": 0,
                "consent_checkboxes": 0,
                "forms_with_validation": 0,
                "forms_data": []
            }
            
            issues = []
            
            for i, form_info in enumerate(forms):
                try:
                    form_analysis = await self._analyze_single_form(page, form_info, i)
                    data["forms_data"].append(form_analysis["data"])
                    issues.extend(form_analysis["issues"])
                    
                    # Update counters
                    if form_analysis["data"].get("tested"):
                        data["forms_tested"] += 1
                    
                    data["email_fields"] += form_analysis["data"].get("email_fields", 0)
                    data["required_fields"] += form_analysis["data"].get("required_fields", 0) 
                    data["consent_checkboxes"] += form_analysis["data"].get("consent_checkboxes", 0)
                    
                    if form_analysis["data"].get("has_validation"):
                        data["forms_with_validation"] += 1
                        
                except Exception as e:
                    logger.error(f"Error analyzing form {i}: {e}")
                    issues.append({
                        "category": "forms",
                        "type": "form_analysis_error",
                        "severity": "low",
                        "description": f"Could not analyze form #{i+1}: {e}"
                    })
            
            logger.info(f"Form analysis completed. Tested {data['forms_tested']}/{data['forms_found']} forms")
            
            return {"data": data, "issues": issues}
            
        except Exception as e:
            logger.error(f"Form analysis failed: {e}")
            return {
                "data": {"error": str(e)},
                "issues": [{
                    "category": "forms",
                    "type": "form_analysis_error",
                    "severity": "low",
                    "description": f"Form analysis failed: {e}"
                }]
            }
    
    async def _find_all_forms(self, page: Page) -> List[Dict]:
        """Find all forms on the page"""
        try:
            forms_data = await page.evaluate("""
                () => {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.map((form, index) => {
                        return {
                            index: index,
                            action: form.action || '',
                            method: form.method || 'GET',
                            id: form.id || '',
                            className: form.className || '',
                            fieldCount: form.querySelectorAll('input, select, textarea').length
                        };
                    });
                }
            """)
            return forms_data
        except Exception as e:
            logger.error(f"Error finding forms: {e}")
            return []
    
    async def _analyze_single_form(self, page: Page, form_info: Dict, form_index: int) -> Dict[str, Any]:
        """Analyze a single form in detail"""
        data = {
            "form_index": form_index,
            "action": form_info.get("action", ""),
            "method": form_info.get("method", "GET"),
            "field_count": form_info.get("fieldCount", 0),
            "tested": False,
            "email_fields": 0,
            "required_fields": 0,
            "consent_checkboxes": 0,
            "has_validation": False,
            "fields": []
        }
        
        issues = []
        
        try:
            # Get detailed form field information
            form_selector = f"form:nth-of-type({form_index + 1})"
            
            fields_data = await page.evaluate(f"""
                (selector) => {{
                    const form = document.querySelector(selector);
                    if (!form) return [];
                    
                    const fields = Array.from(form.querySelectorAll('input, select, textarea'));
                    return fields.map(field => {{
                        return {{
                            type: field.type || field.tagName.toLowerCase(),
                            name: field.name || '',
                            id: field.id || '',
                            required: field.required || false,
                            placeholder: field.placeholder || '',
                            value: field.value || '',
                            className: field.className || '',
                            autocomplete: field.autocomplete || ''
                        }};
                    }});
                }}
            """, form_selector)
            
            data["fields"] = fields_data
            
            # Analyze field types
            for field in fields_data:
                field_type = field.get("type", "").lower()
                
                # Count email fields
                if field_type == "email" or "email" in field.get("name", "").lower():
                    data["email_fields"] += 1
                
                # Count required fields
                if field.get("required"):
                    data["required_fields"] += 1
                
                # Count consent checkboxes
                if field_type == "checkbox":
                    field_name = field.get("name", "").lower()
                    field_id = field.get("id", "").lower()
                    if any(keyword in field_name + field_id for keyword in ["consent", "privacy", "terms", "agree", "accept"]):
                        data["consent_checkboxes"] += 1
            
            # Check for form validation
            has_validation = await page.evaluate(f"""
                (selector) => {{
                    const form = document.querySelector(selector);
                    if (!form) return false;
                    
                    // Check for HTML5 validation attributes
                    const hasRequiredFields = form.querySelectorAll('[required]').length > 0;
                    const hasPattern = form.querySelectorAll('[pattern]').length > 0;
                    const hasMinMax = form.querySelectorAll('[min], [max]').length > 0;
                    
                    // Check for validation classes or attributes
                    const hasValidationClasses = form.querySelector('.validate, .validation, [data-validate]') !== null;
                    
                    return hasRequiredFields || hasPattern || hasMinMax || hasValidationClasses;
                }}
            """, form_selector)
            
            data["has_validation"] = has_validation
            
            # Test form filling (only for safe forms)
            if await self._is_safe_to_test(form_info, fields_data):
                test_result = await self._test_form_filling(page, form_selector, fields_data)
                data["tested"] = test_result["success"]
                if not test_result["success"]:
                    issues.append({
                        "category": "forms",
                        "type": "form_filling_failed",
                        "severity": "low",
                        "description": f"Could not test form #{form_index + 1}: {test_result.get('error', 'Unknown error')}",
                        "element_selector": form_selector
                    })
            
            # Check for common form issues
            form_issues = await self._check_form_issues(page, form_selector, fields_data, form_info)
            issues.extend(form_issues)
            
        except Exception as e:
            logger.error(f"Error in single form analysis: {e}")
            issues.append({
                "category": "forms",
                "type": "form_field_analysis_error",
                "severity": "low",
                "description": f"Could not analyze form fields: {e}",
                "element_selector": f"form:nth-of-type({form_index + 1})"
            })
        
        return {"data": data, "issues": issues}
    
    async def _is_safe_to_test(self, form_info: Dict, fields_data: List[Dict]) -> bool:
        """Determine if it's safe to test the form"""
        # Don't test forms that might cause side effects
        action = form_info.get("action", "").lower()
        method = form_info.get("method", "").upper()
        
        # Skip forms with dangerous actions
        dangerous_actions = ["delete", "remove", "purchase", "buy", "pay", "checkout", "order"]
        if any(word in action for word in dangerous_actions):
            return False
        
        # Skip POST forms to external domains (could be payments, etc.)
        if method == "POST" and action.startswith("http") and "://" in action:
            return False
        
        # Skip forms with password fields (login/register forms)
        for field in fields_data:
            if field.get("type") == "password":
                return False
        
        # Skip forms with file uploads
        for field in fields_data:
            if field.get("type") == "file":
                return False
        
        return True
    
    async def _test_form_filling(self, page: Page, form_selector: str, fields_data: List[Dict]) -> Dict[str, Any]:
        """Test filling the form with dummy data"""
        try:
            for field in fields_data:
                field_type = field.get("type", "").lower()
                field_name = field.get("name", "")
                field_id = field.get("id", "")
                
                # Create field selector
                if field_id:
                    field_selector = f"{form_selector} #{field_id}"
                elif field_name:
                    field_selector = f"{form_selector} [name='{field_name}']"
                else:
                    continue
                
                try:
                    # Fill field based on type
                    if field_type in ["text", "search"]:
                        await page.fill(field_selector, self.test_data["text"])
                    elif field_type == "email":
                        await page.fill(field_selector, self.test_data["email"])
                    elif field_type == "tel":
                        await page.fill(field_selector, self.test_data["phone"])
                    elif field_type == "url":
                        await page.fill(field_selector, self.test_data["url"])
                    elif field_type == "number":
                        await page.fill(field_selector, self.test_data["number"])
                    elif field_type == "textarea":
                        await page.fill(field_selector, self.test_data["text"])
                    elif field_type == "select":
                        # Select first available option
                        await page.select_option(field_selector, index=1)
                    elif field_type == "checkbox" and not field.get("required"):
                        # Only check non-required checkboxes (avoid consent forms)
                        await page.check(field_selector)
                    
                    # Small delay between fields
                    await asyncio.sleep(0.1)
                    
                except Exception as field_error:
                    logger.debug(f"Could not fill field {field_selector}: {field_error}")
                    continue
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_form_issues(self, page: Page, form_selector: str, fields_data: List[Dict], form_info: Dict) -> List[Dict]:
        """Check for common form issues"""
        issues = []
        
        try:
            # Check for missing labels
            unlabeled_fields = []
            for field in fields_data:
                field_id = field.get("id")
                field_name = field.get("name")
                
                if field_id:
                    has_label = await page.evaluate(f"""
                        () => {{
                            return document.querySelector('label[for="{field_id}"]') !== null;
                        }}
                    """)
                    if not has_label and field.get("type") not in ["hidden", "submit", "button"]:
                        unlabeled_fields.append({
                            "id": field_id,
                            "type": field.get("type"),
                            "name": field_name
                        })
            
            if unlabeled_fields:
                issues.append({
                    "category": "accessibility",
                    "type": "unlabeled_form_fields",
                    "severity": "medium", 
                    "description": f"Found {len(unlabeled_fields)} form fields without proper labels",
                    "element_selector": form_selector,
                    "elements": unlabeled_fields[:5]
                })
            
            # Check for missing form validation
            if not any(field.get("required") for field in fields_data):
                issues.append({
                    "category": "forms",
                    "type": "no_required_fields",
                    "severity": "low",
                    "description": "Form has no required fields. Consider adding validation",
                    "element_selector": form_selector
                })
            
            # Check for forms without submit buttons
            has_submit = await page.evaluate(f"""
                (selector) => {{
                    const form = document.querySelector(selector);
                    if (!form) return false;
                    
                    const submitButtons = form.querySelectorAll('input[type="submit"], button[type="submit"], button:not([type])');
                    return submitButtons.length > 0;
                }}
            """, form_selector)
            
            if not has_submit:
                issues.append({
                    "category": "forms",
                    "type": "missing_submit_button",
                    "severity": "medium",
                    "description": "Form appears to be missing a submit button",
                    "element_selector": form_selector
                })
            
            # Check for forms with GET method that should use POST
            if form_info.get("method", "").upper() == "GET" and len(fields_data) > 2:
                # Forms with multiple fields should usually use POST
                has_sensitive_fields = any(
                    field.get("type") in ["password", "email"] or 
                    "password" in field.get("name", "").lower() or
                    "email" in field.get("name", "").lower()
                    for field in fields_data
                )
                
                if has_sensitive_fields:
                    issues.append({
                        "category": "forms",
                        "type": "insecure_form_method",
                        "severity": "medium",
                        "description": "Form with sensitive fields uses GET method. Should use POST for security",
                        "element_selector": form_selector
                    })
            
            # Check for missing autocomplete attributes on important fields
            missing_autocomplete = []
            for field in fields_data:
                field_type = field.get("type", "").lower()
                field_name = field.get("name", "").lower()
                autocomplete = field.get("autocomplete", "")
                
                if field_type == "email" and not autocomplete:
                    missing_autocomplete.append(f"email field without autocomplete")
                elif "name" in field_name and field_type == "text" and not autocomplete:
                    missing_autocomplete.append(f"name field without autocomplete")
                elif "phone" in field_name and not autocomplete:
                    missing_autocomplete.append(f"phone field without autocomplete")
            
            if missing_autocomplete:
                issues.append({
                    "category": "forms",
                    "type": "missing_autocomplete",
                    "severity": "low",
                    "description": f"Form fields missing autocomplete attributes: {', '.join(missing_autocomplete[:3])}",
                    "element_selector": form_selector
                })
        
        except Exception as e:
            logger.error(f"Error checking form issues: {e}")
            issues.append({
                "category": "forms",
                "type": "form_issue_check_error",
                "severity": "low",
                "description": f"Could not check form for common issues: {e}",
                "element_selector": form_selector
            })
        
        return issues