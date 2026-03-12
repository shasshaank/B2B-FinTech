import React from 'react';
import { Typography, Tag } from 'antd';
import { BankOutlined, UserOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Navbar = ({ entityName, entityId }) => {
  return (
    <div className="creditlens-navbar">
      <div className="navbar-brand">
        <div className="navbar-logo">
          <BankOutlined style={{ color: 'white', fontSize: '18px' }} />
        </div>
        <div>
          <Title className="navbar-title" level={4}>CreditLens</Title>
          <div className="navbar-subtitle">AI-Powered Credit Underwriting</div>
        </div>
      </div>
      
      {entityName && (
        <div className="navbar-entity-info">
          <UserOutlined />
          <span>{entityName}</span>
          {entityId && <Tag color="blue" style={{ marginLeft: 4 }}>ID: {entityId}</Tag>}
        </div>
      )}
    </div>
  );
};

export default Navbar;
