#!/usr/bin/env python3
"""
Fix worked_hours calculation for all existing attendance records.
Only deduct break if total time >= break_duration + 120 minutes (2 hours buffer)
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime
import os

# Import models
import sys
sys.path.insert(0, '/home/tw10548/majorv1/backend')

from app.models import Attendance, CheckInOut
from app.config import Settings

async def fix_worked_hours():
    """Recalculate worked_hours for all attendance records"""
    
    settings = Settings()
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all attendance records with check-in and check-out times
        result = await session.execute(
            select(Attendance).where(
                (Attendance.in_time != None) & 
                (Attendance.out_time != None)
            )
        )
        records = result.scalars().all()
        
        print(f"Found {len(records)} attendance records to process...")
        updated = 0
        
        for att in records:
            try:
                # Parse times
                in_time = datetime.strptime(att.in_time, "%H:%M").time()
                out_time = datetime.strptime(att.out_time, "%H:%M").time()
                
                # Calculate total minutes
                in_minutes = in_time.hour * 60 + in_time.minute
                out_minutes = out_time.hour * 60 + out_time.minute
                
                # Handle day boundary (if checkout is next day)
                if out_minutes < in_minutes:
                    out_minutes += 24 * 60
                
                total_minutes = out_minutes - in_minutes
                
                # Get break minutes (default 60)
                break_minutes = att.break_minutes or 60
                
                # Only apply break if total time >= break + 120 minutes (3 hours total)
                if total_minutes >= (break_minutes + 120):
                    worked_minutes = total_minutes - break_minutes
                else:
                    worked_minutes = total_minutes
                
                worked_hours = round(worked_minutes / 60, 2)
                
                # Update if changed
                old_hours = att.worked_hours
                if old_hours != worked_hours:
                    att.worked_hours = worked_hours
                    await session.flush()
                    updated += 1
                    print(f"  ✓ Record {att.id}: {old_hours}h → {worked_hours}h (total: {total_minutes}min)")
            
            except Exception as e:
                print(f"  ✗ Error processing record {att.id}: {str(e)}")
        
        # Commit all changes
        if updated > 0:
            await session.commit()
            print(f"\n✅ Updated {updated} attendance records")
        else:
            print(f"\n✅ All records already correct")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_worked_hours())
