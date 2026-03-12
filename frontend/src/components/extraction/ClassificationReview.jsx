import React, { useState } from 'react';
import { Table, Button, Select, Tag, Space, message, Tooltip, Badge, Progress, Alert } from 'antd';
import { CheckOutlined, EditOutlined, CloseOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { extractionAPI } from '../../services/api';

const { Option } = Select;

const CATEGORIES = [
  'ALM (Asset-Liability Management)',
  'Shareholding Pattern',
  'Borrowing Profile',
  'Annual Report - Profit & Loss',
  'Annual Report - Balance Sheet',
  'Annual Report - Cash Flow',
  'Portfolio Performance Data',
];

const ClassificationReview = ({ entityId, documents, onDocumentsChange }) => {
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editCategory, setEditCategory] = useState('');

  const classifyAll = async () => {
    setLoading(true);
    try {
      const result = await extractionAPI.classifyAll(entityId);
      message.success(`Classified ${result.results?.length || 0} documents`);
      // Refresh documents
      const { documentAPI } = await import('../../services/api');
      const updated = await documentAPI.getAll(entityId);
      onDocumentsChange(updated);
    } catch (error) {
      message.error(`Classification failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const confirmClassification = async (documentId, category, status) => {
    try {
      await extractionAPI.confirmClassification(documentId, { category, status });
      const updated = documents.map(d =>
        d.id === documentId ? { ...d, document_category: category, classification_status: status } : d
      );
      onDocumentsChange(updated);
      message.success(`Document ${status}`);
      setEditingId(null);
    } catch (error) {
      message.error(`Failed: ${error.message}`);
    }
  };

  const batchApproveHighConfidence = async () => {
    const highConfidenceDocs = documents.filter(
      d => d.classification_confidence > 0.8 && d.classification_status === 'classified'
    );
    
    let approved = 0;
    for (const doc of highConfidenceDocs) {
      try {
        await extractionAPI.confirmClassification(doc.id, { category: doc.document_category, status: 'confirmed' });
        approved++;
      } catch (e) { /* continue */ }
    }
    
    if (approved > 0) {
      const updated = documents.map(d =>
        d.classification_confidence > 0.8 && d.classification_status === 'classified'
          ? { ...d, classification_status: 'confirmed' }
          : d
      );
      onDocumentsChange(updated);
      message.success(`Batch approved ${approved} high-confidence documents`);
    }
  };

  const columns = [
    {
      title: 'Document',
      dataIndex: 'original_filename',
      key: 'filename',
      render: (name, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name || record.filename}</div>
          <div style={{ fontSize: 12, color: '#6b7280' }}>{record.file_type?.toUpperCase()} • {record.file_size ? `${(record.file_size / 1024).toFixed(1)} KB` : 'N/A'}</div>
        </div>
      ),
    },
    {
      title: 'AI Category',
      dataIndex: 'document_category',
      key: 'category',
      render: (category, record) => {
        if (editingId === record.id) {
          return (
            <Select
              value={editCategory}
              onChange={setEditCategory}
              style={{ width: 220 }}
              size="small"
            >
              {CATEGORIES.map(c => <Option key={c} value={c}>{c}</Option>)}
            </Select>
          );
        }
        return category ? (
          <Tag color="blue" style={{ maxWidth: 220, whiteSpace: 'normal', height: 'auto' }}>{category}</Tag>
        ) : (
          <Tag color="default">Not classified</Tag>
        );
      },
    },
    {
      title: 'Confidence',
      dataIndex: 'classification_confidence',
      key: 'confidence',
      width: 140,
      render: (conf) => {
        if (!conf) return <Tag>N/A</Tag>;
        const pct = (conf * 100).toFixed(0);
        return (
          <div>
            <Progress
              percent={parseInt(pct)}
              size="small"
              status={conf > 0.8 ? 'success' : conf > 0.5 ? 'normal' : 'exception'}
              format={() => `${pct}%`}
            />
          </div>
        );
      },
    },
    {
      title: 'Status',
      dataIndex: 'classification_status',
      key: 'status',
      width: 120,
      render: (status) => {
        const colorMap = { confirmed: 'success', classified: 'processing', rejected: 'error', uploaded: 'default' };
        return <Badge status={colorMap[status] || 'default'} text={status} />;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 160,
      render: (_, record) => {
        if (record.classification_status === 'confirmed' || record.classification_status === 'rejected') {
          return <Tag color={record.classification_status === 'confirmed' ? 'success' : 'error'}>{record.classification_status}</Tag>;
        }
        
        if (editingId === record.id) {
          return (
            <Space>
              <Button
                size="small"
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => confirmClassification(record.id, editCategory, 'confirmed')}
              >Save</Button>
              <Button size="small" onClick={() => setEditingId(null)}>Cancel</Button>
            </Space>
          );
        }
        
        return (
          <Space>
            <Tooltip title="Approve classification">
              <Button
                size="small"
                type="primary"
                icon={<CheckOutlined />}
                style={{ background: '#16a34a', borderColor: '#16a34a' }}
                onClick={() => confirmClassification(record.id, record.document_category, 'confirmed')}
                disabled={!record.document_category}
              />
            </Tooltip>
            <Tooltip title="Edit classification">
              <Button
                size="small"
                icon={<EditOutlined />}
                onClick={() => { setEditingId(record.id); setEditCategory(record.document_category || ''); }}
              />
            </Tooltip>
            <Tooltip title="Reject document">
              <Button
                size="small"
                danger
                icon={<CloseOutlined />}
                onClick={() => confirmClassification(record.id, record.document_category, 'rejected')}
              />
            </Tooltip>
          </Space>
        );
      },
    },
  ];

  const classifiedCount = documents.filter(d => d.classification_status !== 'uploaded').length;
  const highConfidenceCount = documents.filter(d => d.classification_confidence > 0.8 && d.classification_status === 'classified').length;

  return (
    <div>
      {documents.length === 0 ? (
        <Alert
          type="warning"
          message="No documents uploaded yet"
          description="Please upload documents in the previous stage first."
          showIcon
        />
      ) : (
        <>
          {classifiedCount < documents.length && (
            <Alert
              type="info"
              message={`${documents.length - classifiedCount} document(s) not yet classified`}
              description="Click 'Classify All with AI' to automatically classify all documents."
              showIcon
              style={{ marginBottom: 16 }}
              action={
                <Button type="primary" icon={<ThunderboltOutlined />} onClick={classifyAll} loading={loading} size="small">
                  Classify All with AI
                </Button>
              }
            />
          )}
          
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginBottom: 16 }}>
            <Button icon={<ThunderboltOutlined />} onClick={classifyAll} loading={loading}>
              Re-Classify All with AI
            </Button>
            {highConfidenceCount > 0 && (
              <Button type="primary" style={{ background: '#16a34a', borderColor: '#16a34a' }} onClick={batchApproveHighConfidence}>
                Batch Approve ({highConfidenceCount} high-confidence)
              </Button>
            )}
          </div>
          
          <Table
            dataSource={documents}
            columns={columns}
            rowKey="id"
            pagination={false}
            size="middle"
          />
        </>
      )}
    </div>
  );
};

export default ClassificationReview;
