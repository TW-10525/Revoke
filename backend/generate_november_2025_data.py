#!/usr/bin/env python3
"""
Complete Database Cleanup and November 2025 Mock Data Generator
- Removes all mock data from database
- Creates fresh data for November 2025
- Includes: Users, Departments, Roles, Shifts, Schedules, Attendance, Leave, OT, Comp-Off
"""

import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.models import (
    User, UserType, Department, Manager, Employee, Role, Shift,
    Schedule, Attendance, OvertimeRequest, OvertimeStatus, LeaveRequest,
    LeaveStatus, CompOffRequest, CompOffTracking
)
from app.auth import get_password_hash


async def cleanup_database(session):
    """Remove all mock data from database"""
    print("\n🧹 CLEARING DATABASE...")
    print("=" * 80)
    
    tables_to_clear = [
        'comp_off_details', 'comp_off_tracking', 'comp_off_requests',
        'overtime_worked', 'overtime_requests', 'attendance', 'check_ins',
        'schedules', 'leave_requests', 'employees', 'managers', 'roles',
        'shifts', 'departments', 'users'
    ]
    
    for table in tables_to_clear:
        try:
            await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            await session.commit()
            print(f"  ✅ {table}")
        except Exception as e:
            await session.rollback()
            pass
    
    print("✅ Database cleared successfully\n")


async def create_november_2025_data():
    """Create comprehensive November 2025 mock data"""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("=" * 80)
        print("🌱 GENERATING NOVEMBER 2025 MOCK DATA")
        print("=" * 80)
        
        # Clean database first
        await cleanup_database(session)
        
        # 1. Create Departments
        print("\n📍 Creating departments...")
        departments = []
        dept_configs = [
            ("001", "IT Department"),
            ("002", "HR Department"),
            ("003", "Finance Department"),
        ]
        
        for dept_id, dept_name in dept_configs:
            dept = Department(
                dept_id=dept_id,
                name=dept_name,
                description=f"{dept_name} Description"
            )
            session.add(dept)
            departments.append(dept)
        
        await session.flush()
        print(f"✅ Created {len(departments)} departments")
        
        # 2. Create Roles
        print("\n🎯 Creating roles...")
        roles_dict = {}
        
        for dept in departments:
            role_names = ["Developer", "Manager", "Analyst"]
            for role_name in role_names:
                role = Role(
                    name=role_name,
                    description=f"{role_name} Role",
                    department_id=dept.id,
                    priority=50,
                    break_minutes=60,
                    weekend_required=False
                )
                session.add(role)
                if dept.dept_id not in roles_dict:
                    roles_dict[dept.dept_id] = {}
                roles_dict[dept.dept_id][role_name] = role
        
        await session.flush()
        print(f"✅ Created roles for all departments")
        
        # 3. Create Shifts
        print("\n⏰ Creating shifts...")
        shifts_dict = {}
        shift_configs = [
            ("Morning", "09:00", "18:00"),
            ("Afternoon", "13:00", "22:00"),
            ("Evening", "17:00", "02:00"),
        ]
        
        for dept in departments:
            shifts_dict[dept.dept_id] = {}
            dev_role = roles_dict[dept.dept_id]["Developer"]
            
            for shift_name, start_time, end_time in shift_configs:
                shift = Shift(
                    name=shift_name,
                    start_time=start_time,
                    end_time=end_time,
                    role_id=dev_role.id
                )
                session.add(shift)
                shifts_dict[dept.dept_id][shift_name] = shift
        
        await session.flush()
        print(f"✅ Created shifts for all departments")
        
        # 4. Create Manager
        print("\n👨‍💼 Creating manager...")
        manager_user = User(
            username="manager_nov",
            email="manager@nov.com",
            hashed_password=get_password_hash("password123"),
            full_name="November Manager",
            user_type=UserType.MANAGER,
            is_active=True
        )
        session.add(manager_user)
        await session.flush()
        
        manager = Manager(
            user_id=manager_user.id,
            department_id=departments[0].id
        )
        session.add(manager)
        await session.flush()
        print(f"✅ Manager created: {manager_user.full_name}")
        
        # 5. Create Employees
        print("\n👥 Creating employees...")
        employees = []
        employee_configs = [
            ("EMP001", "Alice", "Johnson", "alice@nov.com"),
            ("EMP002", "Bob", "Smith", "bob@nov.com"),
            ("EMP003", "Charlie", "Brown", "charlie@nov.com"),
        ]
        
        for emp_id, first_name, last_name, email in employee_configs:
            emp_user = User(
                username=f"emp_{emp_id}",
                email=email,
                hashed_password=get_password_hash("password123"),
                full_name=f"{first_name} {last_name}",
                user_type=UserType.EMPLOYEE,
                is_active=True
            )
            session.add(emp_user)
            await session.flush()
            
            employee = Employee(
                user_id=emp_user.id,
                department_id=departments[0].id,
                role_id=roles_dict[departments[0].dept_id]["Developer"].id,
                employee_id=emp_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone="1234567890",
                hire_date=date(2024, 1, 1),
                paid_leave_per_year=12,
                is_active=True
            )
            session.add(employee)
            employees.append(employee)
        
        await session.flush()
        print(f"✅ Created {len(employees)} employees")
        
        # 6. Initialize Comp-Off Tracking
        print("\n💰 Initializing comp-off tracking...")
        for emp in employees:
            comp_tracking = CompOffTracking(
                employee_id=emp.id,
                earned_days=5,
                used_days=1,
                available_days=4
            )
            session.add(comp_tracking)
        await session.flush()
        print(f"✅ Comp-off tracking initialized for all employees")
        
        # 7. Create Schedules for November 2025
        print("\n📅 Creating schedules for November 2025...")
        nov_start = date(2025, 11, 1)
        nov_end = date(2025, 11, 30)
        shift_list = list(shifts_dict[departments[0].dept_id].values())
        
        total_schedules = 0
        current_date = nov_start
        
        while current_date <= nov_end:
            if current_date.weekday() < 5:  # Monday-Friday
                for emp_idx, emp in enumerate(employees):
                    shift = shift_list[emp_idx % len(shift_list)]
                    sched = Schedule(
                        employee_id=emp.id,
                        department_id=departments[0].id,
                        role_id=emp.role_id,
                        shift_id=shift.id,
                        date=current_date,
                        start_time=shift.start_time,
                        end_time=shift.end_time,
                        status="scheduled"
                    )
                    session.add(sched)
                    total_schedules += 1
            
            current_date += timedelta(days=1)
        
        await session.flush()
        print(f"✅ Created {total_schedules} work schedules for November 2025")
        
        # 8. Create Attendance Records
        print("\n✅ Creating attendance records with check-in/check-out...")
        
        attendance_records = []
        # Create realistic attendance data for November
        nov_attendance_data = {
            # Employee 0 (Alice)
            0: [
                (date(2025, 11, 3), "08:45", "18:30", 0.5),
                (date(2025, 11, 4), "09:00", "19:00", 1.0),
                (date(2025, 11, 5), "09:15", "18:15", 0.0),
                (date(2025, 11, 6), "08:30", "20:00", 2.0),
                (date(2025, 11, 7), "09:00", "18:00", 0.0),
                (date(2025, 11, 10), "08:50", "18:45", 0.75),
                (date(2025, 11, 11), "09:05", "17:55", 0.0),
                (date(2025, 11, 12), "09:00", "19:30", 1.5),
                (date(2025, 11, 13), "08:40", "18:40", 1.0),
                (date(2025, 11, 14), "09:00", "18:00", 0.0),
                (date(2025, 11, 17), "09:10", "20:00", 1.75),
                (date(2025, 11, 18), "09:00", "18:00", 0.0),
                (date(2025, 11, 19), "08:30", "18:45", 1.25),
                (date(2025, 11, 20), "09:00", "19:00", 1.0),
                (date(2025, 11, 21), "09:00", "18:00", 0.0),
                (date(2025, 11, 24), "08:55", "18:30", 0.5),
                (date(2025, 11, 25), "09:00", "20:00", 1.5),
                (date(2025, 11, 26), "09:00", "18:00", 0.0),
                (date(2025, 11, 27), "09:15", "19:15", 1.0),
                (date(2025, 11, 28), "09:00", "18:30", 0.5),
            ],
            # Employee 1 (Bob)
            1: [
                (date(2025, 11, 3), "09:00", "18:00", 0.0),
                (date(2025, 11, 4), "08:45", "18:45", 0.75),
                (date(2025, 11, 5), "09:00", "19:00", 1.0),
                (date(2025, 11, 6), "09:05", "18:20", 0.0),
                (date(2025, 11, 7), "08:30", "20:00", 1.75),
                (date(2025, 11, 10), "09:00", "18:00", 0.0),
                (date(2025, 11, 11), "08:50", "19:30", 1.5),
                (date(2025, 11, 12), "09:00", "18:00", 0.0),
                (date(2025, 11, 13), "09:10", "20:00", 1.75),
                (date(2025, 11, 14), "09:00", "18:30", 0.5),
                (date(2025, 11, 17), "08:45", "18:00", 0.0),
                (date(2025, 11, 18), "09:00", "19:00", 1.0),
                (date(2025, 11, 19), "08:30", "18:15", 0.0),
                (date(2025, 11, 20), "09:15", "20:30", 2.0),
                (date(2025, 11, 21), "09:00", "18:00", 0.0),
                (date(2025, 11, 24), "08:50", "18:45", 0.75),
                (date(2025, 11, 25), "09:00", "18:00", 0.0),
                (date(2025, 11, 26), "09:05", "19:15", 1.0),
                (date(2025, 11, 27), "09:00", "18:30", 0.5),
                (date(2025, 11, 28), "08:45", "20:00", 1.5),
            ],
            # Employee 2 (Charlie)
            2: [
                (date(2025, 11, 3), "08:50", "19:00", 1.0),
                (date(2025, 11, 4), "09:00", "18:00", 0.0),
                (date(2025, 11, 5), "08:30", "18:45", 1.25),
                (date(2025, 11, 6), "09:00", "19:00", 1.0),
                (date(2025, 11, 7), "09:10", "18:15", 0.0),
                (date(2025, 11, 10), "08:45", "20:00", 1.75),
                (date(2025, 11, 11), "09:00", "18:00", 0.0),
                (date(2025, 11, 12), "08:50", "18:30", 0.5),
                (date(2025, 11, 13), "09:00", "19:30", 1.5),
                (date(2025, 11, 14), "09:00", "18:00", 0.0),
                (date(2025, 11, 17), "08:30", "18:15", 0.0),
                (date(2025, 11, 18), "09:15", "20:00", 1.75),
                (date(2025, 11, 19), "09:00", "18:00", 0.0),
                (date(2025, 11, 20), "08:45", "18:45", 0.75),
                (date(2025, 11, 21), "09:00", "19:00", 1.0),
                (date(2025, 11, 24), "09:00", "18:00", 0.0),
                (date(2025, 11, 25), "08:50", "18:30", 0.5),
                (date(2025, 11, 26), "09:00", "20:00", 1.5),
                (date(2025, 11, 27), "09:05", "18:15", 0.0),
                (date(2025, 11, 28), "09:00", "19:00", 1.0),
            ],
        }
        
        for emp_idx, emp in enumerate(employees):
            for att_date, check_in, check_out, ot_hours in nov_attendance_data.get(emp_idx, []):
                attendance = Attendance(
                    employee_id=emp.id,
                    date=att_date,
                    in_time=check_in,
                    out_time=check_out,
                    status="onTime",
                    overtime_hours=ot_hours,
                    notes=f"Check-in: {check_in}, Check-out: {check_out}, OT: {ot_hours}h"
                )
                session.add(attendance)
                attendance_records.append((emp.employee_id, att_date, ot_hours))
        
        await session.flush()
        total_attendance = sum(len(records) for records in nov_attendance_data.values())
        total_ot_hours = sum(sum(record[3] for record in nov_attendance_data[emp_idx]) 
                            for emp_idx in nov_attendance_data)
        print(f"✅ Created {total_attendance} attendance records (Total OT: {total_ot_hours:.1f}h)")
        
        # 9. Create Leave Requests
        print("\n🏖️ Creating leave requests...")
        leave_requests = [
            # Employee 0 (Alice)
            (0, date(2025, 11, 10), date(2025, 11, 10), "paid", "approved", "Doctor appointment"),
            (0, date(2025, 11, 24), date(2025, 11, 24), "comp_off", "approved", "Using earned comp-off"),
            # Employee 1 (Bob)
            (1, date(2025, 11, 13), date(2025, 11, 13), "unpaid", "approved", "Personal reason"),
            (1, date(2025, 11, 26), date(2025, 11, 26), "paid", "approved", "Medical checkup"),
            # Employee 2 (Charlie)
            (2, date(2025, 11, 5), date(2025, 11, 5), "paid", "approved", "Anniversary"),
            (2, date(2025, 11, 19), date(2025, 11, 19), "unpaid", "approved", "Family event"),
        ]
        
        for emp_idx, start, end, leave_type, status, reason in leave_requests:
            leave_req = LeaveRequest(
                employee_id=employees[emp_idx].id,
                manager_id=manager.id,
                start_date=start,
                end_date=end,
                leave_type=leave_type,
                duration_type="full_day",
                status=LeaveStatus[status.upper()],
                reason=reason,
                created_at=datetime.now()
            )
            session.add(leave_req)
        
        await session.flush()
        print(f"✅ Created {len(leave_requests)} leave requests")
        print(f"   - Alice: 1 Paid, 1 Comp-Off")
        print(f"   - Bob: 1 Unpaid, 1 Paid")
        print(f"   - Charlie: 1 Paid, 1 Unpaid")
        
        # 10. Create Comp-Off Requests (usage)
        print("\n🎁 Creating comp-off usage requests...")
        comp_off_usage_requests = [
            (0, date(2025, 11, 24), "Using earned comp-off"),
            (1, date(2025, 11, 14), "Taking comp-off"),
            (2, date(2025, 11, 10), "Compensatory day off"),
        ]
        
        for emp_idx, comp_date, reason in comp_off_usage_requests:
            comp_req = CompOffRequest(
                employee_id=employees[emp_idx].id,
                manager_id=manager.id,
                comp_off_date=comp_date,
                reason=reason,
                status=LeaveStatus.APPROVED
            )
            session.add(comp_req)
        
        await session.flush()
        print(f"✅ Created {len(comp_off_usage_requests)} comp-off usage requests")
        
        # 11. Create Overtime Requests
        print("\n⏱️ Creating overtime requests...")
        ot_requests = [
            (0, date(2025, 11, 4), "09:00", "19:00", 1.0, "project deadline", "approved"),
            (0, date(2025, 11, 6), "09:00", "20:00", 2.0, "client meeting prep", "approved"),
            (0, date(2025, 11, 12), "09:00", "19:30", 1.5, "urgent bug fix", "approved"),
            (1, date(2025, 11, 7), "13:00", "20:00", 1.75, "system upgrade", "approved"),
            (1, date(2025, 11, 20), "13:00", "21:00", 2.0, "database migration", "approved"),
            (2, date(2025, 11, 3), "17:00", "20:30", 1.0, "evening support", "approved"),
            (2, date(2025, 11, 25), "17:00", "21:30", 1.5, "deployment", "approved"),
        ]
        
        for emp_idx, ot_date, start_time, end_time, hours, reason, status in ot_requests:
            ot_req = OvertimeRequest(
                employee_id=employees[emp_idx].id,
                manager_id=manager_user.id,
                request_date=ot_date,
                from_time=start_time,
                to_time=end_time,
                request_hours=hours,
                reason=reason,
                status=OvertimeStatus[status.upper()]
            )
            session.add(ot_req)
        
        await session.flush()
        total_ot_req = sum(record[4] for record in ot_requests)
        print(f"✅ Created {len(ot_requests)} overtime requests (total: {total_ot_req:.1f} hours)")
        
        # Final commit
        await session.commit()
        
        print("\n" + "=" * 80)
        print("✅ NOVEMBER 2025 DATA GENERATED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Departments: {len(departments)}")
        print(f"   Employees: {len(employees)}")
        print(f"   Manager: {manager_user.full_name}")
        print(f"   Total Schedules: {total_schedules}")
        print(f"   Total Attendance: {total_attendance} records")
        print(f"   Total OT Hours (Attendance): {total_ot_hours:.1f}h")
        print(f"   Leave Requests: {len(leave_requests)}")
        print(f"   Comp-Off Usage: {len(comp_off_usage_requests)}")
        print(f"   Overtime Requests: {len(ot_requests)} ({total_ot_req:.1f}h)")
        print(f"\n✨ All employees have complete data for November 2025!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_november_2025_data())
