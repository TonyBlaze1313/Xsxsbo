#!/usr/bin/env python3
"""
Account Manager - Database management for accounts
"""

import sqlite3
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AccountManager:
    """Manages accounts in SQLite database"""
    
    def __init__(self, db_path: str = "accounts.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                referral_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified BOOLEAN DEFAULT FALSE,
                verification_code TEXT,
                points INTEGER DEFAULT 0,
                last_task_run TIMESTAMP,
                status TEXT DEFAULT 'active',
                cookies TEXT,
                notes TEXT
            )
        ''')
        
        # Task history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                task_type TEXT NOT NULL,
                xp_earned INTEGER DEFAULT 0,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info("Database initialized")
    
    def add_account(self, email: str, password: str, referral_code: str, 
                   verified: bool = False, verification_code: str = None, 
                   cookies: str = None):
        """Add new account to database"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO accounts 
                (email, password, referral_code, verified, verification_code, cookies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password, referral_code, verified, verification_code, cookies))
            
            self.conn.commit()
            logger.info(f"Account added: {email}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"Account already exists: {email}")
            return False
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            return False
    
    def get_account_by_email(self, email: str) -> Optional[Dict]:
        """Get account by email"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_accounts(self) -> List[Dict]:
        """Get all accounts"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_verified_accounts(self) -> List[Dict]:
        """Get verified accounts"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE verified = 1 AND status = "active"')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_accounts(self) -> List[Dict]:
        """Get pending accounts (not verified)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE verified = 0')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_account_points(self, email: str, points_earned: int):
        """Update account points"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE accounts 
            SET points = points + ?, last_task_run = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (points_earned, email))
        
        self.conn.commit()
        logger.info(f"Updated points for {email}: +{points_earned}")
    
    def record_task_completion(self, email: str, task_type: str, xp_earned: int, details: Dict = None):
        """Record task completion in history"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO task_history (email, task_type, xp_earned, details)
            VALUES (?, ?, ?, ?)
        ''', (email, task_type, xp_earned, json.dumps(details) if details else None))
        
        self.conn.commit()
    
    def get_accounts_needing_tasks(self, hours_since: int = 20) -> List[Dict]:
        """Get accounts that haven't run tasks in specified hours"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM accounts 
            WHERE verified = 1 
            AND status = 'active'
            AND (
                last_task_run IS NULL 
                OR datetime(last_task_run) < datetime('now', ?)
            )
        ''', (f'-{hours_since} hours',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM accounts')
        total_accounts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE verified = 1')
        verified_accounts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE verified = 0')
        pending_accounts = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(points) FROM accounts')
        total_points = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            SELECT referral_code, COUNT(*) as count 
            FROM accounts 
            GROUP BY referral_code 
            ORDER BY count DESC
        ''')
        
        referral_stats = []
        for row in cursor.fetchall():
            referral_stats.append({
                "code": row[0],
                "count": row[1]
            })
        
        # Calculate verification rate
        verification_rate = (verified_accounts / total_accounts * 100) if total_accounts > 0 else 0
        
        return {
            "total_accounts": total_accounts,
            "verified_accounts": verified_accounts,
            "pending_accounts": pending_accounts,
            "total_points": total_points,
            "verification_rate": verification_rate,
            "referral_stats": referral_stats
        }
    
    def export_to_csv(self, filename: str):
        """Export accounts to CSV"""
        accounts = self.get_all_accounts()
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if accounts:
                fieldnames = accounts[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(accounts)
        
        logger.info(f"Exported {len(accounts)} accounts to {filename}")
    
    def export_to_json(self, filename: str):
        """Export accounts to JSON"""
        accounts = self.get_all_accounts()
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "exported_at": datetime.now().isoformat(),
                "total_accounts": len(accounts),
                "accounts": accounts
            }, f, indent=2)
        
        logger.info(f"Exported {len(accounts)} accounts to {filename}")
    
    def delete_account(self, email: str):
        """Delete account from database"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE email = ?', (email,))
        cursor.execute('DELETE FROM task_history WHERE email = ?', (email,))
        self.conn.commit()
        logger.info(f"Deleted account: {email}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Utility functions
def show_dashboard():
    """Display account dashboard"""
    manager = AccountManager()
    stats = manager.get_stats()
    
    print("\n" + "="*60)
    print("📊 ACCOUNT DASHBOARD")
    print("="*60)
    print(f"Total Accounts: {stats['total_accounts']}")
    print(f"Verified Accounts: {stats['verified_accounts']}")
    print(f"Pending Verification: {stats['pending_accounts']}")
    print(f"Total Points: {stats['total_points']}")
    print(f"Verification Rate: {stats['verification_rate']:.1f}%")
    
    if stats['referral_stats']:
        print(f"\n🎯 Referral Codes:")
        for ref in stats['referral_stats']:
            print(f"  {ref['code']}: {ref['count']} accounts")
    
    # Show recent accounts
    accounts = manager.get_all_accounts()[:5]
    if accounts:
        print(f"\n📝 Recent Accounts:")
        for acc in accounts:
            status = "✓" if acc.get("verified") else "⏳"
            points = acc.get("points", 0)
            print(f"  {status} {acc['email'][:25]:25} | {points:4} pts")
    
    manager.close()
    print("="*60)

if __name__ == "__main__":
    show_dashboard()