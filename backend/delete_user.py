#!/usr/bin/env python3
"""
Delete a user by username (for cleaning up partial creates)
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

sys.path.insert(0, '/home/tw10548/majorv1/backend')

from app.models import User
from app.config import Settings

async def delete_user_by_username(username: str):
    """Delete a user by username"""
    
    settings = Settings()
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find user by username
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalars().first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        # Delete the user
        await session.delete(user)
        await session.commit()
        print(f"✅ User '{username}' deleted successfully")
    
    await engine.dispose()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(delete_user_by_username(username))
