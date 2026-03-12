import React, { useState } from 'react';
import { Form, Button, Steps, message, Typography, Space } from 'antd';
import { ArrowRightOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useApp } from '../../App';
import { createEntity, createLoanDetails } from '../../services/api';
import EntityForm from '../../components/onboarding/EntityForm';
import LoanDetailsForm from '../../components/onboarding/LoanDetailsForm';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const { Title, Text } = Typography;

const ONBOARDING_STEPS = [
  { title: 'Entity Details', description: 'Company information' },
  { title: 'Loan Details', description: 'Loan request specifics' },
];

const OnboardingPage = () => {
  const [entityForm] = Form.useForm();
  const [loanForm] = Form.useForm();
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [entityData, setEntityData] = useState(null);
  const { setEntityId, setEntityName, goToStage } = useApp();

  const handleEntitySubmit = async () => {
    try {
      const values = await entityForm.validateFields();
      setLoading(true);

      // Format date
      if (values.date_of_incorporation) {
        values.date_of_incorporation = values.date_of_incorporation.format('YYYY-MM-DD');
      }

      // Normalize CIN and PAN to uppercase
      if (values.cin) values.cin = values.cin.toUpperCase();
      if (values.pan) values.pan = values.pan.toUpperCase();

      const entity = await createEntity(values);
      setEntityData(entity);
      setEntityId(entity.id);
      setEntityName(entity.company_name);
      message.success(`Entity created: ${entity.company_name} (ID: ${entity.id})`);
      setStep(1);
    } catch (err) {
      if (err.errorFields) {
        message.error('Please fix the validation errors');
      } else {
        message.error(err.message || 'Failed to create entity');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLoanSubmit = async () => {
    try {
      const values = await loanForm.validateFields();
      setLoading(true);

      await createLoanDetails(entityData.id, values);
      message.success('Loan details saved successfully!');
      goToStage(1);
    } catch (err) {
      if (err.errorFields) {
        message.error('Please fix the validation errors');
      } else {
        message.error(err.message || 'Failed to save loan details');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <LoadingSpinner fullPage text="Saving information..." />}

      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>
          Stage 1: Entity Onboarding
        </Title>
        <Text type="secondary">
          Enter corporate entity details and loan request information
        </Text>
      </div>

      <div style={{ maxWidth: 200, marginBottom: 24 }}>
        <Steps
          current={step}
          direction="horizontal"
          size="small"
          items={ONBOARDING_STEPS}
        />
      </div>

      {step === 0 && (
        <>
          <Form
            form={entityForm}
            layout="vertical"
            requiredMark="optional"
          >
            <EntityForm form={entityForm} />
          </Form>
          <div style={{ textAlign: 'right', marginTop: 16 }}>
            <Button
              type="primary"
              size="large"
              icon={<ArrowRightOutlined />}
              onClick={handleEntitySubmit}
              loading={loading}
              style={{ minWidth: 160 }}
            >
              Next: Loan Details
            </Button>
          </div>
        </>
      )}

      {step === 1 && (
        <>
          {entityData && (
            <div style={{
              background: '#f6ffed',
              border: '1px solid #b7eb8f',
              borderRadius: 8,
              padding: '12px 16px',
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 16 }} />
              <Text>
                Entity <strong>{entityData.company_name}</strong> created with ID:{' '}
                <strong>{entityData.id}</strong>
              </Text>
            </div>
          )}

          <Form
            form={loanForm}
            layout="vertical"
            requiredMark="optional"
          >
            <LoanDetailsForm form={loanForm} />
          </Form>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16 }}>
            <Button size="large" onClick={() => setStep(0)}>
              ← Back
            </Button>
            <Space>
              <Button
                size="large"
                onClick={() => goToStage(1)}
              >
                Skip Loan Details
              </Button>
              <Button
                type="primary"
                size="large"
                icon={<ArrowRightOutlined />}
                onClick={handleLoanSubmit}
                loading={loading}
                style={{ minWidth: 200 }}
              >
                Save & Proceed to Stage 2
              </Button>
            </Space>
          </div>
        </>
      )}
    </div>
  );
};

export default OnboardingPage;
