import React, { useState } from 'react';
import { ConfigProvider, Layout } from 'antd';
import Navbar from './components/common/Navbar';
import StepProgress from './components/common/StepProgress';
import OnboardingPage from './pages/OnboardingPage';
import IngestionPage from './pages/IngestionPage';
import ExtractionPage from './pages/ExtractionPage';
import AnalysisPage from './pages/AnalysisPage';
import './App.css';

const { Content } = Layout;

const App = () => {
  const [currentStage, setCurrentStage] = useState(0);
  const [entityId, setEntityId] = useState(null);
  const [entityName, setEntityName] = useState(null);

  const handleIngestionComplete = () => {
    setCurrentStage(2);
  };

  const handleExtractionComplete = () => {
    setCurrentStage(3);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1d3a8a',
          borderRadius: 8,
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        },
      }}
    >
      <Layout className="app-layout">
        <Navbar entityName={entityName} entityId={entityId} />
        <StepProgress currentStage={currentStage} />
        <Content className="main-content">
          {currentStage === 0 && (
            <OnboardingPage
              onComplete={(id) => {
                setEntityId(id);
                setCurrentStage(1);
              }}
            />
          )}
          {currentStage === 1 && (
            <IngestionPage
              entityId={entityId}
              onComplete={handleIngestionComplete}
            />
          )}
          {currentStage === 2 && (
            <ExtractionPage
              entityId={entityId}
              onComplete={handleExtractionComplete}
            />
          )}
          {currentStage === 3 && (
            <AnalysisPage entityId={entityId} />
          )}
        </Content>
      </Layout>
    </ConfigProvider>
  );
};

export default App;
