import React, { useState } from 'react';
import { Upload, message, Tag, Progress, List, Typography, Button, Space } from 'antd';
import { InboxOutlined, FileOutlined, FilePdfOutlined, FileExcelOutlined, FileImageOutlined, DeleteOutlined } from '@ant-design/icons';
import { documentAPI } from '../../services/api';

const { Dragger } = Upload;
const { Text } = Typography;

const CATEGORIES = [
  { key: 'alm', label: 'ALM', description: 'Asset-Liability Management', color: '#6366f1' },
  { key: 'shareholding', label: 'Shareholding', description: 'Shareholding Pattern', color: '#0ea5e9' },
  { key: 'borrowing', label: 'Borrowing', description: 'Borrowing Profile', color: '#10b981' },
  { key: 'annual_report', label: 'Annual Report', description: 'P&L, Cashflow, Balance Sheet', color: '#f59e0b' },
  { key: 'portfolio', label: 'Portfolio', description: 'Portfolio Performance Data', color: '#ef4444' },
];

const getFileIcon = (filename) => {
  const ext = filename?.split('.').pop()?.toLowerCase();
  if (ext === 'pdf') return <FilePdfOutlined style={{ color: '#ef4444' }} />;
  if (['xlsx', 'xls'].includes(ext)) return <FileExcelOutlined style={{ color: '#16a34a' }} />;
  if (['png', 'jpg', 'jpeg'].includes(ext)) return <FileImageOutlined style={{ color: '#1d3a8a' }} />;
  return <FileOutlined />;
};

const formatBytes = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

const DocumentUpload = ({ entityId, documents, onDocumentsChange }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const handleUpload = async (file) => {
    if (!entityId) {
      message.error('Please complete entity onboarding first');
      return false;
    }

    setUploading(true);
    setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: Math.min((prev[file.name] || 0) + 20, 80),
        }));
      }, 200);

      const uploaded = await documentAPI.upload(entityId, file);
      
      clearInterval(progressInterval);
      setUploadProgress(prev => ({ ...prev, [file.name]: 100 }));
      
      message.success(`${file.name} uploaded successfully`);
      onDocumentsChange([...documents, uploaded]);
      
      setTimeout(() => {
        setUploadProgress(prev => {
          const { [file.name]: _, ...rest } = prev;
          return rest;
        });
      }, 2000);
    } catch (error) {
      message.error(`Upload failed: ${error.message}`);
      setUploadProgress(prev => {
        const { [file.name]: _, ...rest } = prev;
        return rest;
      });
    } finally {
      setUploading(false);
    }
    return false; // Prevent default upload
  };

  const handleDelete = async (documentId) => {
    try {
      await documentAPI.delete(documentId);
      onDocumentsChange(documents.filter(d => d.id !== documentId));
      message.success('Document deleted');
    } catch (error) {
      message.error(`Delete failed: ${error.message}`);
    }
  };

  return (
    <div>
      {/* Category Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12, marginBottom: 24 }}>
        {CATEGORIES.map(cat => (
          <div key={cat.key} className="category-card" style={{ borderColor: cat.color }}>
            <div style={{ fontSize: 20, marginBottom: 4 }}>📁</div>
            <div style={{ fontWeight: 600, fontSize: 13, color: cat.color }}>{cat.label}</div>
            <div style={{ fontSize: 11, color: '#6b7280', marginTop: 4 }}>{cat.description}</div>
            <Tag color={cat.color} style={{ marginTop: 8, fontSize: 10 }}>
              {documents.filter(d => d.document_category?.toLowerCase().includes(cat.key.split('_')[0])).length} files
            </Tag>
          </div>
        ))}
      </div>

      {/* Upload Area */}
      <Dragger
        multiple
        beforeUpload={handleUpload}
        accept=".pdf,.xlsx,.xls,.png,.jpg,.jpeg"
        showUploadList={false}
        className="upload-area"
        style={{ padding: '20px', marginBottom: 20 }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ color: '#1d3a8a', fontSize: 48 }} />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 16, fontWeight: 600 }}>
          Drop financial documents here or click to browse
        </p>
        <p className="ant-upload-hint" style={{ color: '#6b7280' }}>
          Supports PDF, Excel (.xlsx, .xls), and Images (.png, .jpg, .jpeg)
        </p>
        <p className="ant-upload-hint">
          AI will automatically classify documents into ALM, Shareholding, Borrowing Profile, Annual Reports, or Portfolio Data
        </p>
      </Dragger>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).map(filename => (
        <div key={filename} style={{ marginBottom: 8, background: '#f0f9ff', padding: '8px 12px', borderRadius: 8 }}>
          <Space>
            {getFileIcon(filename)}
            <Text ellipsis style={{ maxWidth: 300 }}>{filename}</Text>
          </Space>
          <Progress percent={uploadProgress[filename]} size="small" />
        </div>
      ))}

      {/* Documents List */}
      {documents.length > 0 && (
        <div>
          <div style={{ fontWeight: 600, marginBottom: 12, color: '#374151' }}>
            Uploaded Documents ({documents.length})
          </div>
          <List
            dataSource={documents}
            renderItem={(doc) => (
              <List.Item
                style={{ background: '#fafafa', marginBottom: 8, borderRadius: 8, padding: '12px 16px', border: '1px solid #e8ecf0' }}
                actions={[
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDelete(doc.id)}
                    size="small"
                  />
                ]}
              >
                <List.Item.Meta
                  avatar={getFileIcon(doc.original_filename || doc.filename)}
                  title={<Text strong>{doc.original_filename || doc.filename}</Text>}
                  description={
                    <Space wrap>
                      <Tag color="blue">{doc.file_type?.toUpperCase()}</Tag>
                      <Text type="secondary" style={{ fontSize: 12 }}>{formatBytes(doc.file_size)}</Text>
                      <Tag color={doc.classification_status === 'confirmed' ? 'success' : doc.classification_status === 'classified' ? 'processing' : 'default'}>
                        {doc.classification_status}
                      </Tag>
                      {doc.document_category && <Tag color="purple">{doc.document_category}</Tag>}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
