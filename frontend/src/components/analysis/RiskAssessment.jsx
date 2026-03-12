import React, { useState } from 'react';
import { Button, Card, Row, Col, Typography, Spin, Table, Tag, List, Alert, Space } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import { analysisAPI } from '../../services/api';

const { Text } = Typography;

const RiskAssessment = ({ entityId, onRecommendationComplete }) => {
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);

  const generateRecommendation = async () => {
    setLoading(true);
    try {
      const result = await analysisAPI.generateRecommendation(entityId);
      setRecommendation(result);
      if (onRecommendationComplete) onRecommendationComplete(result);
    } catch (error) {
      try {
        const existing = await analysisAPI.getRecommendation(entityId);
        setRecommendation(existing);
      } catch (e) {}
    } finally {
      setLoading(false);
    }
  };

  const getDecisionStyle = (decision) => {
    if (decision === 'APPROVE') return { className: 'decision-badge decision-approve', emoji: '✅' };
    if (decision === 'CONDITIONAL_APPROVE') return { className: 'decision-badge decision-conditional', emoji: '⚠️' };
    return { className: 'decision-badge decision-reject', emoji: '❌' };
  };

  const metricsColumns = [
    { title: 'Metric', dataIndex: 'metric', key: 'metric', render: v => <Text strong>{v}</Text> },
    { title: 'Value', dataIndex: 'value', key: 'value', render: v => <Text style={{ color: '#1d3a8a' }}>{v}</Text> },
  ];

  const metricsData = recommendation?.key_metrics
    ? Object.entries(recommendation.key_metrics).map(([k, v], i) => ({
        key: i,
        metric: k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: typeof v === 'number' ? v.toFixed(2) : String(v),
      }))
    : [];

  const riskScore = recommendation?.risk_score || 0;
  const riskColor = riskScore < 40 ? '#16a34a' : riskScore < 65 ? '#d97706' : '#dc2626';

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Button
          type="primary"
          size="large"
          icon={<ThunderboltOutlined />}
          onClick={generateRecommendation}
          loading={loading}
          style={{ minWidth: 240, height: 48 }}
        >
          {loading ? 'Analyzing...' : 'Generate Risk Assessment'}
        </Button>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" />
          <Text type="secondary">AI is analyzing all financial data...</Text>
        </div>
      )}

      {recommendation && !loading && (
        <Row gutter={[20, 20]}>
          {/* Decision Badge */}
          <Col xs={24} style={{ textAlign: 'center' }}>
            <div style={{ padding: '24px 0' }}>
              <div style={{ marginBottom: 16, color: '#6b7280', fontSize: 14 }}>LOAN RECOMMENDATION</div>
              <div className={getDecisionStyle(recommendation.decision).className} style={{ fontSize: 28, display: 'inline-flex' }}>
                <span>{getDecisionStyle(recommendation.decision).emoji}</span>
                <span>{recommendation.decision?.replace('_', ' ')}</span>
              </div>
              <div style={{ marginTop: 12, color: '#6b7280' }}>
                Confidence: <strong style={{ color: '#1d3a8a' }}>{recommendation.confidence}%</strong>
              </div>
            </div>
          </Col>

          {/* Risk Score Gauge */}
          <Col xs={24} md={8}>
            <Card title="🎯 Risk Score" bordered={false} style={{ textAlign: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <div className="risk-gauge-container">
                <div className="risk-score-display" style={{ color: riskColor }}>{riskScore}</div>
                <Text type="secondary">/ 100</Text>
                <Tag
                  color={riskScore < 40 ? 'success' : riskScore < 65 ? 'warning' : 'error'}
                  style={{ marginTop: 8, fontSize: 13 }}
                >
                  {riskScore < 40 ? 'LOW RISK' : riskScore < 65 ? 'MEDIUM RISK' : 'HIGH RISK'}
                </Tag>
              </div>
            </Card>
          </Col>

          {/* Key Metrics */}
          <Col xs={24} md={16}>
            <Card title="📈 Key Financial Metrics" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <Table
                dataSource={metricsData}
                columns={metricsColumns}
                pagination={false}
                size="small"
              />
            </Card>
          </Col>

          {/* Reasoning */}
          <Col xs={24} md={12}>
            <Card title="📋 Reasoning" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <List
                dataSource={recommendation.reasoning || []}
                renderItem={(item, i) => (
                  <List.Item style={{ padding: '8px 0', borderBottom: '1px solid #f0f2f5' }}>
                    <Text>
                      <Tag color="blue" style={{ minWidth: 24, textAlign: 'center' }}>{i + 1}</Tag>
                      {item}
                    </Text>
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          {/* Conditions */}
          {recommendation.conditions && recommendation.conditions.length > 0 && (
            <Col xs={24} md={12}>
              <Card title="📌 Conditions (if applicable)" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)', border: '2px solid #fef3c7' }}>
                <List
                  dataSource={recommendation.conditions}
                  renderItem={(item, i) => (
                    <List.Item style={{ padding: '8px 0' }}>
                      <Space align="start">
                        <Tag color="warning">{i + 1}</Tag>
                        <Text>{item}</Text>
                      </Space>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}
        </Row>
      )}
    </div>
  );
};

export default RiskAssessment;
