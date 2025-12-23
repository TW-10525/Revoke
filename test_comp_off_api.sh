#!/bin/bash

echo "🧪 Testing Comp-Off API Endpoints"
echo "=================================="

# 1. Login as employee
echo -e "\n1️⃣ Logging in as employee (emp1)..."
EMP_LOGIN=$(curl -s -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=emp1&password=emp123")

EMP_TOKEN=$(echo $EMP_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Employee token: ${EMP_TOKEN:0:20}..."

# 2. Get comp-off tracking
echo -e "\n2️⃣ Getting comp-off tracking for employee..."
curl -s -X GET http://localhost:8000/comp-off-tracking \
  -H "Authorization: Bearer $EMP_TOKEN" | jq '.'

# 3. List comp-off requests (should be empty)
echo -e "\n3️⃣ Listing comp-off requests (should be empty)..."
curl -s -X GET http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer $EMP_TOKEN" | jq '.'

# 4. Get comp-off statistics
echo -e "\n4️⃣ Getting comp-off statistics..."
curl -s -X GET http://localhost:8000/comp-off-statistics \
  -H "Authorization: Bearer $EMP_TOKEN" | jq '.'

# 5. Get employee info to find ID
echo -e "\n5️⃣ Getting employee info..."
EMP_INFO=$(curl -s -X GET http://localhost:8000/employees \
  -H "Authorization: Bearer $EMP_TOKEN" | jq '.[0]')
EMP_ID=$(echo $EMP_INFO | jq '.id')
echo "Employee ID: $EMP_ID"

# 6. Try to create comp-off request for a free day
echo -e "\n6️⃣ Creating comp-off request for free day..."
COMP_OFF_RESPONSE=$(curl -s -X POST http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer $EMP_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"employee_id\": $EMP_ID,
    \"comp_off_date\": \"2025-12-27\",
    \"reason\": \"Worked on non-scheduled day\"
  }")
echo $COMP_OFF_RESPONSE | jq '.'

COMP_OFF_ID=$(echo $COMP_OFF_RESPONSE | jq '.id')
echo "Comp-off request ID: $COMP_OFF_ID"

# 7. Login as manager
echo -e "\n7️⃣ Logging in as manager..."
MGR_LOGIN=$(curl -s -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=manager1&password=manager123")

MGR_TOKEN=$(echo $MGR_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "✅ Manager token: ${MGR_TOKEN:0:20}..."

# 8. Manager views all comp-off requests
echo -e "\n8️⃣ Manager viewing all comp-off requests..."
curl -s -X GET http://localhost:8000/comp-off-requests \
  -H "Authorization: Bearer $MGR_TOKEN" | jq '.'

# 9. Manager approves comp-off
if [ "$COMP_OFF_ID" != "null" ] && [ -n "$COMP_OFF_ID" ]; then
  echo -e "\n9️⃣ Manager approving comp-off request..."
  curl -s -X POST http://localhost:8000/manager/approve-comp-off/$COMP_OFF_ID \
    -H "Authorization: Bearer $MGR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"review_notes": "Approved"}' | jq '.'
  
  # 10. Check updated comp-off tracking
  echo -e "\n🔟 Checking updated comp-off tracking..."
  curl -s -X GET http://localhost:8000/comp-off-tracking \
    -H "Authorization: Bearer $EMP_TOKEN" | jq '.'
fi

echo -e "\n✅ All tests completed!"
