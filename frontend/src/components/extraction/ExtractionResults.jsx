import React, { useState } from 'react';
import {
  Card, Button, Table, Tag, Typography, Space,
  message, Empty, Collapse,
} from 'antd';
import { ThunderboltOutlined, SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { extractDocument, updateExtraction } from '../../services/api';

const { Text } = Typography;
const { Panel } = Collapse;

const ExtractionResults = ({ documents, onUpdate }) => {
  const [extracting, setExtracting] = useState({});
  const [editedData, setEditedData] = useState({});

  const handleExtract = async (docId) => {
    setExtracting((prev) => ({ ...prev, [docId]: true }));
    try {
      const result = await extractDocument(docId);
      message.success(`Extracted ${result.extracted_data?.length || 0} records from document`);
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Extraction failed: ${err.message}`);
    } finally {
      setExtracting((prev) => ({ ...prev, [docId]: false }));
    }
  };

  const handleExtractAll = async () => {
    const confirmed = documents.filter(
      (d) => d.classification_status === 'confirmed' && !d.extracted_data
    );
    if (confirmed.length === 0) {
      message.info('No confirmed documents awaiting extraction');
      return;
    }
    for (const doc of confirmed) {
      await handleExtract(doc.id);
    }
    message.success('Extraction complete for all confirmed documents');
  };

  const handleCellEdit = (docId, rowIndex, field, value) => {
    setEditedData((prev) => {
      const docData = [...(prev[docId] || [])];
      if (!docData[rowIndex]) docData[rowIndex] = {};
      docData[rowIndex] = { ...docData[rowIndex], [field]: value };
      return { ...prev, [docId]: docData };
    });
  };

  const handleSaveEdits = async (doc) => {
    const data = editedData[doc.id];
    if (!data) return;

    try {
      // Merge edits with original data
      const original = doc.extracted_data ? JSON.parse(doc.extracted_data) : [];
      const merged = original.map((row, i) => ({ ...row, ...(data[i] || {}) }));

      await updateExtraction(doc.id, merged);
      message.success('Extraction data updated successfully');
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Save failed: ${err.message}`);
    }
  };

  const renderExtractedTable = (doc) => {
    let data = [];
    try {
      data = doc.extracted_data ? JSON.parse(doc.extracted_data) : [];
    } catch (e) {
      data = [];
    }

    if (!Array.isArray(data) || data.length === 0) return <Empty description="No data extracted yet" />;

    const keys = Object.keys(data[0] || {}).filter((k) => !k.startsWith('_'));
    const columns = keys.map((key) => ({
      title: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      dataIndex: key,
      key,
      render: (val, _, rowIndex) => (
        <input
          defaultValue={val}
          onChange={(e) => handleCellEdit(doc.id, rowIndex, key, e.target.value)}
          style={{
            border: 'none',
            borderBottom: '1px solid transparent',
            padding: '2px 4px',
            fontSize: 12,
            width: '100%',
            background: 'transparent',
          }}
          onFocus={(e) => {
            e.target.style.borderBottomColor = '#1890ff';
          }}
          onBlur={(e) => {
            e.target.style.borderBottomColor = 'transparent';
          }}
        />
      ),
    }));

    return (
      <div>
        <Table
          dataSource={data.map((row, i) => ({ ...row, key: i }))}
          columns={columns}
          pagination={{ pageSize: 10, hideOnSinglePage: true }}
          size="small"
          scroll={{ x: 'max-content' }}
          bordered
        />
        {editedData[doc.id] && (
          <div style={{ marginTop: 8, textAlign: 'right' }}>
            <Button
              type="primary"
              size="small"
              icon={<SaveOutlined />}
              onClick={() => handleSaveEdits(doc)}
            >
              Save Edits
            </Button>
          </div>
        )}
      </div>
    );
  };

  const confirmedDocs = documents.filter((d) => d.classification_status === 'confirmed');
  const pendingExtraction = confirmedDocs.filter((d) => !d.extracted_data);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Text strong>{confirmedDocs.length} confirmed documents</Text>
          <Text type="secondary"> — {pendingExtraction.length} pending extraction</Text>
        </div>
        <Button
          type="primary"
          icon={<ThunderboltOutlined />}
          onClick={handleExtractAll}
          disabled={pendingExtraction.length === 0}
        >
          Extract All ({pendingExtraction.length})
        </Button>
      </div>

      {confirmedDocs.length === 0 ? (
        <Empty
          description="No confirmed documents. Please classify and approve documents first."
          style={{ padding: 40 }}
        />
      ) : (
        <Collapse defaultActiveKey={confirmedDocs.slice(0, 2).map((d) => String(d.id))}>
          {confirmedDocs.map((doc) => (
            <Panel
              key={String(doc.id)}
              header={
                <Space>
                  <Text strong>{doc.original_filename}</Text>
                  <Tag color="blue" style={{ borderRadius: 4 }}>{doc.document_category}</Tag>
                  {doc.extracted_data ? (
                    <Tag color="success">Extracted</Tag>
                  ) : (
                    <Tag color="default">Not extracted</Tag>
                  )}
                </Space>
              }
              extra={
                <Space onClick={(e) => e.stopPropagation()}>
                  <Button
                    size="small"
                    icon={doc.extracted_data ? <ReloadOutlined /> : <ThunderboltOutlined />}
                    type={doc.extracted_data ? 'default' : 'primary'}
                    loading={extracting[doc.id]}
                    onClick={() => handleExtract(doc.id)}
                  >
                    {doc.extracted_data ? 'Re-extract' : 'Extract'}
                  </Button>
                </Space>
              }
            >
              {renderExtractedTable(doc)}
            </Panel>
          ))}
        </Collapse>
      )}
    </div>
  );
};

export default ExtractionResults;
