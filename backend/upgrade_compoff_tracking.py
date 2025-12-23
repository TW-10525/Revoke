#!/usr/bin/env python3
"""
Migration script to add monthly expiry tracking to comp_off_tracking table
and create comp_off_details table for detailed audit trail
"""

import asyncio
from sqlalchemy import text
from app.database import engine

async def upgrade_database():
    """Run database migrations for comp-off tracking enhancement"""
    
    async with engine.begin() as conn:
        # Check if columns already exist
        try:
            result = await conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'comp_off_tracking' AND column_name = 'earned_date'
            """))
            if result.scalar():
                print("✓ comp_off_tracking already has earned_date column")
                return
        except Exception as e:
            print(f"Note: {e}")

        try:
            # Add new columns to comp_off_tracking
            print("Adding new columns to comp_off_tracking...")
            await conn.execute(text("""
                ALTER TABLE comp_off_tracking
                ADD COLUMN IF NOT EXISTS earned_date TIMESTAMP,
                ADD COLUMN IF NOT EXISTS expired_days INTEGER DEFAULT 0
            """))
            print("✓ Added earned_date and expired_days columns to comp_off_tracking")
            await conn.commit()
        except Exception as e:
            print(f"Error adding columns: {e}")
            await conn.rollback()

        try:
            # Create comp_off_details table
            print("Creating comp_off_details table...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS comp_off_details (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER NOT NULL,
                    tracking_id INTEGER NOT NULL,
                    type VARCHAR(50) DEFAULT 'earned',
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    earned_month VARCHAR(7),
                    expired_at TIMESTAMP,
                    notes VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_compoff_detail_employee FOREIGN KEY (employee_id) 
                        REFERENCES employees(id) ON DELETE CASCADE,
                    CONSTRAINT fk_compoff_detail_tracking FOREIGN KEY (tracking_id) 
                        REFERENCES comp_off_tracking(id) ON DELETE CASCADE
                )
            """))
            print("✓ Created comp_off_details table")
            await conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")
            await conn.rollback()

        # Create indexes for performance
        try:
            print("Creating indexes...")
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_compoff_details_employee 
                ON comp_off_details(employee_id)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_compoff_details_earned_month 
                ON comp_off_details(earned_month)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_compoff_details_type 
                ON comp_off_details(type)
            """))
            print("✓ Created indexes for comp_off_details")
            await conn.commit()
        except Exception as e:
            print(f"Note: {e}")

        print("\n✓ Database migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(upgrade_database())
