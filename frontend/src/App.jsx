import React, { useState, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import './App.css';

import Navbar from './components/common/Navbar';
import StepProgress from './components/common/StepProgress';
import OnboardingPage from './pages/OnboardingPage';
import IngestionPage from './pages/IngestionPage';
import ExtractionPage from './pages/ExtractionPage';
import AnalysisPage from './pages/AnalysisPage';

// Global app context
export const AppContext = createContext(null);

export const useApp = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
};

const antdTheme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 8,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
};

function AppContent() {
  const [entityId, setEntityId] = useState(null);
  const [entityName, setEntityName] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const goToStage = (stage) => {
    setCurrentStep(stage);
    const routes = ['/', '/ingestion', '/extraction', '/analysis'];
    navigate(routes[stage]);
  };

  const contextValue = {
    entityId,
    setEntityId,
    entityName,
    setEntityName,
    currentStep,
    setCurrentStep,
    goToStage,
  };

  return (
    <AppContext.Provider value={contextValue}>
      <div className="app-layout">
        <Navbar entityName={entityName} entityId={entityId} />
        <div className="step-progress-container">
          <StepProgress currentStep={currentStep} />
        </div>
        <div className="main-content">
          <Routes>
            <Route path="/" element={<OnboardingPage />} />
            <Route path="/ingestion" element={<IngestionPage />} />
            <Route path="/extraction" element={<ExtractionPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
          </Routes>
        </div>
      </div>
    </AppContext.Provider>
  );
}

function App() {
  return (
    <ConfigProvider theme={antdTheme}>
      <Router>
        <AppContent />
      </Router>
    </ConfigProvider>
  );
}

export default App;
