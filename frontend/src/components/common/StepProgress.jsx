import React from 'react';
import { Steps } from 'antd';
import { 
  FormOutlined, 
  UploadOutlined, 
  FileSearchOutlined, 
  BarChartOutlined 
} from '@ant-design/icons';

const STAGES = [
  { title: 'Entity Onboarding', description: 'Company & loan details', icon: <FormOutlined /> },
  { title: 'Document Ingestion', description: 'Upload financial documents', icon: <UploadOutlined /> },
  { title: 'Data Extraction', description: 'AI-powered classification & extraction', icon: <FileSearchOutlined /> },
  { title: 'Analysis & Report', description: 'Risk assessment & reporting', icon: <BarChartOutlined /> },
];

const StepProgress = ({ currentStage }) => {
  return (
    <div className="step-progress-container">
      <Steps
        current={currentStage}
        items={STAGES.map((stage, i) => ({
          title: stage.title,
          description: stage.description,
          icon: stage.icon,
          status: i < currentStage ? 'finish' : i === currentStage ? 'process' : 'wait',
        }))}
        size="small"
      />
    </div>
  );
};

export default StepProgress;
