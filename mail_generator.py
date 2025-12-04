#!/usr/bin/env python3
"""
Gmail Dot Trick Email Generator
Main email generation module for SoSoValue Bot
"""

import random
import string
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def generate_gmail_variation(base_gmail: str) -> str:
    """
    Generate a Gmail dot trick variation
    
    Args:
        base_gmail: Your real Gmail address (e.g., johnbull@gmail.com)
    
    Returns:
        Gmail variation with dots added
    """
    if not base_gmail or "@gmail.com" not in base_gmail:
        # Fallback to temporary email
        return generate_temp_email()
    
    # Extract local part
    local_part = base_gmail.split("@")[0]
    
    # Decide how many dots to add (1-3)
    num_dots = random.randint(1, min(3, len(local_part) - 1))
    
    # Convert to list for dot insertion
    chars = list(local_part)
    
    # Get available positions (not at start or end)
    available_positions = list(range(1, len(chars)))
    
    # Randomly select positions for dots
    if num_dots > len(available_positions):
        num_dots = len(available_positions)
    
    dot_positions = random.sample(available_positions, num_dots)
    dot_positions.sort(reverse=True)  # Sort in reverse for insertion
    
    # Insert dots at selected positions
    for pos in dot_positions:
        chars.insert(pos, '.')
    
    # Create the new email
    new_local = ''.join(chars)
    email = f"{new_local}@gmail.com"
    
    logger.info(f"Generated Gmail variation: {email} -> {base_gmail}")
    return email

def generate_temp_email() -> str:
    """Generate a temporary email address (fallback)"""
    # Generate random username
    adjectives = ['quick', 'fast', 'smart', 'clever', 'bright', 'sharp', 'wise', 'bold']
    nouns = ['fox', 'wolf', 'bear', 'eagle', 'hawk', 'lion', 'tiger', 'owl']
    numbers = ''.join(random.choices(string.digits, k=3))
    
    username = f"{random.choice(adjectives)}{random.choice(nouns)}{numbers}"
    
    # Random domain
    domains = [
        'tempmail.com',
        '10minutemail.net',
        'mailinator.com',
        'guerrillamail.com',
        'yopmail.com'
    ]
    
    email = f"{username}@{random.choice(domains)}"
    logger.info(f"Generated temporary email: {email}")
    return email

def getmails(count: int = 1):
    """
    Generate one or more email addresses
    Compatible with old code
    
    Args:
        count: Number of emails to generate
    
    Returns:
        Single email if count=1, list otherwise
    """
    # Try to load config to get base Gmail
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            base_gmail = config.get("base_gmail", "")
    except:
        base_gmail = ""
    
    emails = []
    for _ in range(count):
        if base_gmail:
            email = generate_gmail_variation(base_gmail)
        else:
            email = generate_temp_email()
        emails.append(email)
    
    if count == 1:
        return emails[0]
    return emails

def get_verification_code(email: str = None) -> Optional[str]:
    """
    Get verification code from user input
    
    Args:
        email: Email address that received the code
    
    Returns:
        6-digit verification code or None
    """
    try:
        print(f"\n" + "="*50)
        print("📧 VERIFICATION REQUIRED")
        print("="*50)
        
        if email:
            if "@gmail.com" in email:
                # Try to show the real Gmail
                try:
                    with open("config.json", "r") as f:
                        config = json.load(f)
                        base_gmail = config.get("base_gmail", "")
                        if base_gmail:
                            print(f"Gmail variation: {email}")
                            print(f"Real inbox: {base_gmail}")
                        else:
                            print(f"Email: {email}")
                except:
                    print(f"Email: {email}")
            else:
                print(f"Email: {email}")
        
        print("\nInstructions:")
        print("1. Check your email inbox")
        print("2. Look for verification email from SoSoValue")
        print("3. Enter the 6-digit code below")
        print("="*50)
        
        while True:
            code = input("\nEnter 6-digit verification code (or 'skip'): ").strip()
            
            if code.lower() == 'skip':
                print("Skipping verification...")
                return None
            
            if code.isdigit() and len(code) == 6:
                print(f"✅ Code accepted: {code}")
                return code
            else:
                print("❌ Invalid. Must be 6 digits.")
                
    except KeyboardInterrupt:
        print("\n\nCode entry cancelled")
        return None
    except Exception as e:
        logger.error(f"Error getting verification code: {e}")
        return None

def generate_multiple_variations(base_gmail: str, count: int) -> List[str]:
    """Generate multiple Gmail variations"""
    variations = []
    for i in range(count):
        var = generate_gmail_variation(base_gmail)
        variations.append(var)
    return variations

# Test function
if __name__ == "__main__":
    # Test the generator
    print("Testing Gmail Dot Trick Generator...")
    
    # Test with example Gmail
    test_gmail = "johnbull@gmail.com"
    
    print(f"\nBase Gmail: {test_gmail}")
    print("\nGenerated variations:")
    for i in range(5):
        variation = generate_gmail_variation(test_gmail)
        print(f"  {i+1}. {variation}")
    
    print("\nAll these emails will go to: johnbull@gmail.com")