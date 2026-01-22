import React, { useState, useEffect } from 'react';
import { Calendar, Plus, Send, AlertCircle, X, CheckCircle, Clock } from 'lucide-react';
import { format, addDays, parseISO } from 'date-fns';
import Card from './common/Card';
import Button from './common/Button';
import Modal from './common/Modal';
import { useLanguage } from '../context/LanguageContext';
import api from '../services/api';

const ShiftPreferenceManager = ({ departmentId, shifts = [] }) => {
  const { t } = useLanguage();
  const [showPeriodForm, setShowPeriodForm] = useState(false);
  const [showPreferenceForm, setShowPreferenceForm] = useState(false);
  const [periods, setPeriods] = useState([]);
  const [preferences, setPreferences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [periodForm, setPeriodForm] = useState({
    name: '',
    description: '',
    period_start: '',
    period_end: ''
  });

  const [preferenceForm, setPreferenceForm] = useState({
    shift_period_id: '',
    available_shifts: []
  });

  const [selectedPeriod, setSelectedPeriod] = useState(null);
  const [selectedPreferences, setSelectedPreferences] = useState(null);

  useEffect(() => {
    loadPeriods();
  }, [departmentId]);

  const loadPeriods = async () => {
    try {
      setLoading(true);
      const response = await api.get('/shift-periods');
      setPeriods(response.data || []);
    } catch (err) {
      console.error('Failed to load shift periods:', err);
      setError('Failed to load shift periods');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePeriod = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (!periodForm.name || !periodForm.period_start || !periodForm.period_end) {
        setError('Please fill in all required fields');
        return;
      }

      const response = await api.post('/shift-periods', {
        name: periodForm.name,
        description: periodForm.description,
        period_start: periodForm.period_start,
        period_end: periodForm.period_end
      });

      setSuccess('Shift period created successfully');
      setPeriodForm({
        name: '',
        description: '',
        period_start: '',
        period_end: ''
      });
      setShowPeriodForm(false);
      await loadPeriods();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create shift period');
    }
  };

  const handleCreatePreferenceForm = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (!preferenceForm.shift_period_id) {
        setError('Please select a shift period');
        return;
      }

      if (preferenceForm.available_shifts.length === 0) {
        setError('Please select at least one shift');
        return;
      }

      const response = await api.post('/shift-preference-forms', {
        shift_period_id: parseInt(preferenceForm.shift_period_id),
        available_shifts: preferenceForm.available_shifts.map(s => parseInt(s))
      });

      setSuccess('Preference form sent to all employees!');
      setPreferenceForm({
        shift_period_id: '',
        available_shifts: []
      });
      setShowPreferenceForm(false);
      await loadPreferences(preferenceForm.shift_period_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create preference form');
    }
  };

  const loadPreferences = async (periodId) => {
    try {
      const response = await api.get(`/employee-shift-preferences/${periodId}`);
      setSelectedPreferences(response.data);
    } catch (err) {
      console.error('Failed to load preferences:', err);
    }
  };

  const handleToggleShift = (shiftId) => {
    setPreferenceForm(prev => ({
      ...prev,
      available_shifts: prev.available_shifts.includes(shiftId)
        ? prev.available_shifts.filter(id => id !== shiftId)
        : [...prev.available_shifts, shiftId]
    }));
  };

  const handleViewPreferences = (period) => {
    setSelectedPeriod(period);
    loadPreferences(period.id);
  };

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div className="space-y-6">
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 flex items-center gap-2">
          <CheckCircle size={20} />
          {success}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error}
        </div>
      )}

      {/* Main Actions */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Shift Preference Management</h2>
            <p className="text-sm text-gray-600 mt-1">Create shift periods and collect employee preferences</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowPeriodForm(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2"
            >
              <Calendar size={18} />
              New Period
            </button>
            <button
              onClick={() => setShowPreferenceForm(true)}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2"
            >
              <Send size={18} />
              Send Form
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : periods.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No shift periods created yet. Create one to get started!
          </div>
        ) : (
          <div className="space-y-4">
            {periods.map(period => (
              <div key={period.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">{period.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{period.description}</p>
                    <div className="flex gap-4 mt-2">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Calendar size={16} className="text-blue-600" />
                        {format(parseISO(period.period_start), 'MMM d, yyyy')} - {format(parseISO(period.period_end), 'MMM d, yyyy')}
                      </div>
                      <div className="text-sm text-gray-600">
                        Duration: {Math.ceil((parseISO(period.period_end) - parseISO(period.period_start)) / (1000 * 60 * 60 * 24))} days
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleViewPreferences(period)}
                    className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded font-medium text-sm"
                  >
                    View Responses
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Create Period Modal */}
      <Modal
        isOpen={showPeriodForm}
        onClose={() => setShowPeriodForm(false)}
        title="Create Shift Period"
        maxWidth="md"
      >
        <form onSubmit={handleCreatePeriod} className="space-y-4">
          <div>
            <label htmlFor="periodName" className="block text-sm font-medium text-gray-900 mb-2">
              Period Name *
            </label>
            <input
              id="periodName"
              name="periodName"
              type="text"
              value={periodForm.name}
              onChange={(e) => setPeriodForm({ ...periodForm, name: e.target.value })}
              placeholder="e.g., January 2024 Schedule"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="periodDescription" className="block text-sm font-medium text-gray-900 mb-2">
              Description
            </label>
            <textarea
              id="periodDescription"
              name="periodDescription"
              value={periodForm.description}
              onChange={(e) => setPeriodForm({ ...periodForm, description: e.target.value })}
              placeholder="Optional description"
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Start Date *
              </label>
              <input
                id="periodStart"
                name="periodStart"
                type="date"
                value={periodForm.period_start}
                onChange={(e) => setPeriodForm({ ...periodForm, period_start: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="periodEnd" className="block text-sm font-medium text-gray-900 mb-2">
                End Date *
              </label>
              <input
                id="periodEnd"
                name="periodEnd"
                type="date"
                value={periodForm.period_end}
                onChange={(e) => setPeriodForm({ ...periodForm, period_end: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setShowPeriodForm(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            >
              Create Period
            </button>
          </div>
        </form>
      </Modal>

      {/* Send Preference Form Modal */}
      <Modal
        isOpen={showPreferenceForm}
        onClose={() => setShowPreferenceForm(false)}
        title="Send Shift Preference Form to Employees"
        maxWidth="md"
      >
        <form onSubmit={handleCreatePreferenceForm} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Select Shift Period *
            </label>
            <select
              value={preferenceForm.shift_period_id}
              onChange={(e) => setPreferenceForm({ ...preferenceForm, shift_period_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select a period --</option>
              {periods.map(period => (
                <option key={period.id} value={period.id}>
                  {period.name} ({format(parseISO(period.period_start), 'MMM d')} - {format(parseISO(period.period_end), 'MMM d, yyyy')})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-3">
              Available Shifts *
            </label>
            <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-4">
              {shifts.length === 0 ? (
                <p className="text-sm text-gray-500">No shifts available in this role</p>
              ) : (
                shifts.map(shift => (
                  <label key={shift.id} className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded">
                    <input
                      type="checkbox"
                      checked={preferenceForm.available_shifts.includes(shift.id.toString())}
                      onChange={() => handleToggleShift(shift.id.toString())}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div className="font-medium text-gray-900">{shift.name}</div>
                      <div className="text-sm text-gray-600">{shift.start_time} - {shift.end_time}</div>
                    </div>
                  </label>
                ))
              )}
            </div>
            <p className="text-xs text-gray-600 mt-2">
              Selected: {preferenceForm.available_shifts.length} shift(s)
            </p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="flex gap-2">
              <AlertCircle size={16} className="text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-blue-800">
                <p className="font-semibold">Employee Notification</p>
                <p className="mt-1">All employees in your department will receive a notification to fill out their preferences for:</p>
                <p className="font-semibold mt-2">
                  {periods.find(p => p.id === parseInt(preferenceForm.shift_period_id))?.name || 'Selected Period'}
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setShowPreferenceForm(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2"
            >
              <Send size={16} />
              Send Form to Employees
            </button>
          </div>
        </form>
      </Modal>

      {/* View Preferences Modal */}
      <Modal
        isOpen={!!selectedPeriod}
        onClose={() => {
          setSelectedPeriod(null);
          setSelectedPreferences(null);
        }}
        title={`Shift Preferences - ${selectedPeriod?.name}`}
        maxWidth="lg"
      >
        {selectedPreferences && (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-blue-800">
                <strong>{selectedPreferences.total_responses}</strong> employee(s) have submitted their preferences
              </p>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {selectedPreferences.preferences.length === 0 ? (
                <p className="text-center py-8 text-gray-500">No preferences submitted yet</p>
              ) : (
                selectedPreferences.preferences.map(pref => (
                  <div key={pref.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900">{pref.employee_name}</h4>
                        <p className="text-sm text-gray-600">Employee ID: {pref.employee_id}</p>
                      </div>
                      {pref.submitted_at && (
                        <div className="text-xs text-gray-500">
                          {format(parseISO(pref.submitted_at), 'MMM d, yyyy HH:mm')}
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div>
                        <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Preferred Shifts</p>
                        <div className="space-y-1">
                          {pref.preferred_shifts.length === 0 ? (
                            <p className="text-sm text-gray-600">No preference</p>
                          ) : (
                            pref.preferred_shifts.map((shift, idx) => (
                              <div key={idx} className="text-sm bg-blue-50 p-2 rounded">
                                <strong>{shift.name}</strong> ({shift.start_time} - {shift.end_time})
                              </div>
                            ))
                          )}
                        </div>
                      </div>

                      <div>
                        <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Leave Days</p>
                        <div className="space-y-1">
                          {pref.leave_day_1 !== null && (
                            <div className="text-sm bg-orange-50 p-2 rounded">
                              {dayNames[pref.leave_day_1]}
                            </div>
                          )}
                          {pref.leave_day_2 !== null && (
                            <div className="text-sm bg-orange-50 p-2 rounded">
                              {dayNames[pref.leave_day_2]}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {pref.notes && (
                      <div className="border-t border-gray-200 pt-3">
                        <p className="text-xs font-semibold text-gray-600 uppercase mb-1">Notes</p>
                        <p className="text-sm text-gray-700">{pref.notes}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ShiftPreferenceManager;
