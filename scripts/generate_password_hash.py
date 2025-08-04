#!/usr/bin/env python3
"""Generate password hash for admin user"""

from passlib.context import CryptContext
import sys

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_password_hash.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hash = pwd_context.hash(password)
    print(f"Password hash: {hash}")
    print(f"\nAdd this to your .env file:")
    print(f"ADMIN_PASSWORD_HASH={hash}")
