import React, { useState } from 'react';
import { Card, Button, Typography, Space, message } from 'antd';
import {
  ThunderboltOutlined,
  CheckCircleOutlined, CloseCircleOutlined,
  StarOutlined, WarningOutlined,
} from '@ant-design/icons';
import { generateSwot } from '../../services/api';

const { Text, Title, Paragraph } = Typography;

const SWOT_CONFIG = [
  {
    key: 'strengths',
    label: 'Strengths',
    icon: <CheckCircleOutlined />,
    className: 'swot-strengths',
    color: '#52c41a',
    emoji: '💪',
  },
  {
    key: 'weaknesses',
    label: 'Weaknesses',
    icon: <CloseCircleOutlined />,
    className: 'swot-weaknesses',
    color: '#ff4d4f',
    emoji: '⚠️',
  },
  {
    key: 'opportunities',
    label: 'Opportunities',
    icon: <StarOutlined />,
    className: 'swot-opportunities',
    color: '#1890ff',
    emoji: '🚀',
  },
  {
    key: 'threats',
    label: 'Threats',
    icon: <WarningOutlined />,
    className: 'swot-threats',
    color: '#fa8c16',
    emoji: '⚡',
  },
];

const SwotAnalysis = ({ entityId, swot, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await generateSwot(entityId);
      if (onUpdate) await onUpdate();
    } catch (err) {
      message.error(`SWOT generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!swot) {
    return (
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📊</div>
        <Title level={4}>SWOT Analysis</Title>
        <Paragraph type="secondary">
          Generate an AI-powered SWOT analysis based on financial data and secondary research.
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<ThunderboltOutlined />}
          onClick={handleGenerate}
          loading={loading}
          style={{ minWidth: 200 }}
        >
          Generate SWOT Analysis
        </Button>
      </Card>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>SWOT Analysis</Title>
        <Button icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={loading}>
          Regenerate
        </Button>
      </div>

      <div className="swot-grid">
        {SWOT_CONFIG.map((config) => (
          <div key={config.key} className={`swot-card ${config.className}`}>
            <div className="swot-title" style={{ color: config.color }}>
              <span style={{ fontSize: 20 }}>{config.emoji}</span>
              <span>{config.label}</span>
            </div>
            {(swot[config.key] || []).map((item, i) => (
              <div key={i} className="swot-item">
                <span style={{ color: config.color, fontWeight: 700, minWidth: 16 }}>•</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SwotAnalysis;
