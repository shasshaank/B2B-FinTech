import React, { useState } from 'react';
import {
  Card, Button, Tag, Typography, Space, Alert, Tooltip,
  Select, Progress, Row, Col, message, Spin,
} from 'antd';
import {
  CheckOutlined, CloseOutlined, EditOutlined,
  RobotOutlined, ThunderboltOutlined,
} from '@ant-design/icons';
import { classifyDocument, confirmClassification } from '../../services/api';

const { Text, Title } = Typography;
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

const getConfidenceColor = (confidence) => {
  if (!confidence) return '#d9d9d9';
  if (confidence >= 0.8) return '#52c41a';
  if (confidence >= 0.5) return '#faad14';
  return '#ff4d4f';
};

const getConfidenceClass = (confidence) => {
  if (!confidence) return '';
  if (confidence >= 0.8) return 'confidence-high';
  if (confidence >= 0.5) return 'confidence-medium';
  return 'confidence-low';
};

const ClassificationReview = ({ documents, onUpdate }) => {
  const [classifying, setClassifying] = useState({});
  const [editing, setEditing] = useState({});
  const [editValues, setEditValues] = useState({});

  const handleClassify = async (docId) => {
    setClassifying((prev) => ({ ...prev, [docId]: true }));
    try {
      const result = await classifyDocument(docId);
      message.success(`Classified as: ${result.category}`);
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Classification failed: ${err.message}`);
    } finally {
      setClassifying((prev) => ({ ...prev, [docId]: false }));
    }
  };

  const handleClassifyAll = async () => {
    const unclassified = documents.filter(
      (d) => d.classification_status === 'uploaded'
    );
    if (unclassified.length === 0) {
      message.info('All documents are already classified');
      return;
    }

    for (const doc of unclassified) {
      await handleClassify(doc.id);
    }
    message.success('Batch classification complete');
  };

  const handleApprove = async (docId, category) => {
    try {
      await confirmClassification(docId, { category, status: 'confirmed' });
      message.success('Classification approved');
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Failed to approve: ${err.message}`);
    }
  };

  const handleReject = async (docId) => {
    try {
      await confirmClassification(docId, {
        category: documents.find((d) => d.id === docId)?.document_category || 'Unknown',
        status: 'rejected',
      });
      message.warning('Document marked as rejected');
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Failed to reject: ${err.message}`);
    }
  };

  const handleEditSave = async (docId) => {
    const newCategory = editValues[docId];
    if (!newCategory) return;

    try {
      await confirmClassification(docId, { category: newCategory, status: 'confirmed' });
      message.success('Category updated and approved');
      setEditing((prev) => ({ ...prev, [docId]: false }));
      if (onUpdate) onUpdate();
    } catch (err) {
      message.error(`Failed to update: ${err.message}`);
    }
  };

  const classifiedDocs = documents.filter((d) => d.classification_status !== 'uploaded');
  const unclassifiedDocs = documents.filter((d) => d.classification_status === 'uploaded');

  return (
    <div>
      {/* Header actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Text strong>{documents.length} documents</Text>
          <Text type="secondary"> — {classifiedDocs.length} classified, {unclassifiedDocs.length} pending</Text>
        </div>
        <Space>
          <Button
            type="primary"
            icon={<RobotOutlined />}
            onClick={handleClassifyAll}
            disabled={unclassifiedDocs.length === 0}
          >
            AI Classify All ({unclassifiedDocs.length})
          </Button>
          <Button
            icon={<CheckOutlined />}
            onClick={async () => {
              const highConf = documents.filter(
                (d) => d.classification_confidence >= 0.8 && d.classification_status === 'classified'
              );
              for (const doc of highConf) {
                await handleApprove(doc.id, doc.document_category);
              }
              if (highConf.length > 0) {
                message.success(`Batch approved ${highConf.length} high-confidence classifications`);
              }
            }}
          >
            Batch Approve High Confidence
          </Button>
        </Space>
      </div>

      {/* Document Cards */}
      <Row gutter={[12, 12]}>
        {documents.map((doc) => (
          <Col xs={24} md={12} lg={8} key={doc.id}>
            <Card
              size="small"
              style={{ borderRadius: 10, border: '1px solid #f0f0f0' }}
              bodyStyle={{ padding: 16 }}
            >
              {/* File name */}
              <div style={{ marginBottom: 8 }}>
                <Text strong style={{ fontSize: 13 }} ellipsis={{ tooltip: doc.original_filename }}>
                  {doc.original_filename}
                </Text>
                <div>
                  <Tag style={{ fontSize: 11, marginTop: 4 }}>{doc.file_type?.toUpperCase()}</Tag>
                </div>
              </div>

              {/* Classification result */}
              {doc.classification_status !== 'uploaded' && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <RobotOutlined style={{ color: '#1890ff', fontSize: 12 }} />
                    <Text type="secondary" style={{ fontSize: 11 }}>AI Classification:</Text>
                  </div>

                  {editing[doc.id] ? (
                    <Space.Compact style={{ width: '100%' }}>
                      <Select
                        size="small"
                        style={{ flex: 1 }}
                        defaultValue={doc.document_category}
                        onChange={(val) => setEditValues((prev) => ({ ...prev, [doc.id]: val }))}
                      >
                        {CATEGORIES.map((c) => (
                          <Option key={c} value={c}>{c}</Option>
                        ))}
                      </Select>
                      <Button size="small" type="primary" onClick={() => handleEditSave(doc.id)}>
                        Save
                      </Button>
                    </Space.Compact>
                  ) : (
                    <Tag
                      color="blue"
                      style={{ borderRadius: 4, fontSize: 12, maxWidth: '100%', whiteSpace: 'normal' }}
                    >
                      {doc.document_category}
                    </Tag>
                  )}

                  {/* Confidence bar */}
                  {doc.classification_confidence && (
                    <div style={{ marginTop: 6 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                        <Text type="secondary" style={{ fontSize: 11 }}>Confidence</Text>
                        <span className={getConfidenceClass(doc.classification_confidence)} style={{ fontSize: 11, fontWeight: 600 }}>
                          {(doc.classification_confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <Progress
                        percent={(doc.classification_confidence * 100).toFixed(0)}
                        size={['100%', 4]}
                        strokeColor={getConfidenceColor(doc.classification_confidence)}
                        showInfo={false}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Status badge */}
              <div style={{ marginBottom: 10 }}>
                <Tag
                  color={
                    doc.classification_status === 'confirmed' ? 'success' :
                    doc.classification_status === 'rejected' ? 'error' :
                    doc.classification_status === 'classified' ? 'processing' : 'default'
                  }
                  style={{ borderRadius: 4, textTransform: 'capitalize' }}
                >
                  {doc.classification_status}
                </Tag>
              </div>

              {/* Actions */}
              <Space wrap size="small">
                {doc.classification_status === 'uploaded' && (
                  <Button
                    size="small"
                    icon={<RobotOutlined />}
                    loading={classifying[doc.id]}
                    onClick={() => handleClassify(doc.id)}
                    type="primary"
                    ghost
                  >
                    Classify
                  </Button>
                )}
                {doc.classification_status === 'classified' && (
                  <>
                    <Tooltip title="Approve this classification">
                      <Button
                        size="small"
                        type="primary"
                        icon={<CheckOutlined />}
                        onClick={() => handleApprove(doc.id, doc.document_category)}
                        style={{ background: '#52c41a', borderColor: '#52c41a' }}
                      >
                        Approve
                      </Button>
                    </Tooltip>
                    <Tooltip title="Edit classification">
                      <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => setEditing((prev) => ({ ...prev, [doc.id]: true }))}
                      >
                        Edit
                      </Button>
                    </Tooltip>
                    <Tooltip title="Reject this document">
                      <Button
                        size="small"
                        danger
                        icon={<CloseOutlined />}
                        onClick={() => handleReject(doc.id)}
                      >
                        Reject
                      </Button>
                    </Tooltip>
                  </>
                )}
                {doc.classification_status === 'confirmed' && (
                  <Button
                    size="small"
                    icon={<EditOutlined />}
                    onClick={() => setEditing((prev) => ({ ...prev, [doc.id]: true }))}
                  >
                    Re-classify
                  </Button>
                )}
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default ClassificationReview;
