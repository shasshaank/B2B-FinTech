import React, { useState } from 'react';
import { Button, Card, Tag, Row, Col, Typography, Spin, List, Badge } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { analysisAPI } from '../../services/api';

const { Text, Paragraph } = Typography;

const getSentimentColor = (sentiment) => {
  if (!sentiment) return 'default';
  const s = sentiment.toLowerCase();
  if (s === 'positive') return 'success';
  if (s === 'negative') return 'error';
  return 'processing';
};

const SecondaryResearch = ({ entityId, onResearchComplete }) => {
  const [loading, setLoading] = useState(false);
  const [research, setResearch] = useState(null);

  const runResearch = async () => {
    setLoading(true);
    try {
      const result = await analysisAPI.runSecondaryResearch(entityId);
      setResearch(result);
      if (onResearchComplete) onResearchComplete(result);
    } catch (error) {
      // Try to get existing
      try {
        const existing = await analysisAPI.getSecondaryResearch(entityId);
        setResearch(existing);
      } catch (e) {}
    } finally {
      setLoading(false);
    }
  };

  const sentimentScore = research?.market_sentiment?.score || 0;
  const sentimentColor = sentimentScore >= 60 ? '#16a34a' : sentimentScore >= 40 ? '#d97706' : '#dc2626';

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Button
          type="primary"
          size="large"
          icon={<SearchOutlined />}
          onClick={runResearch}
          loading={loading}
          style={{ minWidth: 240, height: 48 }}
        >
          {loading ? 'Researching...' : 'Run Secondary Research'}
        </Button>
        <p style={{ marginTop: 8, color: '#6b7280', fontSize: 13 }}>
          AI-powered research from news, regulatory sources, and sector analysis
        </p>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" />
          <Text type="secondary">Gathering market intelligence...</Text>
        </div>
      )}

      {research && !loading && (
        <Row gutter={[20, 20]}>
          {/* Market Sentiment */}
          <Col xs={24} md={8}>
            <Card title="📊 Market Sentiment" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <div className="risk-gauge-container">
                <div className="risk-score-display" style={{ color: sentimentColor }}>
                  {sentimentScore}
                </div>
                <Text type="secondary">/ 100</Text>
                <Tag
                  color={sentimentScore >= 60 ? 'success' : sentimentScore >= 40 ? 'warning' : 'error'}
                  style={{ marginTop: 8, fontSize: 14, padding: '4px 12px' }}
                >
                  {sentimentScore >= 60 ? 'Positive' : sentimentScore >= 40 ? 'Neutral' : 'Negative'}
                </Tag>
              </div>
              <Paragraph style={{ marginTop: 16, fontSize: 13, color: '#4b5563' }}>
                {research.market_sentiment?.summary}
              </Paragraph>
            </Card>
          </Col>

          {/* Key Risks */}
          <Col xs={24} md={16}>
            <Card title="⚠️ Key Risks Identified" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <List
                dataSource={research.key_risks || []}
                renderItem={(risk, i) => (
                  <List.Item style={{ padding: '8px 0' }}>
                    <Badge count={i + 1} style={{ background: '#1d3a8a' }} />
                    <Text style={{ marginLeft: 12 }}>{risk}</Text>
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          {/* Recent News */}
          <Col xs={24}>
            <Card title="📰 Recent News & Developments" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
              <Row gutter={[12, 12]}>
                {(research.news || []).map((item, i) => (
                  <Col xs={24} md={12} key={i}>
                    <div className="news-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                        <Tag color={getSentimentColor(item.sentiment)}>{item.sentiment}</Tag>
                        <Text type="secondary" style={{ fontSize: 12 }}>{item.source} • {item.date}</Text>
                      </div>
                      <Text strong style={{ fontSize: 14 }}>{item.headline}</Text>
                    </div>
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>

          {/* Legal & Regulatory */}
          {research.legal && research.legal.length > 0 && (
            <Col xs={24} md={12}>
              <Card title="⚖️ Legal & Regulatory" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
                <List
                  dataSource={research.legal}
                  renderItem={(item) => (
                    <List.Item>
                      <Tag color={item.severity === 'High' ? 'error' : item.severity === 'Medium' ? 'warning' : 'success'}>
                        {item.severity}
                      </Tag>
                      <Text style={{ marginLeft: 8 }}>{item.description}</Text>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}

          {/* Sector Analysis */}
          {research.sector_analysis && (
            <Col xs={24} md={research.legal?.length > 0 ? 12 : 24}>
              <Card title="🏭 Sector Analysis" bordered={false} style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
                <Paragraph style={{ color: '#374151', lineHeight: 1.8 }}>
                  {research.sector_analysis}
                </Paragraph>
              </Card>
            </Col>
          )}
        </Row>
      )}
    </div>
  );
};

export default SecondaryResearch;
