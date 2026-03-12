import React, { useState, useEffect } from 'react';
import { Button, message } from 'antd';
import { ArrowRightOutlined } from '@ant-design/icons';
import DocumentUpload from '../components/ingestion/DocumentUpload';
import { documentAPI } from '../services/api';

const IngestionPage = ({ entityId, onComplete }) => {
  const [documents, setDocuments] = useState([]);

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
    if (documents.length === 0) {
      message.warning('Please upload at least one document before proceeding');
      return;
    }
    if (onComplete) onComplete(documents);
  };

  return (
    <div>
      <div className="stage-header">
        <h1>Stage 2: Intelligent Data Ingestion</h1>
        <p>Upload financial documents — AI will automatically classify and prepare them for extraction</p>
      </div>

      <div className="creditlens-card">
        <div className="card-header">
          <span className="card-title">📂 Document Upload</span>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={handleProceed}
            disabled={documents.length === 0}
          >
            Proceed to Extraction ({documents.length} docs)
          </Button>
        </div>
        <DocumentUpload
          entityId={entityId}
          documents={documents}
          onDocumentsChange={setDocuments}
        />
      </div>
    </div>
  );
};

export default IngestionPage;
