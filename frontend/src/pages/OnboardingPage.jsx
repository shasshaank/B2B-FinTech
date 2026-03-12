import React, { useState } from 'react';
import { Form, Button, Steps, message } from 'antd';
import { ArrowRightOutlined, CheckCircleOutlined } from '@ant-design/icons';
import EntityForm from '../components/onboarding/EntityForm';
import LoanDetailsForm from '../components/onboarding/LoanDetailsForm';
import { entityAPI } from '../services/api';
import dayjs from 'dayjs';

const STEPS = [
  { title: 'Entity Details', description: 'Company information' },
  { title: 'Loan Details', description: 'Loan parameters' },
];

const OnboardingPage = ({ onComplete }) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [entityId, setEntityId] = useState(null);
  const [entityName, setEntityName] = useState(null);

  const handleEntitySubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // Format date if present
      if (values.date_of_incorporation) {
        values.date_of_incorporation = dayjs(values.date_of_incorporation).format('YYYY-MM-DD');
      }

      const entity = await entityAPI.create(values);
      setEntityId(entity.id);
      setEntityName(entity.company_name);
      message.success('Entity created successfully!');
      setCurrentStep(1);
      form.resetFields();
    } catch (error) {
      if (error?.errorFields) {
        message.error('Please fill in all required fields');
      } else {
        message.error(`Failed to create entity: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoanSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      await entityAPI.createLoan(entityId, values);
      message.success('Loan details saved!');
      
      if (onComplete) onComplete(entityId, entityName);
    } catch (error) {
      if (error?.errorFields) {
        message.error('Please fill in all required fields');
      } else {
        message.error(`Failed to save loan details: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="stage-header">
        <h1>Stage 1: Entity Onboarding</h1>
        <p>Capture entity information and loan requirements for credit assessment</p>
      </div>

      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        <div className="creditlens-card" style={{ marginBottom: 24 }}>
          <Steps current={currentStep} items={STEPS} style={{ maxWidth: 600, margin: '0 auto' }} />
        </div>

        <div className="form-section">
          <Form form={form} layout="vertical" size="large" requiredMark="optional">
            {currentStep === 0 && <EntityForm form={form} />}
            {currentStep === 1 && <LoanDetailsForm form={form} />}
          </Form>

          <div className="nav-buttons">
            {currentStep > 0 && (
              <Button size="large" onClick={() => setCurrentStep(0)}>
                Back
              </Button>
            )}
            {currentStep === 0 && (
              <Button
                type="primary"
                size="large"
                icon={<ArrowRightOutlined />}
                onClick={handleEntitySubmit}
                loading={loading}
              >
                Save & Continue to Loan Details
              </Button>
            )}
            {currentStep === 1 && (
              <Button
                type="primary"
                size="large"
                icon={<CheckCircleOutlined />}
                onClick={handleLoanSubmit}
                loading={loading}
                style={{ background: '#16a34a', borderColor: '#16a34a' }}
              >
                Complete Onboarding & Proceed to Stage 2
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;
