import React from 'react';
import './MetricsCard.css';

const MetricsCard = ({ title, value, subtitle, icon, trend, loading, error, iconType }) => {
  if (loading) {
    return (
      <div className="metrics-card loading">
        <div className="metrics-card-header">
          <div className="metrics-card-skeleton" style={{ width: '48px', height: '48px', borderRadius: '8px' }}></div>
          <div className="metrics-card-skeleton" style={{ width: '120px', height: '14px' }}></div>
        </div>
        <div className="metrics-card-skeleton" style={{ width: '80px', height: '36px', marginBottom: '8px' }}></div>
        <div className="metrics-card-skeleton" style={{ width: '150px', height: '13px' }}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="metrics-card">
        <div className="metrics-card-header">
          <div className={`metrics-card-icon ${iconType || ''}`}>
            {icon || '⚠️'}
          </div>
          <div className="metrics-card-title">{title}</div>
        </div>
        <div className="metrics-card-error">{error}</div>
      </div>
    );
  }

  return (
    <div className="metrics-card">
      <div className="metrics-card-header">
        <div className={`metrics-card-icon ${iconType || ''}`}>
          {icon || '📊'}
        </div>
        <div className="metrics-card-title">{title}</div>
      </div>
      <div className="metrics-card-value">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      {subtitle && <div className="metrics-card-subtitle">{subtitle}</div>}
      {trend && (
        <div className={`metrics-card-trend ${trend.type || 'neutral'}`}>
          {trend.type === 'positive' && '↑'}
          {trend.type === 'negative' && '↓'}
          {trend.type === 'neutral' && '→'}
          {trend.value}
        </div>
      )}
    </div>
  );
};

export default MetricsCard;
