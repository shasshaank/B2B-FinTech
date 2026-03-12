import React from 'react';
import { Modal, Typography, Tag, Descriptions } from 'antd';
import { FilePdfOutlined, FileExcelOutlined, FileImageOutlined } from '@ant-design/icons';

const { Text } = Typography;

const DocumentPreview = ({ document, visible, onClose }) => {
  if (!document) return null;

  const isImage = ['png', 'jpg', 'jpeg'].includes(document.file_type?.toLowerCase());
  const isPDF = document.file_type?.toLowerCase() === 'pdf';

  return (
    <Modal
      title={
        <span>
          {isPDF ? <FilePdfOutlined style={{ color: '#ef4444', marginRight: 8 }} /> :
           isImage ? <FileImageOutlined style={{ color: '#1d3a8a', marginRight: 8 }} /> :
           <FileExcelOutlined style={{ color: '#16a34a', marginRight: 8 }} />}
          {document.original_filename}
        </span>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={700}
    >
      <Descriptions bordered size="small" column={2}>
        <Descriptions.Item label="File Type">
          <Tag color="blue">{document.file_type?.toUpperCase()}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Status">
          <Tag color={document.classification_status === 'confirmed' ? 'success' : 'processing'}>
            {document.classification_status}
          </Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Category" span={2}>
          {document.document_category || <Text type="secondary">Not classified yet</Text>}
        </Descriptions.Item>
        {document.classification_confidence && (
          <Descriptions.Item label="AI Confidence" span={2}>
            <Text style={{ color: document.classification_confidence > 0.8 ? '#16a34a' : document.classification_confidence > 0.5 ? '#d97706' : '#dc2626' }}>
              {(document.classification_confidence * 100).toFixed(1)}%
            </Text>
          </Descriptions.Item>
        )}
      </Descriptions>
    </Modal>
  );
};

export default DocumentPreview;
