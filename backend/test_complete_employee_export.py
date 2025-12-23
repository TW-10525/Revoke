#!/usr/bin/env python3
"""
Complete Employee Mock Data and Excel Report Testing
- Creates 1 test employee with comprehensive data
- Tests: Attendance, Leave Requests, Comp-Off, OT
- Exports: Monthly Attendance, Employee Monthly Attendance, Leave/Comp-Off Report
"""

import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.models import (
    User, UserType, Department, Manager, Employee, Role, Shift,
    Schedule, Attendance, OvertimeRequest, OvertimeStatus, LeaveRequest,
    LeaveStatus, CompOffRequest, CompOffTracking
)
from app.auth import get_password_hash


async def create_test_data():
    """Create comprehensive test data for one employee"""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("=" * 80)
        print("🌱 CREATING COMPREHENSIVE TEST DATA FOR ONE EMPLOYEE")
        print("=" * 80)
        
        # Clear existing data (if needed, comment out for preservation)
        # await session.execute("TRUNCATE TABLE comp_off_details CASCADE")
        
        # 1. Create Department
        print("\n📍 Creating department...")
        dept = Department(
            dept_id="TST",
            name="Test Department",
            description="Test Department for Excel Export"
        )
        session.add(dept)
        await session.flush()
        print(f"✅ Department created: {dept.name}")
        
        # 2. Create Role
        print("\n🎯 Creating role...")
        role = Role(
            name="Test Developer",
            description="Test Developer Role",
            department_id=dept.id,
            priority=50,
            break_minutes=60,
            weekend_required=False
        )
        session.add(role)
        await session.flush()
        print(f"✅ Role created: {role.name}")
        
        # 3. Create Shifts
        print("\n⏰ Creating shifts...")
        shift_config = [
            ("Morning Shift", "09:00", "18:00"),
            ("Afternoon Shift", "13:00", "22:00"),
            ("Evening Shift", "17:00", "02:00"),
        ]
        shifts = {}
        for shift_name, start_time, end_time in shift_config:
            shift = Shift(
                name=shift_name,
                start_time=start_time,
                end_time=end_time,
                role_id=role.id
            )
            session.add(shift)
            shifts[shift_name] = shift
        await session.flush()
        print(f"✅ Created {len(shifts)} shifts: {list(shifts.keys())}")
        
        # 4. Create Manager User
        print("\n👨‍💼 Creating manager...")
        manager_user = User(
            username="test_manager",
            email="manager@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Manager",
            user_type=UserType.MANAGER,
            is_active=True
        )
        session.add(manager_user)
        await session.flush()
        
        manager = Manager(
            user_id=manager_user.id,
            department_id=dept.id
        )
        session.add(manager)
        await session.flush()
        print(f"✅ Manager created: {manager_user.full_name}")
        
        # 5. Create Employee User
        print("\n👤 Creating employee...")
        emp_user = User(
            username="test_employee",
            email="employee@test.com",
            hashed_password=get_password_hash("password123"),
            full_name="John TestEmployee",
            user_type=UserType.EMPLOYEE,
            is_active=True
        )
        session.add(emp_user)
        await session.flush()
        
        employee = Employee(
            user_id=emp_user.id,
            department_id=dept.id,
            role_id=role.id,
            employee_id="TEST001",
            first_name="John",
            last_name="TestEmployee",
            email="employee@test.com",
            phone="1234567890",
            hire_date=date(2024, 1, 1),
            paid_leave_per_year=12,
            is_active=True
        )
        session.add(employee)
        await session.flush()
        print(f"✅ Employee created: {emp_user.full_name} ({employee.employee_id})")
        
        # 6. Initialize Comp-Off Tracking
        print("\n💰 Initializing comp-off tracking...")
        comp_tracking = CompOffTracking(
            employee_id=employee.id,
            earned_days=5,
            used_days=2,
            available_days=3
        )
        session.add(comp_tracking)
        await session.flush()
        print(f"✅ Comp-Off Tracking: Earned={comp_tracking.earned_days}, Used={comp_tracking.used_days}, Available={comp_tracking.available_days}")
        
        # 7. Create Schedules for December 2024 (past month for testing)
        print("\n📅 Creating schedules for December 2024...")
        december_start = date(2024, 12, 1)
        december_end = date(2024, 12, 31)
        current_date = december_start
        shift_list = list(shifts.values())
        shift_index = 0
        
        schedules_created = 0
        while current_date <= december_end:
            # Skip weekends for now (assign work shifts to weekdays)
            if current_date.weekday() < 5:  # Monday-Friday
                shift = shift_list[shift_index % len(shift_list)]
                sched = Schedule(
                    employee_id=employee.id,
                    department_id=dept.id,
                    role_id=role.id,
                    shift_id=shift.id,
                    date=current_date,
                    start_time=shift.start_time,
                    end_time=shift.end_time,
                    status="scheduled"
                )
                session.add(sched)
                shift_index += 1
                schedules_created += 1
            current_date += timedelta(days=1)
        
        await session.flush()
        print(f"✅ Created {schedules_created} work schedules for December 2024")
        
        # 8. Create Attendance Records with Check-In/Check-Out and OT
        print("\n✅ Creating attendance records with check-in/check-out...")
        
        # Sample attendance data for selected dates
        attendance_data = [
            # Date, CheckIn, CheckOut, Status, OT Hours
            (date(2024, 12, 2), "08:45", "18:30", "present", 0.5),      # 5 mins early, 30 mins late = 0.5 OT
            (date(2024, 12, 3), "09:00", "19:00", "present", 1.0),      # 1 hour OT
            (date(2024, 12, 4), "09:15", "18:15", "present", 0.0),      # On time, normal hours
            (date(2024, 12, 5), "08:30", "20:00", "present", 2.0),      # 2 hours OT
            (date(2024, 12, 6), "09:00", "18:00", "present", 0.0),      # Normal
            (date(2024, 12, 9), "08:50", "18:45", "present", 0.75),     # 0.75 hours OT
            (date(2024, 12, 10), "09:05", "17:55", "present", 0.0),     # Slightly under, no OT
            (date(2024, 12, 11), "09:00", "19:30", "present", 1.5),     # 1.5 hours OT
            (date(2024, 12, 12), "08:40", "18:40", "present", 1.0),     # 1 hour OT
            (date(2024, 12, 13), "09:00", "18:00", "present", 0.0),     # Normal
            (date(2024, 12, 16), "09:10", "20:00", "present", 1.75),    # 1.75 hours OT
            (date(2024, 12, 17), "09:00", "18:00", "present", 0.0),     # Normal
            (date(2024, 12, 18), "08:30", "18:45", "present", 1.25),    # 1.25 hours OT
            (date(2024, 12, 19), "09:00", "19:00", "present", 1.0),     # 1 hour OT
            (date(2024, 12, 20), "09:00", "18:00", "present", 0.0),     # Normal
            (date(2024, 12, 23), "08:55", "18:30", "present", 0.5),     # 0.5 hours OT
            (date(2024, 12, 24), "09:00", "17:00", "present", 0.0),     # Leave day (comp-off)
            (date(2024, 12, 26), "09:00", "20:00", "present", 1.0),     # 1 hour OT
            (date(2024, 12, 27), "09:00", "18:00", "present", 0.0),     # Normal
        ]
        
        for att_date, check_in, check_out, status, ot_hours in attendance_data:
            attendance = Attendance(
                employee_id=employee.id,
                date=att_date,
                in_time=check_in,
                out_time=check_out,
                status=status,
                overtime_hours=ot_hours,
                worked_hours=9.0 if ot_hours > 0 else 8.0,
                notes=f"Check-in: {check_in}, Check-out: {check_out}, OT: {ot_hours}h"
            )
            session.add(attendance)
        
        await session.flush()
        print(f"✅ Created {len(attendance_data)} attendance records with OT")
        
        # 9. Create Leave Requests
        print("\n🏖️ Creating leave requests...")
        
        leave_requests_data = [
            # StartDate, EndDate, Type, Status, Reason, Duration
            (date(2024, 12, 10), date(2024, 12, 10), "paid", "approved", "Doctor appointment"),
            (date(2024, 12, 24), date(2024, 12, 24), "comp_off", "approved", "Using comp-off earned"),
            (date(2024, 12, 25), date(2024, 12, 25), "unpaid", "approved", "Personal reason"),
        ]
        
        for start, end, leave_type, status, reason in leave_requests_data:
            leave_req = LeaveRequest(
                employee_id=employee.id,
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
        print(f"✅ Created {len(leave_requests_data)} leave requests")
        print(f"   - 1 Paid Leave (Dec 10)")
        print(f"   - 1 Comp-Off Usage (Dec 24)")
        print(f"   - 1 Unpaid Leave (Dec 25)")
        
        # 10. Skip Comp-Off Earned Requests (will test with leave requests instead)
        print("\n🎁 Comp-off earned skipped (included via leave requests)")
        
        # 11. Create Overtime Requests
        print("\n⏱️ Creating overtime requests...")
        ot_requests = [
            (date(2024, 12, 3), "09:00", "19:00", 1.0, "project deadline", "approved"),
            (date(2024, 12, 5), "09:00", "20:00", 2.0, "client meeting prep", "approved"),
            (date(2024, 12, 11), "09:00", "19:30", 1.5, "urgent bug fix", "approved"),
        ]
        
        for ot_date, start_time, end_time, hours, reason, status in ot_requests:
            ot_req = OvertimeRequest(
                employee_id=employee.id,
                request_date=ot_date,
                from_time=start_time,
                to_time=end_time,
                request_hours=hours,
                reason=reason,
                status=OvertimeStatus[status.upper()],
                manager_id=manager_user.id,
                created_at=datetime.now()
            )
            session.add(ot_req)
        
        await session.flush()
        print(f"✅ Created {len(ot_requests)} overtime requests (total: {sum(h[3] for h in ot_requests):.1f} hours)")
        
        # Final commit
        await session.commit()
        print("\n" + "=" * 80)
        print("✅ ALL TEST DATA CREATED SUCCESSFULLY")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Employee: {emp_user.full_name} ({employee.employee_id})")
        print(f"   Department: {dept.name}")
        print(f"   Role: {role.name}")
        print(f"   Shifts: {len(shifts)}")
        print(f"   Work Schedules: {schedules_created}")
        print(f"   Attendance Records: {len(attendance_data)} (Total OT: {sum(h[4] for h in attendance_data):.1f} hours)")
        print(f"   Leave Requests: {len(leave_requests_data)} (1 Paid + 1 Comp-Off + 1 Unpaid)")
        print(f"   Overtime Requests: {len(ot_requests)} (Total: {sum(h[3] for h in ot_requests):.1f} hours)")
        print(f"   Comp-Off Tracking: Earned={comp_tracking.earned_days}, Used={comp_tracking.used_days}, Available={comp_tracking.available_days}")
        print("\n🔗 Test Export URLs (use bearer token for test_manager):")
        print(f"   Monthly Attendance (All): /attendance/export/monthly?year=2024&month=12")
        print(f"   Employee Monthly: /attendance/export/employee-monthly?year=2024&month=12")
        print(f"   Leave/Comp-Off Report: /manager/export-leave-compoff/{employee.id}")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_test_data())
