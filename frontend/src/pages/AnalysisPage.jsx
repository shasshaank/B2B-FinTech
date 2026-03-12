import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography, Space, Button, Alert, Tabs,
} from 'antd';
import {
  GlobalOutlined, ThunderboltOutlined, BarChartOutlined,
  FilePdfOutlined, ReloadOutlined,
} from '@ant-design/icons';
import { useApp } from '../App';
import {
  getSecondaryResearch, getRecommendation, getSwot, getReport,
} from '../services/api';
import SecondaryResearch from '../components/analysis/SecondaryResearch';
import RiskAssessment from '../components/analysis/RiskAssessment';
import SwotAnalysis from '../components/analysis/SwotAnalysis';
import ReportGenerator from '../components/analysis/ReportGenerator';

const { Title, Text } = Typography;

const AnalysisPage = () => {
  const { entityId } = useApp();
  const [research, setResearch] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [swot, setSwot] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    if (!entityId) return;
    setLoading(true);
    try {
      const [r, rec, s, rep] = await Promise.allSettled([
        getSecondaryResearch(entityId),
        getRecommendation(entityId),
        getSwot(entityId),
        getReport(entityId),
      ]);
      if (r.status === 'fulfilled') setResearch(r.value);
      if (rec.status === 'fulfilled') setRecommendation(rec.value);
      if (s.status === 'fulfilled') setSwot(s.value);
      if (rep.status === 'fulfilled') setReport(rep.value?.report_data);
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [entityId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (!entityId) {
    return (
      <Alert
        message="No Entity Selected"
        description="Please complete the previous stages before running analysis."
        type="warning"
        showIcon
      />
    );
  }

  const tabItems = [
    {
      key: 'research',
      label: <><GlobalOutlined /> Secondary Research</>,
      children: (
        <SecondaryResearch
          entityId={entityId}
          research={research}
          onUpdate={async () => {
            try {
              const r = await getSecondaryResearch(entityId);
              setResearch(r);
            } catch (e) {}
          }}
        />
      ),
    },
    {
      key: 'risk',
      label: <><ThunderboltOutlined /> Risk Assessment</>,
      children: (
        <RiskAssessment
          entityId={entityId}
          recommendation={recommendation}
          onUpdate={async () => {
            try {
              const r = await getRecommendation(entityId);
              setRecommendation(r);
            } catch (e) {}
          }}
        />
      ),
    },
    {
      key: 'swot',
      label: <><BarChartOutlined /> SWOT Analysis</>,
      children: (
        <SwotAnalysis
          entityId={entityId}
          swot={swot}
          onUpdate={async () => {
            try {
              const s = await getSwot(entityId);
              setSwot(s);
            } catch (e) {}
          }}
        />
      ),
    },
    {
      key: 'report',
      label: <><FilePdfOutlined /> Final Report</>,
      children: (
        <ReportGenerator
          entityId={entityId}
          reportData={report}
          onUpdate={async () => {
            try {
              const r = await getReport(entityId);
              setReport(r?.report_data);
            } catch (e) {}
          }}
        />
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>
            Stage 4: Pre-Cognitive Secondary Analysis & Reporting
          </Title>
          <Text type="secondary">
            AI-powered secondary research, risk assessment, SWOT analysis, and final report generation
          </Text>
        </div>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>
          Refresh All
        </Button>
      </div>

      <Tabs items={tabItems} defaultActiveKey="research" type="card" />
    </div>
  );
};

export default AnalysisPage;
