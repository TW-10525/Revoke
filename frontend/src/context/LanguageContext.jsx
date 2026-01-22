import React, { createContext, useContext, useState, useEffect } from 'react';
import translations from '../utils/translations';
import { format } from 'date-fns';
import jaLocale from 'date-fns/locale/ja';

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    const savedLanguage = localStorage.getItem('language');
    return savedLanguage || 'en';
  });

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'en' ? 'ja' : 'en'));
  };

  const t = (key) => {
    return translations[language]?.[key] || translations['en']?.[key] || key;
  };

  const formatDate = (value, { withTime = false, long = false } = {}) => {
    if (!value) return '-';
    const dateObj = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(dateObj.getTime())) return '-';

    const isJa = language === 'ja';
    const locale = isJa ? jaLocale : undefined;

    if (withTime) {
      const pattern = isJa ? 'yyyy年MM月dd日 HH:mm:ss' : 'MMM dd, yyyy HH:mm:ss';
      return format(dateObj, pattern, { locale });
    }

    if (long) {
      const pattern = isJa ? 'yyyy年MM月dd日 EEEE' : 'EEEE, MMMM dd, yyyy';
      return format(dateObj, pattern, { locale });
    }

    const pattern = isJa ? 'yyyy年MM月dd日' : 'MMM dd, yyyy';
    return format(dateObj, pattern, { locale });
  };

  const translateMessage = (message) => {
    if (!message || typeof message !== 'string') return message;
    const normalized = message.toLowerCase();
    const hasStartInvalid = normalized.includes('start_date: input should be a valid date or datetime');
    const hasEndInvalid = normalized.includes('end_date: input should be a valid date or datetime');

    if (hasStartInvalid && hasEndInvalid) {
      return t('startEndDateInvalid');
    }
    if (hasStartInvalid) {
      return t('startDateInvalid');
    }
    if (hasEndInvalid) {
      return t('endDateInvalid');
    }
    return message;
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t, formatDate, translateMessage }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
