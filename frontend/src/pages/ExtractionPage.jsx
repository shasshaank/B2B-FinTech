import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography, Space, Button, Alert, Tabs, Badge,
} from 'antd';
import {
  ArrowRightOutlined, RobotOutlined, TableOutlined,
  EditOutlined, ReloadOutlined,
} from '@ant-design/icons';
import { useApp } from '../App';
import { getDocuments } from '../services/api';
import ClassificationReview from '../components/extraction/ClassificationReview';
import SchemaEditor from '../components/extraction/SchemaEditor';
import ExtractionResults from '../components/extraction/ExtractionResults';

const { Title, Text } = Typography;

const ExtractionPage = () => {
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
        description="Please complete Stage 1 and Stage 2 before proceeding."
        type="warning"
        showIcon
        action={<Button type="primary" onClick={() => goToStage(0)}>Go to Onboarding</Button>}
      />
    );
  }

  const confirmedCount = documents.filter((d) => d.classification_status === 'confirmed').length;
  const extractedCount = documents.filter((d) => d.extracted_data).length;

  const tabItems = [
    {
      key: 'classification',
      label: (
        <>
          <RobotOutlined /> AI Classification{' '}
          <Badge count={documents.filter(d => d.classification_status === 'uploaded').length} style={{ backgroundColor: '#faad14' }} />
        </>
      ),
      children: (
        <ClassificationReview
          documents={documents}
          onUpdate={fetchDocuments}
        />
      ),
    },
    {
      key: 'schema',
      label: <><EditOutlined /> Schema Editor</>,
      children: <SchemaEditor entityId={entityId} />,
    },
    {
      key: 'extraction',
      label: (
        <>
          <TableOutlined /> Extraction Results{' '}
          <Badge count={extractedCount} style={{ backgroundColor: '#52c41a' }} />
        </>
      ),
      children: (
        <ExtractionResults
          documents={documents}
          onUpdate={fetchDocuments}
        />
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>
            Stage 3: Automated Extraction & Schema Mapping
          </Title>
          <Text type="secondary">
            AI classifies documents, extracts structured data, and allows human review
          </Text>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={fetchDocuments} loading={loading}>
            Refresh
          </Button>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={() => goToStage(3)}
          >
            Proceed to Stage 4
          </Button>
        </Space>
      </div>

      <Tabs items={tabItems} defaultActiveKey="classification" type="card" />
    </div>
  );
};

export default ExtractionPage;
