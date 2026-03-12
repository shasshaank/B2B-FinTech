import React, { useState } from 'react';
import { Button, Typography, Spin } from 'antd';
import { BulbOutlined } from '@ant-design/icons';
import { analysisAPI } from '../../services/api';

const { Text } = Typography;

const SWOT_CONFIG = {
  strengths: { title: 'Strengths', emoji: '💪', class: 'swot-card swot-strengths', titleColor: '#16a34a' },
  weaknesses: { title: 'Weaknesses', emoji: '⚠️', class: 'swot-card swot-weaknesses', titleColor: '#dc2626' },
  opportunities: { title: 'Opportunities', emoji: '🚀', class: 'swot-card swot-opportunities', titleColor: '#1d4ed8' },
  threats: { title: 'Threats', emoji: '🔥', class: 'swot-card swot-threats', titleColor: '#ea580c' },
};

const SwotAnalysis = ({ entityId, onSwotComplete }) => {
  const [loading, setLoading] = useState(false);
  const [swot, setSwot] = useState(null);

  const generateSwot = async () => {
    setLoading(true);
    try {
      const result = await analysisAPI.generateSwot(entityId);
      setSwot(result);
      if (onSwotComplete) onSwotComplete(result);
    } catch (error) {
      try {
        const existing = await analysisAPI.getSwot(entityId);
        setSwot(existing);
      } catch (e) {}
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Button
          type="primary"
          size="large"
          icon={<BulbOutlined />}
          onClick={generateSwot}
          loading={loading}
          style={{ minWidth: 240, height: 48 }}
        >
          {loading ? 'Generating...' : 'Generate SWOT Analysis'}
        </Button>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" />
          <Text type="secondary">AI is generating SWOT analysis...</Text>
        </div>
      )}

      {swot && !loading && (
        <div className="swot-grid">
          {Object.entries(SWOT_CONFIG).map(([key, config]) => (
            <div key={key} className={config.class}>
              <div className="swot-title" style={{ color: config.titleColor }}>
                <span style={{ fontSize: 18 }}>{config.emoji}</span>
                {config.title}
              </div>
              <ul className="swot-list">
                {(swot[key] || []).map((item, i) => (
                  <li key={i}>
                    <span style={{ color: config.titleColor, fontWeight: 'bold' }}>•</span>
                    <Text style={{ fontSize: 13 }}>{item}</Text>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SwotAnalysis;
