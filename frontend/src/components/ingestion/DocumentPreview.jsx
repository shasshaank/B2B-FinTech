import React from 'react';
import {
  Table, Tag, Button, Tooltip, Space, Typography, Popconfirm,
} from 'antd';
import {
  FileTextOutlined, FileExcelOutlined, PictureOutlined,
  DeleteOutlined, EyeOutlined,
} from '@ant-design/icons';
import { deleteDocument } from '../../services/api';

const { Text } = Typography;

const getFileIcon = (fileType) => {
  if (fileType === 'pdf') return <FileTextOutlined style={{ color: '#ff4d4f' }} />;
  if (fileType === 'excel') return <FileExcelOutlined style={{ color: '#52c41a' }} />;
  return <PictureOutlined style={{ color: '#1890ff' }} />;
};

const getStatusColor = (status) => {
  const map = {
    uploaded: 'default',
    classified: 'processing',
    confirmed: 'success',
    rejected: 'error',
  };
  return map[status] || 'default';
};

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const DocumentPreview = ({ documents, onDelete, onRefresh }) => {
  const handleDelete = async (docId) => {
    try {
      await deleteDocument(docId);
      if (onDelete) onDelete(docId);
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const columns = [
    {
      title: 'File',
      dataIndex: 'original_filename',
      key: 'filename',
      render: (name, record) => (
        <Space>
          {getFileIcon(record.file_type)}
          <div>
            <Text style={{ fontSize: 13, fontWeight: 500 }}>{name}</Text>
            <div>
              <Text type="secondary" style={{ fontSize: 11 }}>
                {formatFileSize(record.file_size)} • {record.file_type?.toUpperCase()}
              </Text>
            </div>
          </div>
        </Space>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'document_category',
      key: 'category',
      render: (cat) => cat ? (
        <Tag color="blue" style={{ borderRadius: 4 }}>{cat}</Tag>
      ) : (
        <Text type="secondary" style={{ fontSize: 12 }}>Not classified</Text>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'classification_status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)} style={{ textTransform: 'capitalize', borderRadius: 4 }}>
          {status}
        </Tag>
      ),
    },
    {
      title: 'Confidence',
      dataIndex: 'classification_confidence',
      key: 'confidence',
      render: (conf) => {
        if (!conf) return <Text type="secondary">—</Text>;
        const pct = (conf * 100).toFixed(0);
        const cls = conf >= 0.8 ? 'confidence-high' : conf >= 0.5 ? 'confidence-medium' : 'confidence-low';
        return <span className={cls}>{pct}%</span>;
      },
    },
    {
      title: 'Uploaded',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {date ? new Date(date).toLocaleString() : '—'}
        </Text>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Popconfirm
            title="Delete this document?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.id)}
            okText="Delete"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="Delete">
              <Button
                danger
                size="small"
                icon={<DeleteOutlined />}
                type="text"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      dataSource={documents}
      columns={columns}
      rowKey="id"
      pagination={{ pageSize: 10, hideOnSinglePage: true }}
      size="small"
      style={{ background: 'white', borderRadius: 10 }}
    />
  );
};

export default DocumentPreview;
