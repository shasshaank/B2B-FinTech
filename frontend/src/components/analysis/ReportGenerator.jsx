import React, { useState, useRef } from 'react';
import {
  Card, Button, Typography, Divider, Row, Col, Tag, Space,
  Table, List, message,
} from 'antd';
import {
  FilePdfOutlined, DownloadOutlined, ThunderboltOutlined,
  PrinterOutlined,
} from '@ant-design/icons';
import { generateReport, getReportDownloadUrl } from '../../services/api';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const { Text, Title, Paragraph } = Typography;

const DECISION_COLORS = {
  APPROVE: '#52c41a',
  CONDITIONAL_APPROVE: '#faad14',
  REJECT: '#ff4d4f',
};

const ReportGenerator = ({ entityId, reportData, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const reportRef = useRef(null);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await generateReport(entityId);
      if (onUpdate) await onUpdate();
      message.success('Report generated successfully!');
    } catch (err) {
      message.error(`Report generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    // Try backend PDF first, fall back to client-side generation
    setDownloading(true);
    try {
      const url = getReportDownloadUrl(entityId);
      const link = document.createElement('a');
      link.href = url;
      link.download = `credit_report_entity_${entityId}.pdf`;
      link.click();
      message.success('Report download started');
    } catch (err) {
      // Fallback: generate from HTML
      try {
        const canvas = await html2canvas(reportRef.current, { scale: 1.5 });
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        const ratio = Math.min(pageWidth / imgWidth, pageHeight / imgHeight);
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth * ratio, imgHeight * ratio);
        pdf.save(`credit_report_entity_${entityId}.pdf`);
        message.success('PDF downloaded successfully');
      } catch (err2) {
        message.error('Failed to generate PDF');
      }
    } finally {
      setDownloading(false);
    }
  };

  if (!reportData) {
    return (
      <Card style={{ borderRadius: 12, textAlign: 'center', padding: 40 }}>
        <FilePdfOutlined style={{ fontSize: 48, color: '#1890ff', marginBottom: 16 }} />
        <Title level={4}>Final Credit Report</Title>
        <Paragraph type="secondary">
          Generate the comprehensive credit assessment report including all analyses.
        </Paragraph>
        <Button
          type="primary"
          size="large"
          icon={<ThunderboltOutlined />}
          onClick={handleGenerate}
          loading={loading}
          style={{ minWidth: 220 }}
        >
          Generate Final Report
        </Button>
      </Card>
    );
  }

  const entity = reportData.entity_overview || {};
  const loan = reportData.loan_details || {};
  const rec = reportData.recommendation || {};
  const swot = reportData.swot_analysis || {};
  const research = reportData.secondary_research || {};
  const decision = rec.decision || 'PENDING';

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={4} style={{ margin: 0 }}>Credit Assessment Report</Title>
        <Space>
          <Button icon={<ThunderboltOutlined />} onClick={handleGenerate} loading={loading}>
            Regenerate
          </Button>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleDownloadPDF}
            loading={downloading}
          >
            Download PDF
          </Button>
        </Space>
      </div>

      {/* Report Preview */}
      <div className="report-container" ref={reportRef} id="report-preview">
        {/* Header */}
        <div className="report-header">
          <div style={{ fontSize: 28, fontWeight: 700, color: '#1890ff', letterSpacing: 2 }}>
            CREDITLENS
          </div>
          <div style={{ fontSize: 14, color: '#8c8c8c', marginTop: 4 }}>
            AI-Powered Enterprise Credit Underwriting Platform
          </div>
          <Divider style={{ margin: '16px 0 12px' }} />
          <Title level={3} style={{ margin: 0 }}>Credit Assessment Report</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            {entity.company_name} | Generated: {new Date(reportData.generated_at || Date.now()).toLocaleDateString('en-IN')}
          </Text>
        </div>

        {/* Decision Banner */}
        <div
          style={{
            background: `${DECISION_COLORS[decision]}15`,
            border: `2px solid ${DECISION_COLORS[decision] || '#1890ff'}`,
            borderRadius: 10,
            padding: '16px 24px',
            marginBottom: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase' }}>
              Final Recommendation
            </Text>
            <div style={{
              fontSize: 24,
              fontWeight: 700,
              color: DECISION_COLORS[decision] || '#1890ff',
              marginTop: 4,
            }}>
              {decision.replace('_', ' ')}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>Risk Score</Text>
            <div style={{
              fontSize: 32,
              fontWeight: 700,
              color: DECISION_COLORS[decision],
            }}>
              {rec.risk_score?.toFixed(0) || 'N/A'}<span style={{ fontSize: 16 }}>/100</span>
            </div>
          </div>
        </div>

        {/* 1. Executive Summary */}
        <div className="report-section">
          <div className="report-section-title">1. Executive Summary</div>
          <Paragraph style={{ fontSize: 13, lineHeight: 1.8 }}>
            {reportData.executive_summary}
          </Paragraph>
        </div>

        <Divider />

        {/* 2. Entity Overview */}
        <div className="report-section">
          <div className="report-section-title">2. Entity Overview</div>
          <Row gutter={[16, 8]}>
            {[
              ['Company Name', entity.company_name],
              ['CIN', entity.cin],
              ['PAN', entity.pan],
              ['Sector', entity.sector],
              ['Sub-sector', entity.sub_sector],
              ['Annual Turnover', entity.annual_turnover ? `₹${entity.annual_turnover} Cr` : 'N/A'],
              ['Net Worth', entity.net_worth ? `₹${entity.net_worth} Cr` : 'N/A'],
              ['Credit Rating', entity.credit_rating],
              ['Rating Agency', entity.rating_agency],
            ].map(([label, value]) => (
              <Col xs={24} md={12} key={label}>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Text type="secondary" style={{ minWidth: 140, fontSize: 12 }}>{label}:</Text>
                  <Text strong style={{ fontSize: 12 }}>{value || 'N/A'}</Text>
                </div>
              </Col>
            ))}
            {entity.registered_address && (
              <Col xs={24}>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Text type="secondary" style={{ minWidth: 140, fontSize: 12 }}>Address:</Text>
                  <Text style={{ fontSize: 12 }}>{entity.registered_address}</Text>
                </div>
              </Col>
            )}
          </Row>
        </div>

        <Divider />

        {/* 3. Loan Details */}
        <div className="report-section">
          <div className="report-section-title">3. Loan Details</div>
          <Row gutter={[16, 8]}>
            {[
              ['Loan Type', loan.loan_type],
              ['Loan Amount', loan.loan_amount ? `₹${loan.loan_amount} Cr` : 'N/A'],
              ['Tenure', loan.tenure_months ? `${loan.tenure_months} months` : 'N/A'],
              ['Interest Rate', loan.interest_rate ? `${loan.interest_rate}%` : 'N/A'],
              ['Repayment Frequency', loan.repayment_frequency],
            ].map(([label, value]) => (
              <Col xs={24} md={12} key={label}>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Text type="secondary" style={{ minWidth: 160, fontSize: 12 }}>{label}:</Text>
                  <Text strong style={{ fontSize: 12 }}>{value || 'N/A'}</Text>
                </div>
              </Col>
            ))}
          </Row>
        </div>

        <Divider />

        {/* 4. Risk Assessment */}
        <div className="report-section">
          <div className="report-section-title">4. Risk Assessment</div>
          <List
            dataSource={rec.reasoning || []}
            renderItem={(item, i) => (
              <List.Item style={{ padding: '4px 0' }}>
                <Space align="start">
                  <Tag color="blue" style={{ minWidth: 24, textAlign: 'center' }}>{i + 1}</Tag>
                  <Text style={{ fontSize: 13 }}>{item}</Text>
                </Space>
              </List.Item>
            )}
          />
        </div>

        <Divider />

        {/* 5. SWOT Analysis */}
        <div className="report-section">
          <div className="report-section-title">5. SWOT Analysis</div>
          <div className="swot-grid" style={{ gap: 12 }}>
            {[
              { key: 'strengths', label: 'Strengths', color: '#52c41a', bg: '#f6ffed' },
              { key: 'weaknesses', label: 'Weaknesses', color: '#ff4d4f', bg: '#fff1f0' },
              { key: 'opportunities', label: 'Opportunities', color: '#1890ff', bg: '#e6f7ff' },
              { key: 'threats', label: 'Threats', color: '#fa8c16', bg: '#fff7e6' },
            ].map((q) => (
              <div
                key={q.key}
                style={{
                  background: q.bg,
                  border: `1px solid ${q.color}30`,
                  borderRadius: 8,
                  padding: 12,
                }}
              >
                <div style={{ fontWeight: 700, color: q.color, marginBottom: 8, fontSize: 13 }}>
                  {q.label}
                </div>
                {(swot[q.key] || []).map((item, i) => (
                  <div key={i} style={{ fontSize: 12, marginBottom: 4, display: 'flex', gap: 6 }}>
                    <span style={{ color: q.color }}>•</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <Divider />

        {/* Footer */}
        <div style={{ textAlign: 'center', color: '#bfbfbf', fontSize: 12, marginTop: 24 }}>
          <div>CreditLens AI-Powered Underwriting Platform</div>
          <div>This report is confidential and intended for internal use only.</div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;
