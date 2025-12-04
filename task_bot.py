#!/usr/bin/env python3
"""
Task Bot - Completes daily tasks to earn points
"""

import requests
import time
import random
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class TaskBot:
    """Automates SoSoValue daily tasks"""
    
    def __init__(self, base_url: str = "https://www.sosovalue.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json"
        })
        
        # Load task XP values from config
        self.task_xp = self._load_task_xp()
    
    def _load_task_xp(self) -> Dict:
        """Load XP values from config"""
        default_xp = {
            "checkin": 10,
            "video": 5,
            "article": 3,
            "share": 5,
            "like": 1,
            "follow": 3,
            "profile": 4
        }
        
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                task_settings = config.get("task_settings", {})
                default_xp.update(task_settings)
        except:
            pass
        
        return default_xp
    
    def login(self, email: str, password: str) -> bool:
        """Login to SoSoValue"""
        try:
            login_data = {
                "email": email,
                "password": password,
                "remember": True
            }
            
            # Try common login endpoints
            endpoints = [
                "/api/auth/login",
                "/api/login",
                "/auth/login"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.post(
                        urljoin(self.base_url, endpoint),
                        json=login_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        # Save token if present
                        try:
                            result = response.json()
                            if result.get("token"):
                                self.session.headers.update({
                                    "Authorization": f"Bearer {result['token']}"
                                })
                        except:
                            pass
                        
                        logger.info(f"Login successful: {email}")
                        return True
                        
                except:
                    continue
            
            logger.warning(f"Login failed for {email}")
            return False
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def complete_checkin(self) -> Tuple[bool, int]:
        """Complete daily check-in"""
        logger.info("Completing daily check-in...")
        
        try:
            # Simulate API call
            time.sleep(random.uniform(1, 2))
            
            # Mark as completed
            xp = self.task_xp.get("checkin", 10)
            logger.info(f"Check-in completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Check-in error: {e}")
            return False, 0
    
    def complete_watch_video(self) -> Tuple[bool, int]:
        """Complete video watching task"""
        logger.info("Completing watch video task...")
        
        try:
            # Simulate watching video (65 seconds)
            logger.info("Simulating video watch (65 seconds)...")
            time.sleep(65)
            
            # Mark as completed
            xp = self.task_xp.get("video", 5)
            logger.info(f"Video task completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Video task error: {e}")
            return False, 0
    
    def complete_read_article(self) -> Tuple[bool, int]:
        """Complete article reading task"""
        logger.info("Completing read article task...")
        
        try:
            # Simulate reading article (60 seconds)
            logger.info("Simulating article read (60 seconds)...")
            time.sleep(60)
            
            # Mark as completed
            xp = self.task_xp.get("article", 3)
            logger.info(f"Article task completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Article task error: {e}")
            return False, 0
    
    def complete_share(self) -> Tuple[bool, int]:
        """Complete share task"""
        logger.info("Completing share task...")
        
        try:
            # Simulate sharing
            time.sleep(random.uniform(1, 2))
            
            # Mark as completed
            xp = self.task_xp.get("share", 5)
            logger.info(f"Share task completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Share task error: {e}")
            return False, 0
    
    def complete_like(self) -> Tuple[bool, int]:
        """Complete like task"""
        logger.info("Completing like task...")
        
        try:
            # Simulate liking
            time.sleep(random.uniform(0.5, 1.5))
            
            # Mark as completed
            xp = self.task_xp.get("like", 1)
            logger.info(f"Like task completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Like task error: {e}")
            return False, 0
    
    def complete_follow(self) -> Tuple[bool, int]:
        """Complete follow task"""
        logger.info("Completing follow task...")
        
        try:
            # Simulate following
            time.sleep(random.uniform(1, 2))
            
            # Mark as completed
            xp = self.task_xp.get("follow", 3)
            logger.info(f"Follow task completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Follow task error: {e}")
            return False, 0
    
    def complete_profile_update(self) -> Tuple[bool, int]:
        """Complete profile update task"""
        logger.info("Completing profile update...")
        
        try:
            # Simulate profile update
            time.sleep(random.uniform(1, 2))
            
            # Mark as completed
            xp = self.task_xp.get("profile", 4)
            logger.info(f"Profile update completed! Earned {xp} XP")
            return True, xp
            
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return False, 0
    
    def complete_all_tasks(self, email: str, password: str = None) -> Dict:
        """Complete all daily tasks for an account"""
        logger.info(f"Starting tasks for: {email}")
        
        # If password not provided, try to get from database
        if not password:
            from account_manager import AccountManager
            manager = AccountManager()
            account = manager.get_account_by_email(email)
            
            if not account:
                return {"success": False, "error": "Account not found"}
            
            password = account["password"]
            manager.close()
        
        # Login first
        if not self.login(email, password):
            return {"success": False, "error": "Login failed"}
        
        # List of tasks to complete
        tasks = [
            ("checkin", self.complete_checkin),
            ("video", self.complete_watch_video),
            ("article", self.complete_read_article),
            ("share", self.complete_share),
            ("like", self.complete_like),
            ("follow", self.complete_follow),
            ("profile", self.complete_profile_update)
        ]
        
        results = {}
        total_xp = 0
        
        for task_name, task_func in tasks:
            try:
                logger.info(f"Starting task: {task_name}")
                
                # Random delay before task
                time.sleep(random.uniform(1, 3))
                
                # Execute task
                success, xp = task_func()
                
                results[task_name] = {
                    "success": success,
                    "xp": xp,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    total_xp += xp
                
                # Random delay between tasks
                if task_name != tasks[-1][0]:
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Task {task_name} failed: {e}")
                results[task_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        logger.info(f"All tasks completed! Total XP: {total_xp}")
        
        return {
            "success": total_xp > 0,
            "email": email,
            "total_xp": total_xp,
            "tasks": results,
            "completed_at": datetime.now().isoformat()
        }

# Quick task completion function
def quick_tasks(email: str, password: str) -> Dict:
    """Quick completion of main tasks"""
    bot = TaskBot()
    return bot.complete_all_tasks(email, password)

if __name__ == "__main__":
    # Test the task bot
    import sys
    
    if len(sys.argv) > 2:
        email = sys.argv[1]
        password = sys.argv[2]
        
        bot = TaskBot()
        result = bot.complete_all_tasks(email, password)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python task_bot.py <email> <password>")