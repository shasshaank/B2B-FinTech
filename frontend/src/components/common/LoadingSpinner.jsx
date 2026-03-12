import React from 'react';
import { Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const { Text } = Typography;

const LoadingSpinner = ({ text = 'Loading...', size = 'large' }) => {
  return (
    <div className="loading-container">
      <Spin
        indicator={<LoadingOutlined style={{ fontSize: size === 'large' ? 48 : 24 }} spin />}
        size={size}
      />
      <Text type="secondary">{text}</Text>
    </div>
  );
};

export default LoadingSpinner;
