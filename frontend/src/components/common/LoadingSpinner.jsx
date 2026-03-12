import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

const LoadingSpinner = ({ text = 'Processing...', fullPage = false }) => {
  const spinner = (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 40,
    }}>
      <Spin
        indicator={<LoadingOutlined style={{ fontSize: 40, color: '#1890ff' }} spin />}
      />
      <div className="loading-text">{text}</div>
    </div>
  );

  if (fullPage) {
    return <div className="loading-overlay">{spinner}</div>;
  }

  return spinner;
};

export default LoadingSpinner;
