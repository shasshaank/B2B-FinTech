import React, { useState } from 'react';
import {
  Card, Button, Row, Col, Tag, Typography, Space,
  Alert, Skeleton, Divider, Progress,
} from 'antd';
import {
  SearchOutlined, GlobalOutlined, AlertOutlined,
  RiseOutlined, SafetyCertificateOutlined,
} from '@ant-design/icons';
import { runSecondaryResearch } from '../../services/api';

const { Text, Title, Paragraph } = Typography;

const getSentimentColor = (sentiment) => {
  const map = { Positive: 'success', Negative: 'error', Neutral: 'default' };
  return map[sentiment] || 'default';
};

const SecondaryResearch = ({ entityId, research, onUpdate }) => {
  const [loading, setLoading] = useState(false);

  const handleRunResearch = async () => {
    setLoading(true);
    try {
      await runSecondaryResearch(entityId);
      if (onUpdate) await onUpdate();
    } catch (err) {
      console.error('Research error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!research && !loading) {
    return (
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
        <GlobalOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
        <Title level={4}>Secondary Research</Title>
        <Paragraph type="secondary">
          Run AI-powered secondary research to gather recent news, market sentiment,
          legal information, and sector analysis.
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<SearchOutlined />}
          onClick={handleRunResearch}
          style={{ minWidth: 200 }}
        >
          Run Secondary Research
        </Button>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card style={{ borderRadius: 12, padding: 24 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <SearchOutlined style={{ fontSize: 32, color: '#1890ff' }} />
          <div style={{ marginTop: 8 }}>
            <Text style={{ color: '#1890ff', fontWeight: 500 }}>Researching company data...</Text>
          </div>
        </div>
        <Skeleton active paragraph={{ rows: 6 }} />
      </Card>
    );
  }

  const sentiment = research?.market_sentiment || {};
  const sentimentScore = sentiment.score || 50;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>Secondary Research Results</Title>
        <Button icon={<SearchOutlined />} onClick={handleRunResearch} loading={loading}>
          Refresh Research
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {/* Market Sentiment Gauge */}
        <Col xs={24} md={8}>
          <Card style={{ borderRadius: 12, textAlign: 'center' }} title="Market Sentiment">
            <Progress
              type="dashboard"
              percent={sentimentScore}
              strokeColor={
                sentimentScore >= 70 ? '#52c41a' :
                sentimentScore >= 40 ? '#faad14' : '#ff4d4f'
              }
              format={(p) => (
                <div>
                  <div style={{ fontSize: 24, fontWeight: 700 }}>{p}</div>
                  <div style={{ fontSize: 12, color: '#8c8c8c' }}>/100</div>
                </div>
              )}
            />
            <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
              {sentiment.summary}
            </Paragraph>
          </Card>
        </Col>

        {/* Sector Analysis */}
        <Col xs={24} md={16}>
          <Card
            style={{ borderRadius: 12 }}
            title={<><RiseOutlined style={{ marginRight: 8, color: '#1890ff' }} />Sector Analysis</>}
          >
            <Paragraph style={{ marginBottom: 0 }}>
              {research?.sector_analysis || 'No sector analysis available.'}
            </Paragraph>
          </Card>
        </Col>

        {/* Recent News */}
        <Col xs={24} md={14}>
          <Card
            style={{ borderRadius: 12 }}
            title={<><GlobalOutlined style={{ marginRight: 8, color: '#1890ff' }} />Recent News</>}
          >
            {(research?.news || []).map((item, i) => (
              <div key={i} className="news-card">
                <div className="news-headline">{item.headline}</div>
                <div className="news-meta">
                  <span>{item.source}</span>
                  <span>•</span>
                  <span>{item.date}</span>
                  <Tag
                    color={getSentimentColor(item.sentiment)}
                    style={{ margin: 0, fontSize: 11, borderRadius: 4 }}
                  >
                    {item.sentiment}
                  </Tag>
                </div>
                {item.snippet && (
                  <Paragraph
                    type="secondary"
                    ellipsis={{ rows: 2 }}
                    style={{ marginTop: 4, marginBottom: 0, fontSize: 12 }}
                  >
                    {item.snippet}
                  </Paragraph>
                )}
              </div>
            ))}
          </Card>
        </Col>

        {/* Legal & Key Risks */}
        <Col xs={24} md={10}>
          <Space direction="vertical" style={{ width: '100%' }} size={16}>
            <Card
              style={{ borderRadius: 12 }}
              title={<><SafetyCertificateOutlined style={{ marginRight: 8, color: '#52c41a' }} />Legal & Regulatory</>}
            >
              {(research?.legal || []).map((item, i) => (
                <Alert
                  key={i}
                  message={item.description}
                  type={item.severity === 'High' ? 'error' : item.severity === 'Medium' ? 'warning' : 'success'}
                  style={{ borderRadius: 6, marginBottom: 8, fontSize: 12 }}
                  showIcon
                />
              ))}
            </Card>

            <Card
              style={{ borderRadius: 12 }}
              title={<><AlertOutlined style={{ marginRight: 8, color: '#ff4d4f' }} />Key Risk Signals</>}
            >
              {(research?.key_risks || []).map((risk, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'flex-start' }}>
                  <span style={{ color: '#ff4d4f', fontWeight: 700, minWidth: 16 }}>•</span>
                  <Text style={{ fontSize: 13 }}>{risk}</Text>
                </div>
              ))}
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default SecondaryResearch;
