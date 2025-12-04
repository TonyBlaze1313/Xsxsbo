#!/usr/bin/env python3
"""
Referral Bot - Creates accounts using referral code and Gmail dot trick
"""

import requests
import time
import random
import string
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ReferralBot:
    """Creates SoSoValue accounts using referral code"""
    
    def __init__(self, referral_code: str = "NPH90834", base_gmail: str = None):
        self.referral_code = referral_code
        self.base_gmail = base_gmail
        self.base_url = "https://www.sosovalue.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/join/{referral_code}"
        })
        
        logger.info(f"Referral bot initialized with code: {referral_code}")
        if base_gmail:
            logger.info(f"Gmail mode active: {base_gmail}")
    
    def generate_password(self, length: int = 12) -> str:
        """Generate random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_account(self) -> Dict:
        """Create a new account with referral"""
        try:
            # Generate email
            from mail_generator import getmails, get_verification_code
            
            email = getmails(1)  # This uses Gmail dot trick if configured
            password = self.generate_password()
            
            logger.info(f"Creating account: {email}")
            
            # Try to register
            register_result = self._register_account(email, password)
            
            if not register_result.get("success"):
                return register_result
            
            # Get verification code
            verification_code = get_verification_code(email)
            
            if verification_code:
                # Try to verify
                verify_result = self._verify_account(email, verification_code)
                
                return {
                    "success": True,
                    "email": email,
                    "password": password,
                    "verified": verify_result.get("success", False),
                    "verification_code": verification_code,
                    "referral_code": self.referral_code,
                    "created_at": datetime.now().isoformat(),
                    "message": "Account created" + (" and verified" if verify_result.get("success") else " (pending verification)")
                }
            else:
                # Account created but not verified
                return {
                    "success": True,
                    "email": email,
                    "password": password,
                    "verified": False,
                    "referral_code": self.referral_code,
                    "created_at": datetime.now().isoformat(),
                    "message": "Account created (needs verification)"
                }
            
        except Exception as e:
            logger.error(f"Account creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "email": email if 'email' in locals() else "unknown"
            }
    
    def _register_account(self, email: str, password: str) -> Dict:
        """Register account on SoSoValue"""
        try:
            # Try different registration endpoints
            endpoints = [
                "/api/auth/signup",
                "/api/register",
                "/api/v1/auth/register",
                "/auth/register"
            ]
            
            registration_data = {
                "email": email,
                "password": password,
                "confirmPassword": password,
                "referralCode": self.referral_code,
                "agreeToTerms": True,
                "newsletter": False
            }
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying registration endpoint: {endpoint}")
                    
                    response = self.session.post(
                        urljoin(self.base_url, endpoint),
                        json=registration_data,
                        timeout=30
                    )
                    
                    logger.debug(f"Registration response: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        # Check response
                        try:
                            result = response.json()
                            if "success" in str(result).lower() or "verification" in str(result).lower():
                                logger.info(f"Registration successful for {email}")
                                return {"success": True, "message": "Registration successful"}
                        except:
                            # If not JSON, check text
                            if "success" in response.text.lower() or "verify" in response.text.lower():
                                logger.info(f"Registration successful for {email}")
                                return {"success": True, "message": "Registration successful"}
                    
                    # If we get here, try next endpoint
                    
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
            # If all endpoints failed, try direct form
            return self._try_direct_registration(email, password)
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {"success": False, "error": f"Registration failed: {str(e)}"}
    
    def _try_direct_registration(self, email: str, password: str) -> Dict:
        """Try direct form submission as fallback"""
        try:
            # Get signup page
            signup_url = f"{self.base_url}/join/{self.referral_code}"
            response = self.session.get(signup_url, timeout=30)
            
            if response.status_code != 200:
                return {"success": False, "error": "Cannot load signup page"}
            
            # Look for form fields
            import re
            
            # Try to find CSRF token
            csrf_match = re.search(r'name="[^"]*csrf[^"]*".*?value="([^"]+)"', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            # Prepare form data
            form_data = {
                "email": email,
                "password": password,
                "confirm_password": password,
                "referral_code": self.referral_code,
                "agree_terms": "on",
                "csrf_token": csrf_token
            }
            
            # Try to submit
            submit_response = self.session.post(
                signup_url,
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30
            )
            
            if submit_response.status_code == 200:
                if "success" in submit_response.text.lower() or "verify" in submit_response.text.lower():
                    return {"success": True, "message": "Registration via form successful"}
            
            return {"success": False, "error": "Direct registration failed"}
            
        except Exception as e:
            return {"success": False, "error": f"Direct registration error: {str(e)}"}
    
    def _verify_account(self, email: str, verification_code: str) -> Dict:
        """Verify account with code"""
        try:
            verify_endpoints = [
                "/api/auth/verify",
                "/api/verify",
                "/auth/verify"
            ]
            
            verify_data = {
                "email": email,
                "code": verification_code
            }
            
            for endpoint in verify_endpoints:
                try:
                    response = self.session.post(
                        urljoin(self.base_url, endpoint),
                        json=verify_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Account verified: {email}")
                        return {"success": True, "message": "Account verified"}
                        
                except:
                    continue
            
            return {"success": False, "error": "Verification failed"}
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_multiple_accounts(self, count: int = 5) -> list:
        """Create multiple accounts"""
        results = []
        
        for i in range(count):
            logger.info(f"Creating account {i+1}/{count}")
            
            result = self.create_account()
            results.append(result)
            
            # Save progress
            self._save_progress(results)
            
            # Delay between accounts
            if i < count - 1:
                time.sleep(self._get_config_delay())
        
        return results
    
    def _save_progress(self, results: list):
        """Save progress to file"""
        try:
            with open("data/account_progress.json", "w") as f:
                json.dump({
                    "created_at": datetime.now().isoformat(),
                    "total": len(results),
                    "successful": sum(1 for r in results if r.get("success")),
                    "results": results
                }, f, indent=2)
        except:
            pass
    
    def _get_config_delay(self) -> int:
        """Get delay from config"""
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                return config.get("delay_between_accounts", 10)
        except:
            return 10

if __name__ == "__main__":
    # Test the referral bot
    import sys
    
    if len(sys.argv) > 1:
        referral_code = sys.argv[1]
        base_gmail = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        referral_code = "NPH90834"
        base_gmail = None
    
    bot = ReferralBot(referral_code, base_gmail)
    result = bot.create_account()
    print(json.dumps(result, indent=2))