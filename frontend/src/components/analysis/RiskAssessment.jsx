import React, { useState } from 'react';
import {
  Card, Button, Row, Col, Tag, Typography, Space,
  Table, Statistic, Progress, Divider, List,
} from 'antd';
import {
  ThunderboltOutlined, CheckCircleOutlined,
  WarningOutlined, CloseCircleOutlined,
} from '@ant-design/icons';
import { generateRecommendation } from '../../services/api';

const { Text, Title, Paragraph } = Typography;

const DECISION_CONFIG = {
  APPROVE: {
    color: '#52c41a',
    bg: '#f6ffed',
    border: '#52c41a',
    icon: <CheckCircleOutlined />,
    label: 'APPROVED',
  },
  CONDITIONAL_APPROVE: {
    color: '#d48806',
    bg: '#fffbe6',
    border: '#faad14',
    icon: <WarningOutlined />,
    label: 'CONDITIONAL APPROVAL',
  },
  REJECT: {
    color: '#cf1322',
    bg: '#fff1f0',
    border: '#ff4d4f',
    icon: <CloseCircleOutlined />,
    label: 'REJECTED',
  },
};

const RiskAssessment = ({ entityId, recommendation, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await generateRecommendation(entityId);
      if (onUpdate) await onUpdate();
    } catch (err) {
      console.error('Recommendation error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!recommendation) {
    return (
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
        <ThunderboltOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
        <Title level={4}>AI Risk Assessment</Title>
        <Paragraph type="secondary">
          Generate an AI-powered loan recommendation based on all gathered data.
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<ThunderboltOutlined />}
          onClick={handleGenerate}
          loading={loading}
          style={{ minWidth: 220 }}
        >
          Generate Recommendation
        </Button>
      </Card>
    );
  }

  const decision = recommendation.decision || 'CONDITIONAL_APPROVE';
  const config = DECISION_CONFIG[decision] || DECISION_CONFIG.CONDITIONAL_APPROVE;
  const riskScore = recommendation.risk_score || 50;
  const metrics = recommendation.key_metrics || {};

  const metricsData = [
    { label: 'Debt-to-Equity Ratio', value: metrics.debt_to_equity, suffix: 'x' },
    { label: 'Interest Coverage Ratio', value: metrics.interest_coverage_ratio, suffix: 'x' },
    { label: 'Current Ratio', value: metrics.current_ratio, suffix: 'x' },
    { label: 'Return on Assets', value: metrics.return_on_assets, suffix: '%' },
    { label: 'NPA Percentage', value: metrics.npa_percentage, suffix: '%' },
  ];

  const metricsColumns = [
    { title: 'Metric', dataIndex: 'label', key: 'label' },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (val, record) => val != null ? (
        <Text strong>{val}{record.suffix}</Text>
      ) : (
        <Text type="secondary">N/A</Text>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>Risk Assessment & Recommendation</Title>
        <Button icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={loading}>
          Refresh Analysis
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {/* Decision Badge */}
        <Col xs={24}>
          <Card
            style={{ borderRadius: 12, border: `2px solid ${config.border}`, background: config.bg }}
            bodyStyle={{ padding: '24px 32px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                  Loan Recommendation
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8 }}>
                  <span style={{ fontSize: 32, color: config.color }}>{config.icon}</span>
                  <span
                    style={{
                      fontSize: 28,
                      fontWeight: 700,
                      color: config.color,
                      letterSpacing: 2,
                    }}
                  >
                    {config.label}
                  </span>
                </div>
                <Text type="secondary" style={{ marginTop: 4 }}>
                  Confidence: <strong>{recommendation.confidence?.toFixed(0) || 'N/A'}%</strong>
                </Text>
              </div>

              {/* Risk Score */}
              <div style={{ textAlign: 'center' }}>
                <Progress
                  type="circle"
                  percent={riskScore}
                  strokeColor={riskScore < 35 ? '#52c41a' : riskScore < 65 ? '#faad14' : '#ff4d4f'}
                  format={(p) => (
                    <div>
                      <div style={{ fontSize: 20, fontWeight: 700 }}>{p}</div>
                      <div style={{ fontSize: 10, color: '#8c8c8c' }}>RISK</div>
                    </div>
                  )}
                  size={100}
                />
                <div style={{ marginTop: 4, fontSize: 12, color: '#8c8c8c' }}>
                  {riskScore < 35 ? '🟢 Low Risk' : riskScore < 65 ? '🟡 Moderate Risk' : '🔴 High Risk'}
                </div>
              </div>
            </div>
          </Card>
        </Col>

        {/* Key Financial Metrics */}
        <Col xs={24} md={12}>
          <Card title="Key Financial Metrics" style={{ borderRadius: 12 }}>
            <Table
              dataSource={metricsData.map((m, i) => ({ ...m, key: i }))}
              columns={metricsColumns}
              pagination={false}
              size="small"
              showHeader={false}
            />
          </Card>
        </Col>

        {/* Reasoning */}
        <Col xs={24} md={12}>
          <Card title="Reasoning Engine" style={{ borderRadius: 12 }}>
            <List
              dataSource={recommendation.reasoning || []}
              renderItem={(item, index) => (
                <List.Item style={{ padding: '8px 0', alignItems: 'flex-start' }}>
                  <Space align="start">
                    <div
                      style={{
                        minWidth: 24,
                        height: 24,
                        background: '#1890ff',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    >
                      {index + 1}
                    </div>
                    <Text style={{ fontSize: 13 }}>{item}</Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Conditions (if CONDITIONAL_APPROVE) */}
        {decision === 'CONDITIONAL_APPROVE' && recommendation.conditions?.length > 0 && (
          <Col xs={24}>
            <Card
              title={<><WarningOutlined style={{ color: '#faad14', marginRight: 8 }} />Conditions for Approval</>}
              style={{ borderRadius: 12, border: '1px solid #faad14' }}
            >
              <List
                dataSource={recommendation.conditions}
                renderItem={(item, index) => (
                  <List.Item style={{ padding: '8px 0' }}>
                    <Space>
                      <Tag color="warning">{index + 1}</Tag>
                      <Text>{item}</Text>
                    </Space>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default RiskAssessment;
