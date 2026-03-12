import React, { useState, useRef } from 'react';
import { Button, Card, Row, Col, Typography, Spin, List, Tag, Space } from 'antd';
import { FileTextOutlined, DownloadOutlined, PrinterOutlined } from '@ant-design/icons';
import { analysisAPI } from '../../services/api';

const { Title, Text, Paragraph } = Typography;

const ReportGenerator = ({ entityId }) => {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const reportRef = useRef();

  const generateReport = async () => {
    setLoading(true);
    try {
      const result = await analysisAPI.generateReport(entityId);
      setReport(result.report_data);
    } catch (error) {
      try {
        const existing = await analysisAPI.getReport(entityId);
        setReport(existing.report_data);
      } catch (e) {}
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    const url = analysisAPI.downloadReport(entityId);
    window.open(url, '_blank');
  };

  const printReport = () => {
    window.print();
  };

  const getDecisionColor = (decision) => {
    if (decision === 'APPROVE') return '#16a34a';
    if (decision === 'CONDITIONAL_APPROVE') return '#d97706';
    return '#dc2626';
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Space>
          <Button
            type="primary"
            size="large"
            icon={<FileTextOutlined />}
            onClick={generateReport}
            loading={loading}
            style={{ minWidth: 220, height: 48 }}
          >
            Generate Final Report
          </Button>
          {report && (
            <>
              <Button
                size="large"
                icon={<DownloadOutlined />}
                onClick={downloadPDF}
                style={{ height: 48 }}
              >
                Download PDF
              </Button>
              <Button
                size="large"
                icon={<PrinterOutlined />}
                onClick={printReport}
                style={{ height: 48 }}
              >
                Print
              </Button>
            </>
          )}
        </Space>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" />
          <Text type="secondary">Compiling comprehensive report...</Text>
        </div>
      )}

      {report && !loading && (
        <div ref={reportRef} style={{ background: 'white', padding: '32px', borderRadius: 12 }}>
          {/* Report Header */}
          <div style={{ textAlign: 'center', padding: '24px 0', borderBottom: '3px solid #1d3a8a', marginBottom: 32 }}>
            <Title level={2} style={{ color: '#1d3a8a', marginBottom: 4 }}>CreditLens</Title>
            <Title level={3} style={{ marginTop: 0, marginBottom: 8 }}>AI-Powered Credit Assessment Report</Title>
            <Text type="secondary">Generated: {report.generated_at?.slice(0, 10)} | CONFIDENTIAL</Text>
          </div>

          {/* 1. Executive Summary */}
          <div className="report-section">
            <Title level={4} style={{ color: '#1d3a8a' }}>1. Executive Summary</Title>
            <Paragraph style={{ fontSize: 14, lineHeight: 1.8, color: '#374151' }}>
              {report.executive_summary}
            </Paragraph>
          </div>

          {/* 2. Entity Overview */}
          <div className="report-section">
            <Title level={4} style={{ color: '#1d3a8a' }}>2. Entity Overview</Title>
            <Row gutter={[16, 8]}>
              {Object.entries(report.entity_overview || {}).map(([k, v]) => v && (
                <Col xs={24} md={12} key={k}>
                  <Row>
                    <Col span={12}><Text type="secondary">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</Text></Col>
                    <Col span={12}><Text strong>{String(v)}</Text></Col>
                  </Row>
                </Col>
              ))}
            </Row>
          </div>

          {/* 3. Loan Details */}
          <div className="report-section">
            <Title level={4} style={{ color: '#1d3a8a' }}>3. Loan Details</Title>
            <Row gutter={[16, 8]}>
              {Object.entries(report.loan_details || {}).map(([k, v]) => v && k !== 'id' && k !== 'entity_id' && (
                <Col xs={24} md={12} key={k}>
                  <Row>
                    <Col span={12}><Text type="secondary">{k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</Text></Col>
                    <Col span={12}><Text strong>{String(v)}</Text></Col>
                  </Row>
                </Col>
              ))}
            </Row>
          </div>

          {/* 4. Risk Assessment */}
          <div className="report-section">
            <Title level={4} style={{ color: '#1d3a8a' }}>4. Risk Assessment & Recommendation</Title>
            <div style={{ textAlign: 'center', margin: '16px 0' }}>
              <div style={{
                display: 'inline-block',
                padding: '16px 32px',
                borderRadius: 50,
                fontSize: 22,
                fontWeight: 700,
                color: getDecisionColor(report.risk_assessment?.decision),
                border: `3px solid ${getDecisionColor(report.risk_assessment?.decision)}`,
                background: `${getDecisionColor(report.risk_assessment?.decision)}15`,
              }}>
                {report.risk_assessment?.decision?.replace('_', ' ')}
              </div>
            </div>
            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <Card size="small" title="Risk Score" style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 36, fontWeight: 800, color: getDecisionColor(report.risk_assessment?.decision) }}>
                    {report.risk_assessment?.risk_score}/100
                  </div>
                </Card>
              </Col>
              <Col xs={24} md={12}>
                <Card size="small" title="Confidence">
                  <div style={{ fontSize: 36, fontWeight: 800, color: '#1d3a8a', textAlign: 'center' }}>
                    {report.risk_assessment?.confidence}%
                  </div>
                </Card>
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <Text strong>Reasoning:</Text>
              <List
                size="small"
                dataSource={report.risk_assessment?.reasoning || []}
                renderItem={(item, i) => (
                  <List.Item style={{ padding: '4px 0' }}>
                    <Text>{i + 1}. {item}</Text>
                  </List.Item>
                )}
              />
            </div>
          </div>

          {/* 5. SWOT Analysis */}
          {report.swot_analysis && (
            <div className="report-section">
              <Title level={4} style={{ color: '#1d3a8a' }}>5. SWOT Analysis</Title>
              <div className="swot-grid">
                {[
                  { key: 'strengths', title: 'Strengths', color: '#16a34a', bg: '#f0fdf4' },
                  { key: 'weaknesses', title: 'Weaknesses', color: '#dc2626', bg: '#fef2f2' },
                  { key: 'opportunities', title: 'Opportunities', color: '#1d4ed8', bg: '#eff6ff' },
                  { key: 'threats', title: 'Threats', color: '#ea580c', bg: '#fff7ed' },
                ].map(({ key, title, color, bg }) => (
                  <div key={key} style={{ background: bg, border: `1px solid ${color}30`, borderRadius: 8, padding: 16 }}>
                    <div style={{ fontWeight: 700, color, marginBottom: 8 }}>{title}</div>
                    <ul style={{ paddingLeft: 16, margin: 0 }}>
                      {(report.swot_analysis[key] || []).map((item, i) => (
                        <li key={i} style={{ fontSize: 12, marginBottom: 4, color: '#374151' }}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 6. Secondary Research */}
          {report.secondary_research && (
            <div className="report-section">
              <Title level={4} style={{ color: '#1d3a8a' }}>6. Secondary Research Findings</Title>
              {report.secondary_research.sector_analysis && (
                <Paragraph style={{ color: '#374151' }}>{report.secondary_research.sector_analysis}</Paragraph>
              )}
              <div style={{ marginTop: 12 }}>
                <Text strong>Key Risks: </Text>
                {(report.secondary_research.key_risks || []).map((risk, i) => (
                  <Tag key={i} color="orange" style={{ margin: '2px 4px' }}>{risk}</Tag>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div style={{ textAlign: 'center', paddingTop: 24, borderTop: '1px solid #e8ecf0', color: '#9ca3af', fontSize: 12 }}>
            This report was generated by CreditLens — AI-Powered Enterprise Credit Underwriting Platform
            <br />For internal use only. Not for distribution.
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportGenerator;
