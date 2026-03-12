import React, { useState, useCallback } from 'react';
import {
  Upload, message, Card, Tag, Typography, Row, Col,
  Progress, Space, Button, Tooltip,
} from 'antd';
import {
  InboxOutlined, FileTextOutlined, FileExcelOutlined,
  PictureOutlined, CheckCircleOutlined, DeleteOutlined,
} from '@ant-design/icons';
import { uploadDocument } from '../../services/api';

const { Dragger } = Upload;
const { Text, Title } = Typography;

const DOCUMENT_CATEGORIES = [
  { key: 'ALM', label: 'ALM', description: 'Asset-Liability Management', color: '#1890ff' },
  { key: 'Shareholding Pattern', label: 'Shareholding', description: 'Shareholding Pattern', color: '#722ed1' },
  { key: 'Borrowing Profile', label: 'Borrowing', description: 'Borrowing Profile', color: '#13c2c2' },
  { key: 'Annual Report', label: 'Annual Report', description: 'P&L / Balance Sheet / Cash Flow', color: '#52c41a' },
  { key: 'Portfolio Performance Data', label: 'Portfolio', description: 'Portfolio Performance Data', color: '#fa8c16' },
];

const getFileIcon = (fileType) => {
  if (fileType === 'pdf') return <FileTextOutlined style={{ color: '#ff4d4f', fontSize: 20 }} />;
  if (fileType === 'excel') return <FileExcelOutlined style={{ color: '#52c41a', fontSize: 20 }} />;
  return <PictureOutlined style={{ color: '#1890ff', fontSize: 20 }} />;
};

const DocumentUpload = ({ entityId, onUploadComplete }) => {
  const [uploadingFiles, setUploadingFiles] = useState({});
  const [selectedCategory, setSelectedCategory] = useState(null);

  const handleUpload = useCallback(async (file) => {
    const fileId = `${file.name}-${Date.now()}`;
    setUploadingFiles((prev) => ({ ...prev, [fileId]: { name: file.name, progress: 0, status: 'uploading' } }));

    try {
      const result = await uploadDocument(entityId, file, selectedCategory);
      setUploadingFiles((prev) => ({
        ...prev,
        [fileId]: { name: file.name, progress: 100, status: 'done' },
      }));
      message.success(`${file.name} uploaded successfully`);
      if (onUploadComplete) onUploadComplete(result);
    } catch (err) {
      setUploadingFiles((prev) => ({
        ...prev,
        [fileId]: { name: file.name, progress: 0, status: 'error' },
      }));
      message.error(`Failed to upload ${file.name}: ${err.message}`);
    }

    return false; // Prevent default upload behavior
  }, [entityId, selectedCategory, onUploadComplete]);

  return (
    <div>
      {/* Category Selection */}
      <Card
        size="small"
        title="Document Category (optional — AI will auto-classify)"
        style={{ marginBottom: 16, borderRadius: 10 }}
      >
        <Row gutter={[8, 8]}>
          {DOCUMENT_CATEGORIES.map((cat) => (
            <Col key={cat.key}>
              <Tag
                style={{
                  cursor: 'pointer',
                  padding: '6px 14px',
                  borderRadius: 20,
                  fontSize: 13,
                  border: selectedCategory === cat.key
                    ? `2px solid ${cat.color}`
                    : '1px solid #d9d9d9',
                  background: selectedCategory === cat.key ? `${cat.color}15` : 'white',
                  fontWeight: selectedCategory === cat.key ? 600 : 400,
                }}
                color={selectedCategory === cat.key ? cat.color : undefined}
                onClick={() => setSelectedCategory(selectedCategory === cat.key ? null : cat.key)}
              >
                {selectedCategory === cat.key && (
                  <CheckCircleOutlined style={{ marginRight: 4 }} />
                )}
                {cat.label}
              </Tag>
            </Col>
          ))}
        </Row>
        {selectedCategory && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Files will be tagged as: <strong>{selectedCategory}</strong>{' '}
              <Button type="link" size="small" onClick={() => setSelectedCategory(null)} style={{ padding: 0 }}>
                Clear
              </Button>
            </Text>
          </div>
        )}
      </Card>

      {/* Upload Dragger */}
      <Dragger
        multiple
        beforeUpload={handleUpload}
        accept=".pdf,.xlsx,.xls,.png,.jpg,.jpeg"
        showUploadList={false}
        className="upload-dragger"
        style={{ padding: '20px 0' }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: '#1890ff' }} />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 16, fontWeight: 600 }}>
          Click or drag documents here to upload
        </p>
        <p className="ant-upload-hint" style={{ color: '#8c8c8c' }}>
          Supports PDF, Excel (.xlsx, .xls), and Images (.png, .jpg, .jpeg)
          <br />
          Multiple files can be uploaded simultaneously
        </p>
      </Dragger>

      {/* Upload Progress */}
      {Object.keys(uploadingFiles).length > 0 && (
        <div style={{ marginTop: 16 }}>
          {Object.entries(uploadingFiles).map(([id, file]) => (
            <div
              key={id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '8px 12px',
                background: '#fafafa',
                borderRadius: 8,
                marginBottom: 6,
              }}
            >
              {getFileIcon('pdf')}
              <div style={{ flex: 1 }}>
                <Text style={{ fontSize: 13 }}>{file.name}</Text>
                <Progress
                  percent={file.progress}
                  size="small"
                  status={file.status === 'error' ? 'exception' : file.status === 'done' ? 'success' : 'active'}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
