import React from 'react';
import { Form, Select, InputNumber, Row, Col } from 'antd';
import { Input } from 'antd';
import { DollarOutlined, CalendarOutlined } from '@ant-design/icons';

const { Option } = Select;
const { TextArea: AntTextArea } = Input;

const LOAN_TYPES = ['Term Loan', 'Working Capital', 'Overdraft', 'Letter of Credit', 'Bank Guarantee', 'ECB', 'NCD', 'Commercial Paper'];
const REPAYMENT_FREQ = ['Monthly', 'Quarterly', 'Half-Yearly', 'Annually', 'Bullet'];

const LoanDetailsForm = ({ form }) => {
  return (
    <div>
      <div className="section-title">
        <DollarOutlined /> Loan Parameters
      </div>
      
      <Row gutter={[24, 0]}>
        <Col xs={24} md={12}>
          <Form.Item
            label="Loan Type"
            name="loan_type"
          >
            <Select placeholder="Select loan type" size="large">
              {LOAN_TYPES.map(t => <Option key={t} value={t}>{t}</Option>)}
            </Select>
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item
            label="Loan Amount (₹ Cr)"
            name="loan_amount"
            rules={[{ required: true, message: 'Loan amount is required' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0.01}
              placeholder="e.g., 100.00"
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/,/g, '')}
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} md={12}>
          <Form.Item
            label="Tenure (months)"
            name="tenure_months"
            rules={[{ required: true, message: 'Tenure is required' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={1}
              max={360}
              placeholder="e.g., 60"
            />
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item label="Interest Rate (%)" name="interest_rate">
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              max={100}
              step={0.25}
              placeholder="e.g., 9.50"
              formatter={value => `${value}%`}
              parser={value => value.replace('%', '')}
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} md={12}>
          <Form.Item label="Repayment Frequency" name="repayment_frequency">
            <Select placeholder="Select repayment frequency" size="large">
              {REPAYMENT_FREQ.map(f => <Option key={f} value={f}>{f}</Option>)}
            </Select>
          </Form.Item>
        </Col>
      </Row>
      
      <div className="section-title" style={{ marginTop: 8 }}>
        <CalendarOutlined /> Additional Details
      </div>
      
      <Form.Item label="Purpose of Loan" name="purpose">
        <AntTextArea rows={3} placeholder="Describe the purpose of the loan..." size="large" />
      </Form.Item>
      
      <Form.Item label="Collateral Details" name="collateral_details">
        <AntTextArea rows={3} placeholder="Describe collateral offered (if any)..." size="large" />
      </Form.Item>
    </div>
  );
};

export default LoanDetailsForm;
