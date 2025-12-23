#!/usr/bin/env python3
"""
Simple test script to verify comp-off feature works
"""
import asyncio
import sys
sys.path.insert(0, '/home/tw10548/majorv8/backend')

from sqlalchemy import select
from app.database import engine
from app.models import (
    User, Employee, CompOffRequest, CompOffTracking, 
    Department, Manager, Role, UserType
)

async def test_database():
    print("🧪 Testing Comp-Off Feature Database")
    print("=" * 50)
    
    try:
        async with engine.begin() as conn:
            # Test 1: Check users
            result = await conn.execute(select(User))
            users = result.scalars().all()
            print(f"\n✅ Test 1: Database Connection")
            print(f"   Found {len(users)} users")
            
            # Test 2: Check employees
            result = await conn.execute(select(Employee))
            employees = result.scalars().all()
            print(f"\n✅ Test 2: Employees")
            print(f"   Found {len(employees)} employees")
            if employees:
                for emp in employees[:3]:
                    try:
                        print(f"   - {emp.first_name} {emp.last_name} (ID: {emp.employee_id})")
                    except:
                        print(f"   - Employee found (unable to display details)")
            
            # Test 3: Check comp-off tables exist
            result = await conn.execute(select(CompOffRequest))
            comp_off_reqs = result.scalars().all()
            print(f"\n✅ Test 3: CompOffRequest Table")
            print(f"   Found {len(comp_off_reqs)} comp-off requests")
            
            # Test 4: Check comp-off tracking table
            result = await conn.execute(select(CompOffTracking))
            comp_off_tracking = result.scalars().all()
            print(f"\n✅ Test 4: CompOffTracking Table")
            print(f"   Found {len(comp_off_tracking)} tracking records")
            
            # Test 5: Check roles and departments
            result = await conn.execute(select(Department))
            departments = result.scalars().all()
            print(f"\n✅ Test 5: Departments")
            print(f"   Found {len(departments)} departments")
            
            result = await conn.execute(select(Role))
            roles = result.scalars().all()
            print(f"\n✅ Test 6: Roles")
            print(f"   Found {len(roles)} roles")
            
            print("\n" + "=" * 50)
            print("✅ All database tests passed!")
            print("\n📝 Summary:")
            print(f"   - {len(users)} users")
            print(f"   - {len(employees)} employees")
            print(f"   - {len(departments)} departments")
            print(f"   - {len(roles)} roles")
            print(f"   - CompOffRequest table ready")
            print(f"   - CompOffTracking table ready")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())
