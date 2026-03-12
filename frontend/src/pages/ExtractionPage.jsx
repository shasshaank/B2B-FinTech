import React, { useState, useEffect } from 'react';
import { Tabs, Button, message } from 'antd';
import { ArrowRightOutlined, AuditOutlined, TableOutlined, SettingOutlined } from '@ant-design/icons';
import ClassificationReview from '../components/extraction/ClassificationReview';
import SchemaEditor from '../components/extraction/SchemaEditor';
import ExtractionResults from '../components/extraction/ExtractionResults';
import { documentAPI } from '../services/api';

const ExtractionPage = ({ entityId, onComplete }) => {
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('classify');

  useEffect(() => {
    if (entityId) loadDocuments();
  }, [entityId]);

  const loadDocuments = async () => {
    try {
      const docs = await documentAPI.getAll(entityId);
      setDocuments(docs);
    } catch (error) {
      message.error('Failed to load documents');
    }
  };

  const handleProceed = () => {
    const extractedCount = documents.filter(d => d.extracted_data).length;
    if (extractedCount === 0) {
      message.warning('Please extract data from at least one document before proceeding');
      return;
    }
    if (onComplete) onComplete();
  };

  const tabItems = [
    {
      key: 'classify',
      label: <span><AuditOutlined /> Classification Review</span>,
      children: (
        <ClassificationReview
          entityId={entityId}
          documents={documents}
          onDocumentsChange={setDocuments}
        />
      ),
    },
    {
      key: 'schema',
      label: <span><SettingOutlined /> Schema Editor</span>,
      children: <SchemaEditor entityId={entityId} />,
    },
    {
      key: 'extraction',
      label: <span><TableOutlined /> Extraction Results</span>,
      children: (
        <ExtractionResults
          entityId={entityId}
          documents={documents}
          onDocumentsChange={setDocuments}
        />
      ),
    },
  ];

  return (
    <div>
      <div className="stage-header">
        <h1>Stage 3: Automated Extraction & Schema Mapping</h1>
        <p>AI classifies documents, extracts structured data, and enables human-in-the-loop corrections</p>
      </div>

      <div className="creditlens-card">
        <div className="card-header">
          <span className="card-title">🤖 AI Extraction Pipeline</span>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={handleProceed}
          >
            Proceed to Analysis
          </Button>
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

export default ExtractionPage;
