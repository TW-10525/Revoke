#!/usr/bin/env python3
"""
Test script to verify DeptAccess API endpoints are working
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test 1: Check if /comp-off-requests endpoint responds
print("=" * 60)
print("Test 1: Testing /comp-off-requests endpoint")
print("=" * 60)

# You'll need to authenticate first and get a token
# This is just to test the endpoint structure

print("\nNote: You need to be authenticated to test these endpoints.")
print("Steps to test manually:")
print("1. Login as admin/manager/employee")
print("2. In browser console, run:")
print("   fetch('/comp-off-requests').then(r => r.json()).then(d => console.log(d))")
print("3. Check if the response is valid JSON (not a 500 error)")

print("\n" + "=" * 60)
print("Test 2: Testing DeptAccess route")
print("=" * 60)

print("\nSteps to test manually:")
print("1. Login as admin or sub_admin")
print("2. Go to Admin > Departments")
print("3. Click on a department")
print("4. Look for the green 'Access Dept' button (with 🔑 icon)")
print("5. Click it - should navigate to /admin/access-dept/dashboard")
print("6. Verify sidebar loads with all 9 menu items")
print("7. Click each sidebar item to verify pages load correctly")

print("\n" + "=" * 60)
print("Menu items to verify:")
print("=" * 60)
menu_items = [
    "Dashboard",
    "Employees", 
    "Schedules",
    "Roles",
    "Overtime Approvals",
    "Leaves",
    "Comp-off",
    "Attendance",
    "Messages"
]

for i, item in enumerate(menu_items, 1):
    print(f"{i}. {item}")

print("\n" + "=" * 60)
print("Expected behavior:")
print("=" * 60)
print("✓ Access Dept button visible in department details")
print("✓ Clicking button navigates to /admin/access-dept/dashboard")
print("✓ Department name shown in sidebar header")
print("✓ All 9 menu items clickable")
print("✓ Data filtered to selected department")
print("✓ 'Back to Departments' button returns to department list")
print("✓ All pages load without 404 or 500 errors")

print("\n" + "=" * 60)
print("Troubleshooting:")
print("=" * 60)
print("If you see:")
print("  404 Not Found - Check that the route is registered in App.jsx")
print("  500 Error - Check browser console and backend logs for details")
print("  Empty page - Check that sessionStorage has department_id set")
print("  Missing menu items - Check that DeptAccess.jsx has all imports")

print("\n" + "=" * 60)
print("Test complete - Use browser DevTools to verify functionality")
print("=" * 60)
