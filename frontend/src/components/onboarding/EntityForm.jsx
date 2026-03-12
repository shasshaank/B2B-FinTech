import React from 'react';
import {
  Form, Input, Select, DatePicker, InputNumber, Row, Col, Card,
} from 'antd';
import {
  BankOutlined, IdcardOutlined,
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

const SECTORS = [
  'Banking', 'NBFC', 'Manufacturing', 'IT/ITES', 'Infrastructure',
  'Pharma', 'Real Estate', 'Retail', 'Agriculture', 'Others',
];

const CREDIT_RATINGS = [
  'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-',
  'BBB+', 'BBB', 'BBB-', 'Below BBB-', 'Not Rated',
];

const RATING_AGENCIES = [
  'CRISIL', 'ICRA', 'CARE', 'India Ratings', 'Acuité', 'Brickwork',
];

const EntityForm = ({ form }) => {
  return (
    <Card
      title={
        <span>
          <BankOutlined style={{ marginRight: 8 }} />
          Entity Details
        </span>
      }
      className="form-card"
      style={{ marginBottom: 24 }}
    >
      <Row gutter={24}>
        <Col xs={24} md={12}>
          <Form.Item
            name="company_name"
            label="Company Name"
            rules={[{ required: true, message: 'Please enter company name' }]}
          >
            <Input
              prefix={<BankOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="e.g. HDFC Bank Limited"
              size="large"
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            name="cin"
            label="CIN (Corporate Identity Number)"
            rules={[
              { required: true, message: 'Please enter CIN' },
              {
                pattern: /^[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$/,
                message: 'Invalid CIN format (e.g. U65920MH2000PLC128450)',
              },
            ]}
          >
            <Input
              prefix={<IdcardOutlined style={{ color: '#bfbfbf' }} />}
              placeholder="e.g. U65920MH2000PLC128450"
              size="large"
              style={{ textTransform: 'uppercase' }}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item
            name="pan"
            label="PAN"
            rules={[
              { required: true, message: 'Please enter PAN' },
              {
                pattern: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
                message: 'Invalid PAN format (e.g. ABCDE1234F)',
              },
            ]}
          >
            <Input
              placeholder="e.g. ABCDE1234F"
              size="large"
              style={{ textTransform: 'uppercase' }}
              maxLength={10}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item name="sector" label="Sector / Industry">
            <Select placeholder="Select sector" size="large">
              {SECTORS.map((s) => (
                <Option key={s} value={s}>{s}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item name="sub_sector" label="Sub-sector">
            <Input placeholder="e.g. Retail Banking, Auto Loans" size="large" />
          </Form.Item>
        </Col>

        <Col xs={24} md={12}>
          <Form.Item name="date_of_incorporation" label="Date of Incorporation">
            <DatePicker
              style={{ width: '100%' }}
              size="large"
              format="DD/MM/YYYY"
              placeholder="Select date"
            />
          </Form.Item>
        </Col>

        <Col xs={24}>
          <Form.Item name="registered_address" label="Registered Address">
            <TextArea
              rows={2}
              placeholder="Enter registered address"
              showCount
              maxLength={500}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item name="annual_turnover" label="Annual Turnover (₹ Cr)">
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              precision={2}
              placeholder="e.g. 5000.00"
              formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item name="net_worth" label="Net Worth (₹ Cr)">
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              precision={2}
              placeholder="e.g. 1200.00"
              formatter={(v) => `₹ ${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(v) => v.replace(/₹\s?|(,*)/g, '')}
            />
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item name="credit_rating" label="Credit Rating">
            <Select placeholder="Select rating" size="large">
              {CREDIT_RATINGS.map((r) => (
                <Option key={r} value={r}>{r}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>

        <Col xs={24} md={8}>
          <Form.Item name="rating_agency" label="Rating Agency">
            <Select placeholder="Select agency" size="large">
              {RATING_AGENCIES.map((a) => (
                <Option key={a} value={a}>{a}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default EntityForm;
