import { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { format, startOfMonth, endOfMonth, addMonths, subMonths, addDays } from 'date-fns';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Table from '../components/common/Table';
import RoleManagement from '../components/RoleManagement';
import ScheduleManager from '../components/ScheduleManager';
import OvertimeApproval from '../components/OvertimeApproval';
import CompOffManagement from '../components/CompOffManagement';
import { useLanguage } from '../context/LanguageContext';
import api from '../services/api';
import {
  listEmployees,
  listLeaveRequests,
  getSchedules,
  getAttendance,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  createRole,
  listRoles,
  listShifts,
  generateSchedule,
  generateSchedules,
  approveLeave,
  rejectLeave,
  sendMessage,
  getMessages,
  deleteMessage,
  deleteShift,
  getEmployeeLeaveStatistics,
  listDepartments
} from '../services/api';
import {
  Plus, Edit2, Trash2, AlertCircle, Clock, CheckCircle, XCircle, ChevronLeft,
  ChevronRight, Calendar, Sparkles, Users, UserCheck, ClipboardList, CalendarDays,
  Send, Building2, LogOut, LayoutDashboard
} from 'lucide-react';

// Import Manager Pages
import { ManagerDashboardHome, ManagerEmployees, ManagerRoles, ManagerSchedules, ManagerLeaves, ManagerAttendance, ManagerMessages } from './Manager';

// DeptAccess Dashboard Page
const DeptAccessDashboard = ({ user, deptId, deptName, onRoleSwitch }) => {
  const { t } = useLanguage();
  const [stats, setStats] = useState({
    totalEmployees: 0,
    pendingLeaves: 0,
    todayScheduled: 0,
    activeEmployees: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [deptId]);

  const loadData = async () => {
    try {
      const [employeesRes, leavesRes] = await Promise.all([
        api.get('/employees', { params: { department_id: deptId } }),
        api.get('/leave-requests', { params: { department_id: deptId } })
      ]);
      const employees = employeesRes.data || [];
      const leaves = leavesRes.data || [];
      setStats({
        totalEmployees: employees.length,
        pendingLeaves: leaves.filter(l => l.status === 'pending').length,
        todayScheduled: 0,
        activeEmployees: employees.filter(e => e.is_active).length
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { title: t('totalEmployees'), value: stats.totalEmployees, icon: Users, color: 'blue' },
    { title: t('pendingLeaves'), value: stats.pendingLeaves, icon: ClipboardList, color: 'yellow' },
    { title: t('activeEmployees'), value: stats.activeEmployees, icon: UserCheck, color: 'green' },
    { title: t('todaysSchedule'), value: stats.todayScheduled, icon: CalendarDays, color: 'purple' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xl text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <Header 
        title={`${t('department')}: ${deptName}`} 
        subtitle={`${t('welcome')}, ${user.full_name}`} 
        user={user} 
        onRoleSwitch={onRoleSwitch} 
      />
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {statCards.map((stat, index) => (
            <Card key={index} padding={false}>
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`p-3 bg-${stat.color}-100 rounded-lg`}>
                    <stat.icon className={`w-8 h-8 text-${stat.color}-600`} />
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title={t('recentActivity')}>
            <div className="space-y-4">
              <p className="text-gray-600">
                {t('youAreManaging')} {stats.totalEmployees} {t('employeesInDepartment')}.
              </p>
              <p className="text-gray-600">
                {stats.pendingLeaves > 0 ? (
                  <span className="text-yellow-600 font-semibold">
                    {stats.pendingLeaves} {t('leaveRequest')}{stats.pendingLeaves > 1 ? 's' : ''} {t('pendingReview')}.
                  </span>
                ) : (
                  t('noPendingLeaveRequests')
                )}
              </p>
            </div>
          </Card>
          <Card title={t('quickTips')}>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• {t('reviewApproveLeaveRegularly')}</p>
              <p>• {t('checkDailyAttendance')}</p>
              <p>• {t('createSchedulesInAdvance')}</p>
              <p>• {t('keepEmployeeInfoUpdated')}</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Wrapper component that handles the DeptAccess routing
const DeptAccessWrapper = ({ user, onLogout, onRoleSwitch }) => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [deptId, setDeptId] = useState(null);
  const [deptName, setDeptName] = useState('');

  useEffect(() => {
    const deptIdFromSession = sessionStorage.getItem('accessDeptId');
    if (deptIdFromSession) {
      setDeptId(parseInt(deptIdFromSession));
      loadDeptName(parseInt(deptIdFromSession));
    } else {
      // Redirect back to admin departments if no dept selected
      navigate('/admin/departments');
    }
  }, [navigate]);

  const loadDeptName = async (id) => {
    try {
      const response = await api.get(`/departments/${id}/details`);
      setDeptName(response.data.name);
    } catch (error) {
      console.error('Failed to load department name:', error);
    }
  };

  const handleBackToDepartments = () => {
    sessionStorage.removeItem('accessDeptId');
    navigate('/admin/departments');
  };

  if (!deptId) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <DeptAccessSidebar user={user} onLogout={onLogout} onBack={handleBackToDepartments} deptName={deptName} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <Routes>
            <Route 
              path="/dashboard" 
              element={<DeptAccessDashboard user={user} deptId={deptId} deptName={deptName} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/employees" 
              element={<ManagerEmployees user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/schedules" 
              element={<ManagerSchedules user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/roles" 
              element={<ManagerRoles user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/overtime-approvals" 
              element={<OvertimeApproval user={{ ...user, manager_department_id: deptId }} />} 
            />
            <Route 
              path="/leaves" 
              element={<ManagerLeaves user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/comp-off" 
              element={<CompOffManagement user={{ ...user, manager_department_id: deptId }} />} 
            />
            <Route 
              path="/attendance" 
              element={<ManagerAttendance user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route 
              path="/messages" 
              element={<ManagerMessages user={{ ...user, manager_department_id: deptId }} onRoleSwitch={onRoleSwitch} />} 
            />
            <Route path="/" element={<Navigate to="/admin/access-dept/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

// Custom sidebar for DeptAccess
const DeptAccessSidebar = ({ user, onLogout, onBack, deptName }) => {
  const { t } = useLanguage();

  const navItems = [
    { path: '/admin/access-dept/dashboard', icon: LayoutDashboard, label: t('dashboard') },
    { path: '/admin/access-dept/employees', icon: Users, label: t('manageEmployees') },
    { path: '/admin/access-dept/schedules', icon: Calendar, label: t('scheduleManagement') },
    { path: '/admin/access-dept/roles', icon: ClipboardList, label: t('roleManagement') },
    { path: '/admin/access-dept/overtime-approvals', icon: Clock, label: t('overtimeApprovals') },
    { path: '/admin/access-dept/leaves', icon: UserCheck, label: t('leaveManagement') },
    { path: '/admin/access-dept/comp-off', icon: Sparkles, label: t('compOffRequests') },
    { path: '/admin/access-dept/attendance', icon: Clock, label: t('attendance') },
    { path: '/admin/access-dept/messages', icon: Send, label: t('notifications') },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white w-64">
      {/* Logo & Dept Info */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center gap-1 mb-2">
          <img
            src="../../images/Logo.png" 
            alt="Thirdwave Group Logo"
            className="w-10 h-10"
          />
          <h1 className="text-2xl font-bold">{t('thirdwaveGroup')}</h1>
        </div>
        <p className="text-sm text-gray-400 mt-1">{t('departmentAccess')}</p>
        <div className="mt-3 p-2 bg-blue-900 rounded-lg border border-blue-700">
          <p className="text-xs text-blue-300 uppercase tracking-wide">{t('department')}</p>
          <p className="text-sm font-semibold text-white truncate">{deptName}</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        {navItems.map((item) => (
          <a
            key={item.path}
            href={item.path}
            className={`flex items-center px-4 py-3 mb-2 rounded-lg transition-colors ${
              window.location.pathname === item.path
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <item.icon className="w-5 h-5 mr-3" />
            <span>{item.label}</span>
          </a>
        ))}
      </nav>

      {/* Back & User Info */}
      <div className="p-4 border-t border-gray-700">
        <button
          onClick={onBack}
          className="flex items-center w-full px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors mb-2"
        >
          <ChevronLeft className="w-5 h-5 mr-3" />
          <span>{t('backToDepartments')}</span>
        </button>
        <div className="px-4 py-2 mb-2">
          <p className="text-sm font-medium">{user.full_name}</p>
          <p className="text-xs text-gray-400">{user.email}</p>
        </div>
        <button
          onClick={onLogout}
          className="flex items-center w-full px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5 mr-3" />
          <span>{t('logout')}</span>
        </button>
      </div>
    </div>
  );
};

export default DeptAccessWrapper;
