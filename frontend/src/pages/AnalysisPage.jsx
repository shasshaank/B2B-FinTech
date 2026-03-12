import React, { useState } from 'react';
import { Tabs } from 'antd';
import { SearchOutlined, SafetyOutlined, BulbOutlined, FileTextOutlined } from '@ant-design/icons';
import SecondaryResearch from '../components/analysis/SecondaryResearch';
import RiskAssessment from '../components/analysis/RiskAssessment';
import SwotAnalysis from '../components/analysis/SwotAnalysis';
import ReportGenerator from '../components/analysis/ReportGenerator';

const AnalysisPage = ({ entityId }) => {
  const [activeTab, setActiveTab] = useState('research');

  const tabItems = [
    {
      key: 'research',
      label: <span><SearchOutlined /> Secondary Research</span>,
      children: (
        <SecondaryResearch
          entityId={entityId}
          onResearchComplete={() => {}}
        />
      ),
    },
    {
      key: 'risk',
      label: <span><SafetyOutlined /> Risk Assessment</span>,
      children: (
        <RiskAssessment
          entityId={entityId}
          onRecommendationComplete={() => {}}
        />
      ),
    },
    {
      key: 'swot',
      label: <span><BulbOutlined /> SWOT Analysis</span>,
      children: <SwotAnalysis entityId={entityId} />,
    },
    {
      key: 'report',
      label: <span><FileTextOutlined /> Final Report</span>,
      children: <ReportGenerator entityId={entityId} />,
    },
  ];

  return (
    <div>
      <div className="stage-header">
        <h1>Stage 4: Pre-Cognitive Analysis & Reporting</h1>
        <p>AI-powered secondary research, risk assessment, SWOT analysis, and final report generation</p>
      </div>

      <div className="creditlens-card">
        <div className="card-header">
          <span className="card-title">🧠 AI Analysis Engine</span>
        </div>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          type="line"
        />
      </div>
    </div>
  );
};

export default AnalysisPage;
