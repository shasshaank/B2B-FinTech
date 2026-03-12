import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography, Space, Button, Alert, Tabs, Badge,
} from 'antd';
import {
  ArrowRightOutlined, UploadOutlined, ReloadOutlined,
} from '@ant-design/icons';
import { useApp } from '../App';
import { getDocuments } from '../services/api';
import DocumentUpload from '../components/ingestion/DocumentUpload';
import DocumentPreview from '../components/ingestion/DocumentPreview';

const { Title, Text } = Typography;

const IngestionPage = () => {
  const { entityId, goToStage } = useApp();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchDocuments = useCallback(async () => {
    if (!entityId) return;
    setLoading(true);
    try {
      const docs = await getDocuments(entityId);
      setDocuments(docs);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  }, [entityId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  if (!entityId) {
    return (
      <Alert
        message="No Entity Selected"
        description="Please complete Stage 1 (Entity Onboarding) before uploading documents."
        type="warning"
        showIcon
        action={
          <Button type="primary" onClick={() => goToStage(0)}>
            Go to Onboarding
          </Button>
        }
      />
    );
  }

  const tabItems = [
    {
      key: 'upload',
      label: <><UploadOutlined /> Upload Documents</>,
      children: (
        <DocumentUpload
          entityId={entityId}
          onUploadComplete={fetchDocuments}
        />
      ),
    },
    {
      key: 'documents',
      label: (
        <>
          <ReloadOutlined /> Document List{' '}
          <Badge count={documents.length} style={{ backgroundColor: '#1890ff' }} />
        </>
      ),
      children: (
        <DocumentPreview
          documents={documents}
          onDelete={fetchDocuments}
          onRefresh={fetchDocuments}
        />
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>
            Stage 2: Intelligent Data Ingestion
          </Title>
          <Text type="secondary">
            Upload financial documents — AI will classify them automatically
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchDocuments} loading={loading}>
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => goToStage(2)}
            disabled={documents.length === 0}
          >
            Proceed to Stage 3
          </Button>
        </Space>
      </div>

      <Tabs items={tabItems} defaultActiveKey="upload" type="card" />
    </div>
  );
};

export default IngestionPage;
