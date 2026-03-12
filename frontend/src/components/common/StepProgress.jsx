import React from 'react';
import { Steps } from 'antd';
import {
  UserAddOutlined,
  FileAddOutlined,
  FunctionOutlined,
  BarChartOutlined,
} from '@ant-design/icons';

const STEPS = [
  {
    title: 'Entity Onboarding',
    description: 'Company & Loan Details',
    icon: <UserAddOutlined />,
  },
  {
    title: 'Data Ingestion',
    description: 'Upload Documents',
    icon: <FileAddOutlined />,
  },
  {
    title: 'Extraction & Mapping',
    description: 'AI Classification & Schema',
    icon: <FunctionOutlined />,
  },
  {
    title: 'Analysis & Report',
    description: 'Insights & Recommendation',
    icon: <BarChartOutlined />,
  },
];

const StepProgress = ({ currentStep }) => {
  return (
    <Steps
      current={currentStep}
      items={STEPS}
      style={{ maxWidth: 900, margin: '0 auto' }}
      responsive={false}
    />
  );
};

export default StepProgress;
