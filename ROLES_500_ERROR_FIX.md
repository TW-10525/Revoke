# Roles Endpoint 500 Error Fix

## Issue
**Error**: `Failed to load resource: the server responded with a status of 500 (Internal Server Error)`
- **Endpoint**: `GET /api/roles?department_id=8`
- **Location**: `Manager.jsx:726`

## Root Cause
When the `GET /roles` endpoint was called, it would fail with a 500 error if:
1. The current user was a manager
2. The manager had no department assigned (i.e., `Manager` record doesn't exist or is incomplete)

The issue was in the `list_roles()` function where `get_manager_department()` would return `None`, but the code would still try to filter with:
```python
Role.department_id == None  # ❌ Invalid SQL filter
```

This would cause a database error resulting in a 500 response.

## Fix Applied

### Files Modified
- `backend/app/main.py`

### Changes Made

#### 1. **GET /roles endpoint (Line ~2498)**
```python
# BEFORE:
else:
    manager_dept = await get_manager_department(current_user, db)
    stmt = stmt.filter(
        Role.department_id == manager_dept,
        Role.is_active == True
    )

# AFTER:
else:
    manager_dept = await get_manager_department(current_user, db)
    if manager_dept is None:
        # Manager has no department assigned, return empty list
        return []
    stmt = stmt.filter(
        Role.department_id == manager_dept,
        Role.is_active == True
    )
```

#### 2. **GET /roles/{role_id} endpoint (Line ~2524)**
```python
# BEFORE:
if current_user.user_type != UserType.ADMIN:
    manager_dept = await get_manager_department(current_user, db)
    stmt = stmt.filter(Role.department_id == manager_dept)

# AFTER:
if current_user.user_type != UserType.ADMIN:
    manager_dept = await get_manager_department(current_user, db)
    if manager_dept is None:
        raise HTTPException(status_code=404, detail="Role not found")
    stmt = stmt.filter(Role.department_id == manager_dept)
```

## Why These Fixes Work

1. **GET /roles**: Returns an empty list when the manager has no department assignment. This is correct behavior since a manager with no department can't have any roles assigned to them.

2. **GET /roles/{role_id}**: Returns a 404 error when the manager has no department. This prevents attempting to access a role when the manager has no valid context.

## Testing
After the fix:
- ✅ `/api/roles` endpoint returns 200 with empty array or full list depending on department
- ✅ `/api/roles?department_id=X` works correctly for admin/sub_admin users
- ✅ No more 500 errors when accessing roles as a manager with incomplete department assignment

## Status
**Fixed** - Backend code updated and restarted.
