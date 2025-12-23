"""
Comprehensive Mock Data Seeding Script
Creates: 3 Managers, 30 Employees (10 per manager), Leaves, Comp-Off, Overtime, Schedules
Run: python seed_comprehensive_mock_data.py
"""

import asyncio
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import engine, DATABASE_URL
from app.models import (
    User, UserType, Department, Manager, Employee, Role, Shift, 
    Schedule, Attendance, OvertimeRequest, OvertimeStatus, LeaveRequest,
    LeaveStatus, CompOffRequest, CompOffTracking, CompOffDetail
)
from app.auth import get_password_hash


async def seed_comprehensive_data():
    print("🌱 Starting comprehensive mock data seeding...")
    print("=" * 60)
    
    # Create async session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # ===== 0. CLEAR EXISTING DATA =====
            print("\n🧹 Clearing existing data...")
            # Delete in order of foreign key dependencies
            tables_to_clear = [
                'comp_off_details', 'comp_off_tracking', 'comp_off_requests',
                'overtime_worked', 'overtime_requests', 'attendance', 'check_ins',
                'schedules', 'messages', 'notifications', 'shifts', 'roles',
                'employees', 'managers', 'departments', 'users'
            ]
            for table in tables_to_clear:
                try:
                    await session.execute(f"TRUNCATE TABLE {table} CASCADE")
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    # Table might not exist, continue
                    pass
            
            print("✅ Database cleared")
            
            # ===== 1. CREATE DEPARTMENTS =====
            print("\n📍 Creating departments...")
            departments = []
            dept_names = ["IT Department", "HR Department", "Finance Department"]
            for i, name in enumerate(dept_names, 1):
                dept = Department(
                    dept_id=f"{i:03d}",
                    name=name,
                    description=f"{name} Description"
                )
                session.add(dept)
                departments.append(dept)
            await session.flush()
            print(f"✅ Created {len(departments)} departments")

            # ===== 2. CREATE ROLES =====
            print("\n🎯 Creating roles...")
            roles = {}
            for dept in departments:
                for role_name in ["Developer", "Manager", "Analyst"]:
                    role = Role(
                        name=role_name,
                        description=f"{role_name} Role",
                        department_id=dept.id,
                        priority=50,
                        break_minutes=60,
                        weekend_required=False
                    )
                    session.add(role)
                    if dept.dept_id not in roles:
                        roles[dept.dept_id] = {}
                    roles[dept.dept_id][role_name] = role
            await session.flush()
            print(f"✅ Created roles for all departments")

            # ===== 3. CREATE SHIFTS =====
            print("\n⏰ Creating shifts...")
            shifts = {}
            for dept in departments:
                dept_shifts = []
                shift_configs = [
                    ("Morning Shift", "09:00", "18:00"),
                    ("Afternoon Shift", "13:00", "22:00"),
                    ("Evening Shift", "17:00", "02:00"),
                ]
                for role_name in ["Developer", "Manager", "Analyst"]:
                    role = roles[dept.dept_id][role_name]
                    for shift_name, start_time, end_time in shift_configs:
                        shift = Shift(
                            role_id=role.id,
                            name=shift_name,
                            start_time=start_time,
                            end_time=end_time,
                            priority=50,
                            min_emp=1,
                            max_emp=5
                        )
                        session.add(shift)
                        dept_shifts.append(shift)
                shifts[dept.dept_id] = dept_shifts
            await session.flush()
            print(f"✅ Created shifts for all roles")

            # ===== 4. CREATE MANAGERS & EMPLOYEES =====
            print("\n👔 Creating 3 managers with 10 employees each...")
            all_employees = []
            manager_data = []
            
            for dept_idx, dept in enumerate(departments):
                # Create manager for this department
                manager_user = User(
                    username=f"manager{dept_idx + 1}",
                    email=f"manager{dept_idx + 1}@company.com",
                    hashed_password=get_password_hash("manager123"),
                    full_name=f"Manager {dept_idx + 1} ({dept.name})",
                    user_type=UserType.MANAGER,
                    is_active=True
                )
                session.add(manager_user)
                await session.flush()
                
                manager_record = Manager(
                    user_id=manager_user.id,
                    department_id=dept.id,
                    is_active=True
                )
                session.add(manager_record)
                await session.flush()
                
                manager_data.append({
                    'user': manager_user,
                    'record': manager_record,
                    'department': dept
                })
                print(f"  ✅ Manager: {manager_user.full_name} (username: manager{dept_idx + 1}, password: manager123)")
                
                # Create 10 employees for this manager
                for emp_idx in range(10):
                    emp_id = f"{dept_idx:02d}{emp_idx:02d}"
                    employee_user = User(
                        username=f"emp{emp_id}",
                        email=f"emp{emp_id}@company.com",
                        hashed_password=get_password_hash("emp123"),
                        full_name=f"Employee {emp_idx + 1} (Dept {dept_idx + 1})",
                        user_type=UserType.EMPLOYEE,
                        is_active=True
                    )
                    session.add(employee_user)
                    await session.flush()
                    
                    # Distribute employees across roles: ~3-4 per role
                    role_names = ["Developer", "Manager", "Analyst"]
                    assigned_role = role_names[emp_idx % 3]
                    assigned_role_id = roles[dept.dept_id][assigned_role].id
                    
                    employee = Employee(
                        employee_id=emp_id,
                        first_name=f"Employee",
                        last_name=f"{emp_idx + 1}",
                        email=f"emp{emp_id}@company.com",
                        phone=f"555-{emp_id}",
                        department_id=dept.id,
                        role_id=assigned_role_id,
                        user_id=employee_user.id,
                        weekly_hours=40,
                        daily_max_hours=8,
                        shifts_per_week=5,
                        paid_leave_per_year=10,
                        hire_date=date.today() - timedelta(days=365)
                    )
                    session.add(employee)
                    all_employees.append({
                        'employee': employee,
                        'user': employee_user,
                        'manager': manager_record,
                        'department': dept
                    })
                
                print(f"  ✅ Created 10 employees for {manager_user.full_name}")
            
            await session.flush()
            print(f"✅ Total created: {len(manager_data)} managers and {len(all_employees)} employees")

            # ===== 5. CREATE SCHEDULES (Next 4 weeks) =====
            print("\n📅 Creating schedules for next 4 weeks...")
            start_date = date.today()
            for dept_idx, dept in enumerate(departments):
                for emp_data in all_employees:
                    if emp_data['department'].id != dept.id:
                        continue
                    
                    employee = emp_data['employee']
                    dept_shifts = shifts[dept.dept_id]
                    
                    # Create 5 shifts per week for 4 weeks
                    shift_idx = 0
                    for day in range(28):  # 4 weeks
                        current_date = start_date + timedelta(days=day)
                        
                        # Assign 5 shifts per week (Mon-Fri typically)
                        if current_date.weekday() < 5:  # Mon-Fri
                            shift = dept_shifts[shift_idx % len(dept_shifts)]
                            schedule = Schedule(
                                department_id=dept.id,
                                employee_id=employee.id,
                                role_id=employee.role_id,
                                shift_id=shift.id,
                                date=current_date,
                                start_time=shift.start_time,
                                end_time=shift.end_time,
                                status='scheduled',
                                is_overtime=False
                            )
                            session.add(schedule)
                            shift_idx += 1
                
            await session.flush()
            print(f"✅ Created schedules for all employees")

            # ===== 6. CREATE VARIOUS LEAVE REQUESTS =====
            print("\n🏖️  Creating diverse leave requests...")
            leave_count = 0
            for emp_idx, emp_data in enumerate(all_employees):
                employee = emp_data['employee']
                manager = emp_data['manager']
                
                # Each employee gets different types of leaves
                if emp_idx % 3 == 0:  # Every 3rd employee - Full day paid leave
                    leave = LeaveRequest(
                        employee_id=employee.id,
                        start_date=start_date + timedelta(days=5),
                        end_date=start_date + timedelta(days=5),
                        leave_type='paid',
                        duration_type='full_day',
                        reason=f"Sick leave - Employee {emp_idx}",
                        status=LeaveStatus.APPROVED,
                        manager_id=manager.id,
                        reviewed_at=datetime.utcnow()
                    )
                    session.add(leave)
                    leave_count += 1
                
                if emp_idx % 3 == 1:  # Half day leave (morning)
                    leave = LeaveRequest(
                        employee_id=employee.id,
                        start_date=start_date + timedelta(days=8),
                        end_date=start_date + timedelta(days=8),
                        leave_type='paid',
                        duration_type='half_day_morning',
                        reason=f"Doctor appointment - Employee {emp_idx}",
                        status=LeaveStatus.APPROVED,
                        manager_id=manager.id,
                        reviewed_at=datetime.utcnow()
                    )
                    session.add(leave)
                    leave_count += 1
                
                if emp_idx % 3 == 2:  # Half day leave (afternoon)
                    leave = LeaveRequest(
                        employee_id=employee.id,
                        start_date=start_date + timedelta(days=10),
                        end_date=start_date + timedelta(days=10),
                        leave_type='paid',
                        duration_type='half_day_afternoon',
                        reason=f"Personal work - Employee {emp_idx}",
                        status=LeaveStatus.APPROVED,
                        manager_id=manager.id,
                        reviewed_at=datetime.utcnow()
                    )
                    session.add(leave)
                    leave_count += 1
                
                # Some employees get unpaid leave
                if emp_idx % 5 == 0:
                    leave = LeaveRequest(
                        employee_id=employee.id,
                        start_date=start_date + timedelta(days=15),
                        end_date=start_date + timedelta(days=16),
                        leave_type='unpaid',
                        duration_type='full_day',
                        reason=f"Personal reasons - Employee {emp_idx}",
                        status=LeaveStatus.APPROVED,
                        manager_id=manager.id,
                        reviewed_at=datetime.utcnow()
                    )
                    session.add(leave)
                    leave_count += 1
                
                # Pending leave request
                if emp_idx % 4 == 0:
                    leave = LeaveRequest(
                        employee_id=employee.id,
                        start_date=start_date + timedelta(days=20),
                        end_date=start_date + timedelta(days=20),
                        leave_type='paid',
                        duration_type='full_day',
                        reason=f"Family event - Employee {emp_idx}",
                        status=LeaveStatus.PENDING
                    )
                    session.add(leave)
                    leave_count += 1
            
            await session.flush()
            print(f"✅ Created {leave_count} leave requests")

            # ===== 7. CREATE COMP-OFF REQUESTS =====
            print("\n💰 Creating comp-off requests...")
            compoff_count = 0
            for emp_idx, emp_data in enumerate(all_employees):
                employee = emp_data['employee']
                manager = emp_data['manager']
                
                # Half of employees have comp-off requests
                if emp_idx % 2 == 0:
                    # Create comp-off tracking entry
                    comp_tracking = CompOffTracking(
                        employee_id=employee.id,
                        earned_days=3,
                        used_days=1,
                        available_days=2,
                        earned_date=datetime.utcnow() - timedelta(days=30)
                    )
                    session.add(comp_tracking)
                    await session.flush()
                    
                    # Create comp-off request
                    comp_off = CompOffRequest(
                        employee_id=employee.id,
                        comp_off_date=start_date + timedelta(days=12),
                        reason=f"Worked on weekend - Employee {emp_idx}",
                        status=LeaveStatus.APPROVED,
                        manager_id=manager.id,
                        reviewed_at=datetime.utcnow()
                    )
                    session.add(comp_off)
                    compoff_count += 1
                    
                    # Add comp-off detail
                    detail = CompOffDetail(
                        employee_id=employee.id,
                        tracking_id=comp_tracking.id,
                        type='used',
                        date=datetime.utcnow(),
                        earned_month=date.today().strftime("%Y-%m"),
                        notes=f"Comp-off used - Employee {emp_idx}"
                    )
                    session.add(detail)
            
            await session.flush()
            print(f"✅ Created {compoff_count} comp-off requests with tracking")

            # ===== 8. CREATE OVERTIME REQUESTS =====
            print("\n⏱️  Creating overtime requests...")
            ot_count = 0
            for emp_idx, emp_data in enumerate(all_employees):
                employee = emp_data['employee']
                
                # Some employees have overtime requests
                if emp_idx % 3 == 0:
                    ot_request = OvertimeRequest(
                        employee_id=employee.id,
                        request_date=start_date + timedelta(days=3),
                        from_time="18:00",
                        to_time="20:00",
                        request_hours=2.0,
                        reason=f"Project deadline - Employee {emp_idx}",
                        status=OvertimeStatus.APPROVED,
                        manager_id=emp_data['manager'].user_id,
                        approved_at=datetime.utcnow()
                    )
                    session.add(ot_request)
                    ot_count += 1
                
                if emp_idx % 4 == 0:
                    ot_request = OvertimeRequest(
                        employee_id=employee.id,
                        request_date=start_date + timedelta(days=11),
                        from_time="19:00",
                        to_time="22:00",
                        request_hours=3.0,
                        reason=f"Critical bug fix - Employee {emp_idx}",
                        status=OvertimeStatus.PENDING
                    )
                    session.add(ot_request)
                    ot_count += 1
            
            await session.flush()
            print(f"✅ Created {ot_count} overtime requests")

            # ===== 9. CREATE ATTENDANCE RECORDS =====
            print("\n✅ Creating attendance records...")
            attendance_count = 0
            for emp_idx, emp_data in enumerate(all_employees):
                employee = emp_data['employee']
                
                # Create attendance for days worked
                for day in range(10):
                    current_date = start_date + timedelta(days=day)
                    
                    # Skip weekends
                    if current_date.weekday() >= 5:
                        continue
                    
                    # Find corresponding schedule
                    schedules_query = await session.execute(
                        select(Schedule).filter(
                            Schedule.employee_id == employee.id,
                            Schedule.date == current_date
                        )
                    )
                    schedule = schedules_query.scalars().first()
                    
                    if schedule and schedule.status == 'scheduled':
                        # Simulate attendance
                        in_time = "09:15" if day % 2 == 0 else "09:05"  # Mix of on-time and slightly late
                        out_time = "18:30" if day % 3 == 0 else "18:00"
                        
                        attendance = Attendance(
                            employee_id=employee.id,
                            schedule_id=schedule.id,
                            date=current_date,
                            in_time=in_time,
                            out_time=out_time,
                            status="onTime" if day % 2 == 0 else "slightlyLate",
                            out_status="onTime",
                            worked_hours=9.0 if day % 3 == 0 else 8.75,
                            overtime_hours=1.0 if day % 3 == 0 else 0.75,
                            break_minutes=60,
                            notes=f"Attendance - Day {day + 1}"
                        )
                        session.add(attendance)
                        attendance_count += 1
            
            await session.flush()
            print(f"✅ Created {attendance_count} attendance records")

            # Commit all changes
            await session.commit()
            
            print("\n" + "=" * 60)
            print("🎉 MOCK DATA SEEDING COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\n📊 Summary:")
            print(f"  • Departments: 3")
            print(f"  • Managers: 3 (one per department)")
            print(f"  • Employees: 30 (10 per manager)")
            print(f"  • Roles: 9 (3 per department)")
            print(f"  • Shifts: Multiple (3 per role)")
            print(f"  • Leave Requests: {leave_count}")
            print(f"  • Comp-Off Requests: {compoff_count}")
            print(f"  • Overtime Requests: {ot_count}")
            print(f"  • Attendance Records: {attendance_count}")
            
            print("\n🔐 Login Credentials:")
            print("  Managers:")
            print("    - manager1 / manager123 (IT Department)")
            print("    - manager2 / manager123 (HR Department)")
            print("    - manager3 / manager123 (Finance Department)")
            print("\n  Sample Employees (format: empDDEE / emp123 where DD=dept, EE=emp#):")
            print("    - emp0001 / emp123 (Employee 1, Department 1)")
            print("    - emp0105 / emp123 (Employee 5, Department 1)")
            print("    - emp0201 / emp123 (Employee 1, Department 2)")
            print("    - emp0305 / emp123 (Employee 5, Department 3)")
            print("\n" + "=" * 60)
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
