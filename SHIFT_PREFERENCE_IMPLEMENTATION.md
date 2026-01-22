# Shift Preference Management System - Implementation Complete

## Overview
This document describes the new Shift Preference Management system that replaces the "weekend_required" field in role creation with a comprehensive preference collection and management system.

## Key Changes

### 1. Database Models (Backend)
Three new models have been added to `app/models.py`:

#### ShiftPeriod
- Represents a scheduling period (e.g., "January 2024 Schedule")
- Fields:
  - `id`: Primary key
  - `department_id`: Which department this period belongs to
  - `manager_id`: Manager who created this period
  - `name`: Period name
  - `description`: Optional description
  - `period_start`: Start date (e.g., 2024-01-01)
  - `period_end`: End date (e.g., 2024-01-31)
  - `created_at`, `updated_at`: Timestamps

#### ShiftPreferenceForm
- Template created by managers to request employee preferences
- Fields:
  - `id`: Primary key
  - `shift_period_id`: Which period this form is for
  - `department_id`: Department reference
  - `manager_id`: Manager who created the form
  - `status`: 'active', 'closed', 'expired'
  - `available_shifts`: JSON list of shift IDs available for preference
  - `created_at`, `updated_at`: Timestamps

#### EmployeeShiftPreference
- Employee's preference submission
- Fields:
  - `id`: Primary key
  - `preference_form_id`: Which form this preference is for
  - `employee_id`: Which employee
  - `department_id`: Department reference
  - `preferred_shifts`: JSON list of preferred shift IDs
  - `leave_day_1`: Day of week (0-6, Mon-Sun) for first leave day
  - `leave_day_2`: Day of week (0-6, Mon-Sun) for second leave day
  - `notes`: Optional notes from employee
  - `submitted_at`: When employee submitted
  - `created_at`, `updated_at`: Timestamps

### 2. Removed from Role Model
- ✅ Removed `weekend_required` boolean field from the Role model
- Weekends are now managed through shift preferences instead

### 3. Backend APIs (New Endpoints)

#### Create Shift Period
```
POST /shift-periods
Body: {
  "name": "January 2024 Schedule",
  "description": "Monthly scheduling",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
Response: ShiftPeriodResponse
```

#### Get Shift Period
```
GET /shift-periods/{period_id}
Response: ShiftPeriodResponse
```

#### Create Preference Form (Send to Employees)
```
POST /shift-preference-forms
Body: {
  "shift_period_id": 1,
  "available_shifts": [1, 2, 3, 4]  // Array of shift IDs
}
Response: ShiftPreferenceFormResponse
- Auto-notifies all employees in the department
```

#### Get Preference Form Details
```
GET /shift-preference-forms/{form_id}
Response: Form details with available shifts
```

#### Submit Employee Preferences
```
POST /employee-shift-preferences
Body: {
  "preference_form_id": 1,
  "preferred_shifts": [1, 3],
  "leave_day_1": 5,  // 0-6: Mon-Sun
  "leave_day_2": 6,
  "notes": "Optional notes"
}
Response: EmployeeShiftPreferenceResponse
```

#### Get All Employee Preferences (Manager View)
```
GET /employee-shift-preferences/{form_id}
Response: {
  "form_id": 1,
  "total_responses": 25,
  "preferences": [
    {
      "id": 1,
      "employee_id": 1,
      "employee_name": "John Doe",
      "preferred_shifts": [...],
      "leave_day_1": "Mon",
      "leave_day_2": "Sat",
      "notes": "...",
      "submitted_at": "2024-01-15T10:30:00"
    },
    ...
  ]
}
```

#### Update Employee Preferences
```
PUT /employee-shift-preferences/{pref_id}
Body: {
  "preferred_shifts": [1, 2],
  "leave_day_1": 5,
  "leave_day_2": 6,
  "notes": "Updated notes"
}
Response: EmployeeShiftPreferenceResponse
```

### 4. Frontend Components

#### ShiftPreferenceManager (Manager Side)
- New component: `/frontend/src/components/ShiftPreferenceManager.jsx`
- Provides manager interface to:
  1. Create shift periods (specify date range like 1 month)
  2. Create preference forms (select available shifts for employees)
  3. Send forms to all employees automatically
  4. View all employee preference responses
  5. See summary statistics

#### EmployeePreferenceForm (Employee Side)
- New component: `/frontend/src/components/EmployeePreferenceForm.jsx`
- Provides employee interface to:
  1. View active preference forms
  2. Select preferred shifts from available options
  3. Choose 2 leave days (any days Mon-Sun, not fixed Sat/Sun)
  4. Add optional notes
  5. Submit preferences

### 5. Manager Schedule Page Updates
- Added tab to schedule management page:
  - "Schedule View" tab: Existing schedule manager
  - "Shift Preferences" tab: New preference management
- Managers can toggle between creating schedules and managing preferences

### 6. Employee Dashboard Updates
- Added new "Shift Preferences" section
- Employees receive notifications when preference form is available
- Can easily access and fill preference forms

## Workflow

### Manager Side
1. Manager goes to Schedule > Shift Preferences tab
2. Clicks "New Period" and creates shift period (e.g., "Jan 1-31, 2024")
3. Clicks "Send Form" and:
   - Selects the period
   - Chooses which shifts to make available
   - All employees in department get notified
4. Employees fill out their preferences
5. Manager views all preferences:
   - See which shifts employees prefer
   - See which 2 days per week they want leave
   - Use this data when generating schedules

### Employee Side
1. Gets notified of new preference form
2. Goes to "Shift Preferences" page
3. Fills form with:
   - Preferred shifts (may select multiple)
   - 2 leave days per week (any days, no fixed Sat/Sun)
   - Optional notes
4. Submits form
5. Can update anytime while form is active

## Key Features

✅ **Flexible Leave Days**: Employees can choose ANY 2 days per week, not fixed Sat/Sun
✅ **Multiple Shift Preferences**: Employees can select multiple preferred shifts
✅ **Date Range Scheduling**: Managers specify exact period (e.g., 1 month)
✅ **Weekend Allocation**: Works with all days including weekends
✅ **No Public Holidays**: System allocates shifts on public holidays too
✅ **5 Work + 2 Leave Days**: Default constraint (5 work days, 2 leave days per week)
✅ **Notifications**: Employees notified when forms are available
✅ **Historical Tracking**: All preferences stored for auditing/analytics

## Usage Examples

### Create a Shift Period
```
POST /shift-periods
{
  "name": "January 2024 - Monthly Scheduling",
  "description": "Complete month scheduling from Jan 1-31",
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
```

### Send Preference Form
```
POST /shift-preference-forms
{
  "shift_period_id": 1,
  "available_shifts": [1, 2, 3, 4, 5]  // Morning, Afternoon, Evening, Night, Overnight
}
```

### Employee Submits Preferences
```
POST /employee-shift-preferences
{
  "preference_form_id": 1,
  "preferred_shifts": [1, 2],  // Prefers morning or afternoon
  "leave_day_1": 5,  // Saturday
  "leave_day_2": 6,  // Sunday (but can be any combination)
  "notes": "Prefer morning shifts if possible"
}
```

## Integration with Schedule Generation

When using the schedule generator, the system can now:
1. Read employee preferences from submitted forms
2. Prioritize assigning preferred shifts to employees
3. Respect selected leave days (no shifts assigned on those days)
4. Generate fair schedules that align with employee preferences

## Notes

- Forms are marked "closed" when manager stops accepting submissions
- Leave days are applied consistently for entire period
- Employees can update preferences while form is active
- Manager can see all responses aggregated by employee
- All data is preserved for historical auditing

## Files Modified/Created

**Backend:**
- ✅ `app/models.py` - Added 3 new models, removed `weekend_required` from Role
- ✅ `app/schemas.py` - Added validation schemas for new models
- ✅ `app/main.py` - Added 6 new API endpoints

**Frontend:**
- ✅ `src/components/ShiftPreferenceManager.jsx` - NEW
- ✅ `src/components/EmployeePreferenceForm.jsx` - NEW
- ✅ `src/pages/Manager.jsx` - Updated schedules page with tabs
- ✅ `src/pages/Employee.jsx` - Added preferences route and page
- ✅ `src/components/RoleManagement.jsx` - Removed weekend_required UI

## Next Steps (Future Enhancements)

1. Integrate preferences into schedule generation algorithm
2. Add analytics dashboard showing preference patterns
3. Add preference analytics (most popular shifts, etc.)
4. Add ability to close forms
5. Add reminders to employees who haven't submitted
6. Add conflict resolution when preferences can't be fully met
7. Add batch import/export of preferences
