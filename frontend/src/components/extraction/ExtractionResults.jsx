import React, { useState, useEffect } from 'react';
import { Table, Button, message, Tabs, Tag, Space, Alert, Spin, Typography } from 'antd';
import { ThunderboltOutlined, SaveOutlined, SyncOutlined } from '@ant-design/icons';
import { extractionAPI } from '../../services/api';

const { Text } = Typography;

const ExtractionResults = ({ entityId, documents, onDocumentsChange }) => {
  const [extractedData, setExtractedData] = useState({});
  const [loading, setLoading] = useState(false);
  const [extractingAll, setExtractingAll] = useState(false);

  const classifiedDocs = documents.filter(d =>
    ['classified', 'confirmed'].includes(d.classification_status)
  );

  useEffect(() => {
    loadExistingExtractions();
  }, [documents]);

  const loadExistingExtractions = async () => {
    const data = {};
    for (const doc of classifiedDocs) {
      if (doc.extracted_data) {
        try {
          data[doc.id] = JSON.parse(doc.extracted_data);
        } catch (e) {
          data[doc.id] = [];
        }
      }
    }
    setExtractedData(data);
  };

  const extractAll = async () => {
    setExtractingAll(true);
    try {
      const result = await extractionAPI.extractAll(entityId);
      message.success(`Extraction complete: ${result.results?.length || 0} documents processed`);
      
      // Reload documents
      const { documentAPI } = await import('../../services/api');
      const updated = await documentAPI.getAll(entityId);
      onDocumentsChange(updated);
      
      // Load extracted data
      const data = {};
      for (const doc of updated) {
        if (doc.extracted_data) {
          try { data[doc.id] = JSON.parse(doc.extracted_data); } catch (e) {}
        }
      }
      setExtractedData(data);
    } catch (error) {
      message.error(`Extraction failed: ${error.message}`);
    } finally {
      setExtractingAll(false);
    }
  };

  const extractSingle = async (documentId) => {
    try {
      const result = await extractionAPI.extract(documentId);
      setExtractedData(prev => ({ ...prev, [documentId]: result.extracted_data }));
      message.success(`Extracted ${result.extracted_data?.length || 0} records`);
    } catch (error) {
      message.error(`Extraction failed: ${error.message}`);
    }
  };

  const saveEdits = async (documentId, data) => {
    try {
      await extractionAPI.updateExtraction(documentId, data);
      message.success('Changes saved');
    } catch (error) {
      message.error(`Save failed: ${error.message}`);
    }
  };

  const getColumnsForData = (data) => {
    if (!data || data.length === 0) return [];
    const keys = Object.keys(data[0]);
    return keys.map(key => ({
      title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      dataIndex: key,
      key,
      render: (val) => {
        if (val === null || val === undefined) return <Text type="secondary">—</Text>;
        if (typeof val === 'number') return <Text strong>{val.toLocaleString()}</Text>;
        return String(val);
      },
    }));
  };

  const tabItems = classifiedDocs.map(doc => ({
    key: String(doc.id),
    label: (
      <Space>
        <span>{(doc.original_filename || doc.filename)?.split('_').slice(2).join('_') || doc.original_filename || doc.filename}</span>
        {extractedData[doc.id] ? <Tag color="success">Extracted</Tag> : <Tag color="default">Pending</Tag>}
      </Space>
    ),
    children: (
      <div>
        <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Tag color="blue">{doc.document_category}</Tag>
            <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>{doc.original_filename}</Text>
          </div>
          <Space>
            <Button
              icon={<SyncOutlined />}
              onClick={() => extractSingle(doc.id)}
              size="small"
            >
              Re-Extract
            </Button>
            {extractedData[doc.id] && (
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={() => saveEdits(doc.id, extractedData[doc.id])}
                size="small"
              >
                Save Edits
              </Button>
            )}
          </Space>
        </div>
        
        {extractedData[doc.id] ? (
          <Table
            dataSource={extractedData[doc.id]}
            columns={getColumnsForData(extractedData[doc.id])}
            rowKey={(_, i) => i}
            size="small"
            scroll={{ x: true }}
            pagination={{ pageSize: 20 }}
          />
        ) : (
          <Alert
            type="info"
            message="No extracted data yet"
            description="Click 'Re-Extract' or use 'Extract All' to extract data from this document."
            showIcon
          />
        )}
      </div>
    ),
  }));

  if (classifiedDocs.length === 0) {
    return (
      <Alert
        type="warning"
        message="No classified documents"
        description="Please classify your documents in the Classification Review tab first."
        showIcon
      />
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          onClick={extractAll}
          loading={extractingAll}
          size="large"
        >
          Extract All Documents
        </Button>
      </div>
      
      <Tabs items={tabItems} type="card" />
    </div>
  );
};

export default ExtractionResults;
