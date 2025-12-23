#!/bin/bash
# Test Comp-Off Functionality
# This script tests the comp-off feature end-to-end

echo "🧪 Testing Comp-Off Feature"
echo "=============================="

# Test 1: Get comp-off tracking (should exist for employee)
echo -e "\n📊 Test 1: Getting comp-off tracking..."
curl -s -X GET http://localhost:8000/comp-off-tracking \
  -H "Authorization: Bearer YOUR_EMPLOYEE_TOKEN" | jq '.'

# Test 2: Create comp-off request for free day (should succeed)
echo -e "\n✅ Test 2: Creating comp-off request for free day..."
curl -s -X POST http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer YOUR_EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "comp_off_date": "2025-12-25",
    "reason": "Worked on non-scheduled day"
  }' | jq '.'

# Test 3: Try to create comp-off for day with assigned shift (should fail)
echo -e "\n❌ Test 3: Attempting comp-off on shift day (should fail)..."
curl -s -X POST http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer YOUR_EMPLOYEE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "comp_off_date": "2025-12-24",
    "reason": "Already has shift"
  }' | jq '.'

# Test 4: List all comp-off requests
echo -e "\n📋 Test 4: Getting all comp-off requests..."
curl -s -X GET http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer YOUR_MANAGER_TOKEN" | jq '.'

# Test 5: Approve comp-off request
echo -e "\n✅ Test 5: Manager approving comp-off..."
curl -s -X POST http://localhost:8000/manager/approve-comp-off/1 \
  -H "Authorization: Bearer YOUR_MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"review_notes": "Approved"}' | jq '.'

# Test 6: Check updated comp-off tracking after approval
echo -e "\n📊 Test 6: Getting updated comp-off tracking..."
curl -s -X GET http://localhost:8000/comp-off-tracking \
  -H "Authorization: Bearer YOUR_EMPLOYEE_TOKEN" | jq '.'

# Test 7: Download comp-off report
echo -e "\n📥 Test 7: Downloading comp-off report..."
curl -s -X GET http://localhost:8000/comp-off/export/employee \
  -H "Authorization: Bearer YOUR_EMPLOYEE_TOKEN" \
  -o comp_off_report.xlsx && echo "✅ Report downloaded"

echo -e "\n✅ All tests completed!"
