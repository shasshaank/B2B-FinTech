import React from 'react';
import { Form, Input, Select, DatePicker, InputNumber, Row, Col } from 'antd';
import { 
  BankOutlined, IdcardOutlined, ApartmentOutlined 
} from '@ant-design/icons';
const { TextArea } = Input;
const { Option } = Select;

const SECTORS = ['Banking', 'NBFC', 'Manufacturing', 'IT/ITES', 'Infrastructure', 'Pharma', 'Real Estate', 'Retail', 'Agriculture', 'Others'];
const CREDIT_RATINGS = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'Below BBB-', 'Not Rated'];
const RATING_AGENCIES = ['CRISIL', 'ICRA', 'CARE', 'India Ratings', 'Acuité', 'Brickwork'];

const EntityForm = ({ form }) => {
  return (
    <div>
      <div className="section-title">
        <BankOutlined /> Company Information
      </div>
      
      <Row gutter={[24, 0]}>
        <Col xs={24} md={12}>
          <Form.Item
            label="Company Name"
            name="company_name"
            rules={[{ required: true, message: 'Company name is required' }]}
          >
            <Input placeholder="e.g., Acme Financial Services Ltd" size="large" />
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item
            label="CIN (Corporate Identity Number)"
            name="cin"
            rules={[
              {
                pattern: /^[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$/,
                message: 'Invalid CIN format (e.g., U65929TN2010PTC078194)',
              }
            ]}
          >
            <Input placeholder="e.g., U65929TN2010PTC078194" size="large" maxLength={21} />
          </Form.Item>
        </Col>
        
        <Col xs={24} md={12}>
          <Form.Item
            label="PAN"
            name="pan"
            rules={[
              {
                pattern: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,
                message: 'Invalid PAN format (e.g., ABCDE1234F)',
              }
            ]}
          >
            <Input placeholder="e.g., ABCDE1234F" size="large" maxLength={10} style={{ textTransform: 'uppercase' }} />
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item label="Date of Incorporation" name="date_of_incorporation">
            <DatePicker style={{ width: '100%' }} size="large" format="DD-MM-YYYY" />
          </Form.Item>
        </Col>
      </Row>
      
      <div className="section-title" style={{ marginTop: 8 }}>
        <ApartmentOutlined /> Sector & Classification
      </div>
      
      <Row gutter={[24, 0]}>
        <Col xs={24} md={12}>
          <Form.Item label="Sector / Industry" name="sector">
            <Select placeholder="Select sector" size="large" showSearch>
              {SECTORS.map(s => <Option key={s} value={s}>{s}</Option>)}
            </Select>
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item label="Sub-sector" name="sub_sector">
            <Input placeholder="e.g., Retail Lending, Cloud Computing" size="large" />
          </Form.Item>
        </Col>
      </Row>
      
      <Form.Item label="Registered Address" name="registered_address">
        <TextArea rows={3} placeholder="Full registered address of the company" size="large" />
      </Form.Item>
      
      <div className="section-title" style={{ marginTop: 8 }}>
        <IdcardOutlined /> Financial Overview
      </div>
      
      <Row gutter={[24, 0]}>
        <Col xs={24} md={12}>
          <Form.Item label="Annual Turnover (₹ Cr)" name="annual_turnover">
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              placeholder="e.g., 500.00"
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/,/g, '')}
            />
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item label="Net Worth (₹ Cr)" name="net_worth">
            <InputNumber
              style={{ width: '100%' }}
              size="large"
              min={0}
              placeholder="e.g., 200.00"
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/,/g, '')}
            />
          </Form.Item>
        </Col>
        
        <Col xs={24} md={12}>
          <Form.Item label="Credit Rating" name="credit_rating">
            <Select placeholder="Select credit rating" size="large">
              {CREDIT_RATINGS.map(r => <Option key={r} value={r}>{r}</Option>)}
            </Select>
          </Form.Item>
        </Col>
        <Col xs={24} md={12}>
          <Form.Item label="Rating Agency" name="rating_agency">
            <Select placeholder="Select rating agency" size="large">
              {RATING_AGENCIES.map(r => <Option key={r} value={r}>{r}</Option>)}
            </Select>
          </Form.Item>
        </Col>
      </Row>
    </div>
  );
};

export default EntityForm;
