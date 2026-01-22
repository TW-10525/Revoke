import React, { useState, useEffect } from 'react';
import { Send, AlertCircle, CheckCircle, Calendar, Clock } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import Card from './common/Card';
import Button from './common/Button';
import Modal from './common/Modal';
import { useLanguage } from '../context/LanguageContext';
import api from '../services/api';

const EmployeePreferenceForm = () => {
  const { t } = useLanguage();
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedForm, setSelectedForm] = useState(null);

  const [preferenceData, setPreferenceData] = useState({
    preferred_shifts: [],
    leave_day_1: null,
    leave_day_2: null,
    notes: ''
  });

  useEffect(() => {
    loadForms();
  }, []);

  const loadForms = async () => {
    try {
      setLoading(true);
      // Note: API endpoint to get active forms for employee
      const response = await api.get('/shift-preference-forms');
      setForms(response.data || []);
    } catch (err) {
      console.error('Failed to load preference forms:', err);
      // This is expected if endpoint doesn't exist yet
    } finally {
      setLoading(false);
    }
  };

  const handleSelectShift = (shiftId) => {
    setPreferenceData(prev => ({
      ...prev,
      preferred_shifts: prev.preferred_shifts.includes(shiftId)
        ? prev.preferred_shifts.filter(id => id !== shiftId)
        : [...prev.preferred_shifts, shiftId]
    }));
  };

  const handleSelectLeaveDay = (dayIndex) => {
    if (preferenceData.leave_day_1 === dayIndex) {
      setPreferenceData(prev => ({ ...prev, leave_day_1: null }));
    } else if (preferenceData.leave_day_2 === dayIndex) {
      setPreferenceData(prev => ({ ...prev, leave_day_2: null }));
    } else if (preferenceData.leave_day_1 === null) {
      setPreferenceData(prev => ({ ...prev, leave_day_1: dayIndex }));
    } else if (preferenceData.leave_day_2 === null) {
      setPreferenceData(prev => ({ ...prev, leave_day_2: dayIndex }));
    }
  };

  const handleSubmitPreference = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (preferenceData.preferred_shifts.length === 0) {
        setError('Please select at least one shift preference');
        return;
      }

      if (preferenceData.leave_day_1 === null || preferenceData.leave_day_2 === null) {
        setError('Please select both leave days');
        return;
      }

      if (preferenceData.leave_day_1 === preferenceData.leave_day_2) {
        setError('Leave days must be different');
        return;
      }

      const response = await api.post('/employee-shift-preferences', {
        preference_form_id: selectedForm.id,
        preferred_shifts: preferenceData.preferred_shifts,
        leave_day_1: preferenceData.leave_day_1,
        leave_day_2: preferenceData.leave_day_2,
        notes: preferenceData.notes
      });

      setSuccess('Your shift preferences have been submitted!');
      setShowModal(false);
      setPreferenceData({
        preferred_shifts: [],
        leave_day_1: null,
        leave_day_2: null,
        notes: ''
      });
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit preferences');
    }
  };

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  const handleOpenForm = async (form) => {
    setSelectedForm(form);
    setShowModal(true);
    setError('');
    setSuccess('');
    setPreferenceData({
      preferred_shifts: [],
      leave_day_1: null,
      leave_day_2: null,
      notes: ''
    });
  };

  return (
    <div className="space-y-6">
      {error && !showModal && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 flex items-center gap-2">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 flex items-center gap-2">
          <CheckCircle size={20} />
          {success}
        </div>
      )}

      <Card className="p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Shift Preference Forms</h2>
          <p className="text-sm text-gray-600 mt-1">Submit your shift and leave day preferences for the upcoming schedules</p>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading forms...</div>
        ) : forms.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No preference forms available at this time.</p>
            <p className="text-sm mt-2">Your manager will send one when they're ready to schedule shifts.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {forms.map(form => (
              <div
                key={form.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">
                      Shift Preference - {form.period?.name || 'Shift Period'}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {form.period?.description}
                    </p>
                    <div className="flex gap-4 mt-3">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Calendar size={16} className="text-blue-600" />
                        {form.period && (
                          <>
                            {format(parseISO(form.period.period_start), 'MMM d, yyyy')} -{' '}
                            {format(parseISO(form.period.period_end), 'MMM d, yyyy')}
                          </>
                        )}
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-700">
                          <strong>{form.available_shifts?.length || 0}</strong> available shift(s)
                        </span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleOpenForm(form)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm flex items-center gap-2 ml-4 flex-shrink-0"
                  >
                    <Send size={16} />
                    Fill Form
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Preference Form Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setSelectedForm(null);
        }}
        title="Submit Shift Preferences"
        maxWidth="lg"
      >
        {selectedForm && (
          <form onSubmit={handleSubmitPreference} className="space-y-6">
            {/* Shift Preferences */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Select Your Preferred Shifts *
              </label>
              <div className="space-y-2 border border-gray-200 rounded-lg p-4">
                {selectedForm.available_shifts.length === 0 ? (
                  <p className="text-sm text-gray-500">No shifts available</p>
                ) : (
                  selectedForm.available_shifts.map(shift => (
                    <label
                      key={shift.id}
                      className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-3 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={preferenceData.preferred_shifts.includes(shift.id)}
                        onChange={() => handleSelectShift(shift.id)}
                        className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{shift.name}</div>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Clock size={14} />
                          {shift.start_time} - {shift.end_time}
                        </div>
                      </div>
                    </label>
                  ))
                )}
              </div>
              {preferenceData.preferred_shifts.length === 0 && (
                <p className="text-xs text-red-600 mt-2">Please select at least one shift</p>
              )}
            </div>

            {/* Leave Days Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-3">
                Select Your 2 Preferred Leave Days Per Week *
              </label>
              <p className="text-xs text-gray-600 mb-3">
                Choose any 2 days (Monday-Sunday) that will be your regular leave days throughout the shift period.
              </p>
              <div className="grid grid-cols-7 gap-2">
                {dayNames.map((day, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectLeaveDay(idx)}
                    className={`p-3 rounded-lg font-medium text-sm transition ${
                      preferenceData.leave_day_1 === idx || preferenceData.leave_day_2 === idx
                        ? 'bg-orange-500 text-white border-2 border-orange-600'
                        : 'bg-gray-100 text-gray-900 border-2 border-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    {day.substring(0, 3)}
                  </button>
                ))}
              </div>
              <div className="mt-3 flex gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-orange-500 rounded"></div>
                  <span className="text-sm text-gray-700">Selected days: </span>
                </div>
                <div className="text-sm font-semibold text-gray-900">
                  {preferenceData.leave_day_1 !== null
                    ? dayNames[preferenceData.leave_day_1]
                    : 'Not selected'}{' '}
                  {preferenceData.leave_day_2 !== null
                    ? `& ${dayNames[preferenceData.leave_day_2]}`
                    : preferenceData.leave_day_1 !== null
                    ? '& Not selected'
                    : ''}
                </div>
              </div>
              {(preferenceData.leave_day_1 === null || preferenceData.leave_day_2 === null) && (
                <p className="text-xs text-red-600 mt-2">Please select both leave days</p>
              )}
            </div>

            {/* Additional Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Additional Notes (Optional)
              </label>
              <textarea
                value={preferenceData.notes}
                onChange={(e) => setPreferenceData({ ...preferenceData, notes: e.target.value })}
                placeholder="Any special requests or notes for your manager..."
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex gap-2">
                <AlertCircle size={16} className="text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-blue-800">
                  <p className="font-semibold">Important Information</p>
                  <ul className="list-disc list-inside space-y-1 mt-1">
                    <li>Your leave days will be fixed throughout the entire shift period</li>
                    <li>You will work 5 days per week with your selected 2 leave days</li>
                    <li>The manager will use your preferences to create your schedule</li>
                    <li>Shifts will be allocated across all days including weekends</li>
                  </ul>
                </div>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm flex items-center gap-2">
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            {/* Buttons */}
            <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={() => {
                  setShowModal(false);
                  setSelectedForm(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium flex items-center gap-2"
              >
                <Send size={16} />
                Submit Preferences
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};

export default EmployeePreferenceForm;
