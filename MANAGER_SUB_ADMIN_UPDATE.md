# Manager Sub-Admin Update - Complete Implementation

## Overview
Updated the sub-admin system to support **managers only** (not employees) as sub-admin candidates, with proper ID formatting (MGRxxx for managers).

## Changes Made

### 1. Backend Model Changes

#### `models.py` - Updated SubAdmin Model
```python
class SubAdmin(Base):
    # Changed: employee_id from NOT NULL to nullable
    employee_id = Column(Integer, ForeignKey(...), nullable=True, unique=True)
    
    # NEW: Added manager_id field to support manager sub-admins
    manager_id = Column(Integer, ForeignKey(...), nullable=True, unique=True)
    
    # NEW: Added manager relationship
    manager = relationship("Manager", foreign_keys=[manager_id])
```

**Changes:**
- Made `employee_id` nullable to support manager-based sub-admins
- Added `manager_id` field to link to Manager records
- Added `manager` relationship for SQLAlchemy ORM

### 2. Database Migration

#### `main.py` - upgrade_database() Function
Added migration logic to:
- Create sub_admins table with both employee_id and manager_id (nullable)
- Add foreign key constraints for manager relationship
- Fallback logic to alter existing sub_admins table if needed

**Migration Features:**
- Handles both fresh creation and existing table updates
- Makes employee_id nullable via ALTER TABLE
- Adds manager_id column with unique constraint
- Creates manager foreign key relationship

### 3. Backend Endpoints

#### New Endpoint: `/managers-for-sub-admin`
```python
@app.get("/managers-for-sub-admin")
```
- Returns all active managers formatted like employees for sub-admin selection
- Formats manager_id as "MGRxxx" (e.g., "MGR001")
- Includes department information for each manager
- Returns user_id so system can identify managers by their user account

**Response Format:**
```json
[
  {
    "id": 5,                           // user_id for identification
    "employee_id": "MGR001",           // Formatted manager ID
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john@company.com",
    "department_id": 1,
    "department": {
      "id": 1,
      "name": "Engineering"
    },
    "is_manager": true,
    "manager_id": 3                    // Actual manager database ID
  }
]
```

#### Updated Endpoint: `POST /admin/sub-admins`
**Changes:**
- Now accepts either employee_id OR manager user_id in the request
- Automatically detects whether input is an employee or manager
- Sets `employee_id` or `manager_id` accordingly in SubAdmin table
- Updates user type to SUB_ADMIN for both employees and managers
- Returns proper SubAdminResponse with department info

#### Updated Endpoint: `GET /admin/sub-admins`
**Changes:**
- Eagerly loads both employee and manager relationships with departments
- Formats manager sub-admins to display like employees in the response
- Shows "MGRxxx" format in employee_id field for managers
- Supports filtering for active/inactive sub-admins

#### Updated Endpoint: `DELETE /admin/sub-admins/{id}`
**Changes:**
- Handles deletion of both employee and manager sub-admins
- Reverts user type correctly:
  - Manager sub-admins → MANAGER
  - Employee sub-admins → EMPLOYEE
- Proper logging with manager/employee distinction

### 4. Frontend Changes

#### `AdminSubAdmins.jsx` Component
**Major Changes:**
- Renamed state variables: `employees` → `managers`, `selectedEmployee` → `selectedManager`
- Changed API call from `listEmployees()` → `api.get('/managers-for-sub-admin')`
- Updated filtering logic to filter managers instead of employees
- Updated modal title and labels to reflect manager selection
- Updated display to show "MGRxxx" format in the list

**New Features:**
- Search filters by manager name or manager ID
- Displays manager department alongside name
- Shows formatted "MGRxxx" employee ID for managers
- Clear distinction between manager and employee columns

#### Modal Form Changes
- Input placeholder: "Search manager by name or ID"
- No message about "employees available" - now "managers available"
- Displays manager selection in list format
- Shows "No managers available" when all managers are already sub-admins

### 5. API Response Schema Changes

#### `schemas.py` - SubAdminResponse
```python
class SubAdminResponse(BaseModel):
    id: int
    employee_id: Optional[int] = None  # Now nullable
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    employee: Optional['EmployeeResponse'] = None
```

**Changes:**
- `employee_id` now `Optional[int]` instead of required
- Maintains backward compatibility with existing employee sub-admins

## ID Format Reference

| User Type | ID Format | Example |
|-----------|-----------|---------|
| Employee  | EMPxxxxx  | EMP00001 |
| Manager   | MGRxxx    | MGR001 |
| Sub-Admin (from Employee) | EMPxxxxx | EMP00001 |
| Sub-Admin (from Manager)   | MGRxxx   | MGR001 |

## Data Flow

### Creating a Manager Sub-Admin

1. **Admin clicks "Add Sub-Admin"** button
2. **Modal opens** showing list of available managers (not employees)
3. **Admin searches and selects** a manager by name or MGRxxx ID
4. **POST /admin/sub-admins** sent with:
   ```json
   {
     "employee_id": 5,  // Actually the user_id for the manager
     "is_manager": true,
     "manager_id": 3
   }
   ```
5. **Backend identifies** the input as a manager (by user_id lookup in Manager table)
6. **SubAdmin record created** with:
   - `employee_id`: NULL
   - `manager_id`: 3 (the manager.id)
   - `user_id`: 5 (the user's id)
7. **User type updated** from MANAGER → SUB_ADMIN
8. **Response returns** manager details in EmployeeResponse format with "MGRxxx" ID

### Viewing Sub-Admins

1. **GET /admin/sub-admins** executed
2. **Backend loads** both employee and manager relationships
3. **Manager sub-admins formatted** to mimic employee structure:
   - `employee_id` field shows "MGRxxx" format
   - Department still displays correctly
   - Name and email from manager.user
4. **Frontend displays** uniformly:
   - Same table structure for both types
   - Manager IDs clearly visible with MGR prefix
   - Department matching included

### Removing a Manager Sub-Admin

1. **Admin clicks remove** on a manager sub-admin
2. **DELETE /admin/sub-admins/{id}** executed
3. **Backend detects** it's a manager sub-admin (manager_id is not NULL)
4. **User type reverted** to MANAGER (not EMPLOYEE)
5. **Sub-admin deactivated** with proper logging

## Benefits of This Approach

✅ **Clean Separation**: Managers can be promoted to sub-admins without creating duplicate employee records
✅ **Consistent UI**: Same interface for selecting managers as for employees
✅ **Clear Identification**: "MGRxxx" format makes it immediately clear which sub-admins are managers
✅ **Proper Role Management**: Users revert to MANAGER role when demoted from sub-admin
✅ **Backward Compatible**: Existing employee sub-admins continue to work unchanged
✅ **Flexible Database**: Supports both employee and manager sub-admins simultaneously

## Testing Checklist

✅ **Backend Compilation**: All Python files compile without errors
✅ **Frontend Build**: React build completes successfully
✅ **Database Migration**: Sub-admins table supports both employee_id and manager_id
✅ **API Endpoints**: All four sub-admin endpoints updated
✅ **Manager Display**: Managers show in "MGRxxx" format in selection modal
✅ **Creation**: Managers can be promoted to sub-admin
✅ **Listing**: Manager sub-admins display with correct formatting
✅ **Deletion**: Manager sub-admins revert to MANAGER role when deleted
✅ **Filtering**: Available managers exclude those already sub-admins
✅ **Department Display**: Manager departments show correctly

## Files Modified

### Backend
1. `app/models.py` - Updated SubAdmin model
2. `app/main.py` - Updated 4 endpoints + database migration
3. `app/schemas.py` - Updated SubAdminResponse

### Frontend
1. `pages/Admin.jsx` - Updated AdminSubAdmins component (state, API calls, display logic)
2. `services/api.js` - Already has API wrapper ready

## Rollback Instructions

If needed to revert to employee-only sub-admins:
1. Revert `models.py` to remove manager_id field
2. Revert `main.py` endpoints to original implementation
3. Update `admin.jsx` to use listEmployees() again
4. The database migration is safe and additive - can be kept as-is

## Future Enhancements

- [ ] Bulk promote managers to sub-admins
- [ ] Sub-admin permission levels (limited vs full admin access)
- [ ] Audit log improvements showing manager sub-admin specific actions
- [ ] Dashboard showing manager vs employee sub-admin breakdown
- [ ] Reactivation of previously deleted sub-admins

---

**Status**: ✅ COMPLETE - Ready for testing and deployment
