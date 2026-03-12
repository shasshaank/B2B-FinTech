import React from 'react';
import {
  Form, Select, InputNumber, Row, Col, Card,
} from 'antd';
import { DollarOutlined } from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = require('antd').Input;

const LOAN_TYPES = [
  'Term Loan', 'Working Capital', 'Overdraft', 'Letter of Credit',
  'Bank Guarantee', 'ECB', 'NCD', 'Commercial Paper',
];

const REPAYMENT_FREQUENCIES = [
  'Monthly', 'Quarterly', 'Half-Yearly', 'Annually', 'Bullet',
];

const LoanDetailsForm = ({ form }) => {
  return (
    <Card
      title={
        <span>
          <DollarOutlined style={{ marginRight: 8 }} />
          Loan Details
        </span>
      }
      className="form-card"
      style={{ marginBottom: 24 }}
    >
      <Row gutter={24}>
        <Col xs={24} md={12}>
          <Form.Item
            name="loan_type"
            label="Loan Type"
          >
            <Select placeholder="Select loan type" size="large">
              {LOAN_TYPES.map((t) => (
                <Option key={t} value={t}>{t}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            name="loan_amount"
            label="Loan Amount (₹ Cr)"
            rules={[{ required: true, message: 'Please enter loan amount' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0.01}
              precision={2}
              placeholder="e.g. 500.00"
              formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item
            name="tenure_months"
            label="Tenure (months)"
            rules={[{ required: true, message: 'Please enter tenure' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={1}
              max={360}
              placeholder="e.g. 60"
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item
            name="interest_rate"
            label="Interest Rate (%)"
          >
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              max={100}
              precision={2}
              placeholder="e.g. 9.50"
              formatter={(v) => `${v}%`}
              parser={(v) => v.replace('%', '')}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item
            name="repayment_frequency"
            label="Repayment Frequency"
          >
            <Select placeholder="Select frequency" size="large">
              {REPAYMENT_FREQUENCIES.map((f) => (
                <Option key={f} value={f}>{f}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item name="purpose" label="Purpose of Loan">
            <TextArea
              rows={3}
              placeholder="Describe the purpose of the loan..."
              showCount
              maxLength={1000}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item name="collateral_details" label="Collateral Details">
            <TextArea
              rows={3}
              placeholder="Describe collateral offered..."
              showCount
              maxLength={1000}
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default LoanDetailsForm;
