import React from 'react';
import { Tag, Space } from 'antd';
import {
  BankOutlined,
  UserOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';

const Navbar = ({ entityName, entityId }) => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="navbar-logo">CL</div>
        <div>
          <div className="navbar-title">CreditLens</div>
          <div className="navbar-subtitle">AI-Powered Credit Underwriting</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {entityId && (
          <div className="navbar-entity-info">
            <Space>
              <BankOutlined style={{ color: '#40a9ff' }} />
              <span style={{ color: 'rgba(255,255,255,0.85)', fontSize: 13 }}>
                {entityName || `Entity #${entityId}`}
              </span>
              <Tag
                color="blue"
                style={{ margin: 0, fontSize: 11 }}
              >
                ID: {entityId}
              </Tag>
            </Space>
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <SafetyCertificateOutlined style={{ color: '#52c41a', fontSize: 16 }} />
          <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>
            B2B FinTech Hackathon 2025
          </span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
