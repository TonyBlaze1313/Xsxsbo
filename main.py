#!/usr/bin/env python3
"""
SoSoValue Bot - Main Controller with Gmail Dot Trick
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SoSoValueBot:
    def __init__(self):
        self.config = self.load_config()
        self.referral_code = self.config.get("referral_code", "NPH90834")
        self.base_gmail = self.config.get("base_gmail", "")
        
        logger.info(f"SoSoValue Bot initialized")
        logger.info(f"Referral Code: {self.referral_code}")
        
        if self.base_gmail:
            logger.info(f"Gmail Mode: Active ({self.base_gmail})")
        else:
            logger.info("Gmail Mode: Not configured - using temporary emails")
    
    def load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "referral_code": "NPH90834",
            "base_url": "https://www.sosovalue.com",
            "base_gmail": "",
            "max_accounts": 50,
            "daily_batch_size": 5,
            "delay_between_accounts": 10,
            "max_retries": 3,
            "termux_mode": True,
            "log_level": "INFO"
        }
        
        try:
            with open("config.json", "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)
                logger.info("Loaded config.json")
        except FileNotFoundError:
            logger.warning("config.json not found, creating with defaults")
            with open("config.json", "w") as f:
                json.dump(default_config, f, indent=2)
        
        return default_config
    
    def create_accounts(self, count: int = 5):
        """Create new accounts"""
        try:
            from referral_bot import ReferralBot
        except ImportError as e:
            print(f"Error: {e}")
            print("Make sure referral_bot.py exists")
            return []
        
        logger.info(f"Creating {count} accounts...")
        
        bot = ReferralBot(self.referral_code, self.base_gmail)
        results = []
        
        for i in range(count):
            try:
                logger.info(f"Creating account {i+1}/{count}")
                
                # Create account
                result = bot.create_account()
                results.append(result)
                
                # Save progress
                if result.get("success"):
                    self.save_account(result)
                
                # Delay between accounts
                if i < count - 1:
                    delay = self.config["delay_between_accounts"]
                    logger.info(f"Waiting {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error creating account: {e}")
                results.append({"error": str(e)})
        
        # Generate report
        self.generate_report(results, "account_creation")
        return results
    
    def run_daily_tasks(self):
        """Run daily tasks for all accounts"""
        try:
            from task_bot import TaskBot
            from account_manager import AccountManager
        except ImportError as e:
            print(f"Error: {e}")
            print("Make sure task_bot.py and account_manager.py exist")
            return []
        
        logger.info("Running daily tasks...")
        
        # Get active accounts
        manager = AccountManager()
        accounts = manager.get_all_accounts()
        
        if not accounts:
            logger.warning("No accounts found in database")
            return []
        
        logger.info(f"Found {len(accounts)} accounts")
        
        # Process accounts
        results = []
        task_bot = TaskBot()
        
        for i, account in enumerate(accounts):
            try:
                logger.info(f"Processing account {i+1}/{len(accounts)}: {account['email']}")
                
                # Run tasks
                result = task_bot.complete_all_tasks(
                    email=account["email"],
                    password=account["password"]
                )
                
                # Update account
                if result.get("success"):
                    manager.update_account_points(
                        email=account["email"],
                        points_earned=result.get("total_xp", 0)
                    )
                
                results.append(result)
                
                # Delay between accounts
                if i < len(accounts) - 1:
                    time.sleep(5)
                    
            except Exception as e:
                logger.error(f"Error processing {account['email']}: {e}")
                results.append({"email": account["email"], "error": str(e)})
        
        manager.close()
        
        # Generate report
        self.generate_report(results, "daily_tasks")
        return results
    
    def save_account(self, account_data: Dict):
        """Save account to database"""
        try:
            from account_manager import AccountManager
            
            manager = AccountManager()
            
            if account_data.get("success"):
                manager.add_account(
                    email=account_data["email"],
                    password=account_data["password"],
                    referral_code=self.referral_code,
                    verified=account_data.get("verified", False),
                    verification_code=account_data.get("verification_code")
                )
                logger.info(f"Account saved: {account_data['email']}")
            else:
                logger.warning(f"Account not saved (failed): {account_data.get('email', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Error saving account: {e}")
    
    def generate_report(self, results: List[Dict], report_type: str):
        """Generate report file"""
        try:
            os.makedirs("data", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"data/report_{report_type}_{timestamp}.json"
            
            report = {
                "generated_at": datetime.now().isoformat(),
                "referral_code": self.referral_code,
                "total": len(results),
                "successful": sum(1 for r in results if r.get("success")),
                "results": results
            }
            
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
    
    def show_stats(self):
        """Show bot statistics"""
        try:
            from account_manager import AccountManager
        except ImportError as e:
            print(f"Error: {e}")
            return
        
        try:
            manager = AccountManager()
            stats = manager.get_stats()
            
            print("\n" + "="*60)
            print("📊 SoSoValue Bot Statistics")
            print("="*60)
            print(f"Total Accounts: {stats['total_accounts']}")
            print(f"Verified: {stats['verified_accounts']}")
            print(f"Pending: {stats['pending_accounts']}")
            print(f"Total Points: {stats['total_points']}")
            print(f"Referral Code: {self.referral_code}")
            
            if self.base_gmail:
                print(f"Gmail Mode: Active ({self.base_gmail})")
            else:
                print(f"Gmail Mode: Not configured")
            
            print("="*60)
            
            # Show recent accounts
            accounts = manager.get_all_accounts()[:5]
            if accounts:
                print("\n📝 Recent Accounts:")
                for acc in accounts:
                    status = "✓" if acc.get("verified") else "⏳"
                    print(f"  {status} {acc['email'][:25]:25} | {acc.get('points', 0):3} pts")
            
            manager.close()
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            print(f"Error: {e}")
    
    def setup_gmail(self):
        """Setup Gmail configuration"""
        print("\n🔧 Gmail Dot Trick Setup")
        print("="*60)
        
        base_email = input("Enter your Gmail address (e.g., johnbull@gmail.com): ").strip()
        
        if not base_email.endswith('@gmail.com'):
            print("❌ Must be a Gmail address")
            return
        
        # Update config
        self.config["base_gmail"] = base_email
        
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
        
        self.base_gmail = base_email
        
        print(f"\n✅ Gmail configured: {base_email}")
        print("   The bot will now use Gmail dot trick for account creation")
        print("   All verification emails will go to this address")
        
        # Show examples
        print("\n📧 Example variations:")
        from mail_generator import generate_gmail_variation
        for i in range(3):
            var = generate_gmail_variation(base_email)
            print(f"  {i+1}. {var}")

def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("🤖 SoSoValue Bot - Gmail Dot Trick Edition")
    print("="*60)
    print("1. Create New Accounts")
    print("2. Run Daily Tasks")
    print("3. Show Statistics")
    print("4. Setup Gmail")
    print("5. Export Accounts")
    print("6. Schedule Tasks")
    print("7. Exit")
    print("="*60)

def main():
    """Main entry point"""
    bot = SoSoValueBot()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            bot.create_accounts(count)
        elif command == "daily":
            bot.run_daily_tasks()
        elif command == "stats":
            bot.show_stats()
        elif command == "setup":
            bot.setup_gmail()
        else:
            print(f"Unknown command: {command}")
        return
    
    # Interactive mode
    while True:
        try:
            show_menu()
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                try:
                    count = int(input("How many accounts? (Default: 5): ") or "5")
                    bot.create_accounts(count)
                except ValueError:
                    print("Please enter a valid number")
                    
            elif choice == "2":
                bot.run_daily_tasks()
                
            elif choice == "3":
                bot.show_stats()
                
            elif choice == "4":
                bot.setup_gmail()
                
            elif choice == "5":
                from account_manager import AccountManager
                manager = AccountManager()
                filename = f"data/accounts_{datetime.now().strftime('%Y%m%d')}.csv"
                manager.export_to_csv(filename)
                print(f"Accounts exported to: {filename}")
                manager.close()
                
            elif choice == "6":
                print("\nTo schedule daily tasks:")
                print("1. Use cron (Linux/macOS) or Task Scheduler (Windows)")
                print("2. Run: python main.py daily")
                print("\nExample cron (runs daily at 9 AM):")
                print("0 9 * * * cd /path/to/bot && python main.py daily")
                
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("Invalid choice")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Display welcome message
    print("""
╔═══════════════════════════════════════════════╗
║      SoSoValue Bot - Gmail Dot Trick         ║
║      No Temp Email API Required              ║
╚═══════════════════════════════════════════════╝
    """)
    
    main()