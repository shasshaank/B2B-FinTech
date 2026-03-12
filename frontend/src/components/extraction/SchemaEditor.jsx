import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Switch, Space, message, Tabs, Tag, Tooltip } from 'antd';
import { PlusOutlined, DeleteOutlined, SaveOutlined } from '@ant-design/icons';
import { extractionAPI } from '../../services/api';

const { Option } = Select;
const { TabPane } = Tabs;

const FIELD_TYPES = ['string', 'number', 'date', 'currency'];

const SchemaEditor = ({ entityId }) => {
  const [schemas, setSchemas] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSchemas();
  }, [entityId]);

  const loadSchemas = async () => {
    if (!entityId) return;
    try {
      const data = await extractionAPI.getSchema(entityId);
      setSchemas(data.schemas || {});
    } catch (error) {
      message.error(`Failed to load schemas: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const updateField = (category, index, field, value) => {
    setSchemas(prev => ({
      ...prev,
      [category]: prev[category].map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      ),
    }));
  };

  const addField = (category) => {
    setSchemas(prev => ({
      ...prev,
      [category]: [...(prev[category] || []), {
        field_name: 'new_field',
        field_type: 'string',
        required: false,
        description: ''
      }],
    }));
  };

  const removeField = (category, index) => {
    setSchemas(prev => ({
      ...prev,
      [category]: prev[category].filter((_, i) => i !== index),
    }));
  };

  const saveSchemas = async () => {
    setSaving(true);
    try {
      await extractionAPI.updateSchema(entityId, schemas);
      message.success('Schemas saved successfully');
    } catch (error) {
      message.error(`Failed to save: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const getColumns = (category) => [
    {
      title: 'Field Name',
      dataIndex: 'field_name',
      key: 'field_name',
      render: (val, _, index) => (
        <Input
          value={val}
          onChange={e => updateField(category, index, 'field_name', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: 'Type',
      dataIndex: 'field_type',
      key: 'field_type',
      width: 120,
      render: (val, _, index) => (
        <Select
          value={val}
          onChange={v => updateField(category, index, 'field_type', v)}
          size="small"
          style={{ width: '100%' }}
        >
          {FIELD_TYPES.map(t => <Option key={t} value={t}>{t}</Option>)}
        </Select>
      ),
    },
    {
      title: 'Required',
      dataIndex: 'required',
      key: 'required',
      width: 80,
      render: (val, _, index) => (
        <Switch
          checked={val}
          onChange={v => updateField(category, index, 'required', v)}
          size="small"
        />
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (val, _, index) => (
        <Input
          value={val}
          onChange={e => updateField(category, index, 'description', e.target.value)}
          size="small"
          placeholder="Field description"
        />
      ),
    },
    {
      title: '',
      key: 'action',
      width: 50,
      render: (_, __, index) => (
        <Button
          size="small"
          danger
          icon={<DeleteOutlined />}
          onClick={() => removeField(category, index)}
        />
      ),
    },
  ];

  const tabItems = Object.keys(schemas).map(category => ({
    key: category,
    label: (
      <Tooltip title={category}>
        <span>{category.split(' - ')[1] || category.split(' ')[0]}</span>
      </Tooltip>
    ),
    children: (
      <div>
        <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            size="small"
            icon={<PlusOutlined />}
            onClick={() => addField(category)}
            type="dashed"
          >
            Add Field
          </Button>
        </div>
        <Table
          dataSource={schemas[category] || []}
          columns={getColumns(category)}
          rowKey={(_, i) => i}
          pagination={false}
          size="small"
        />
      </div>
    ),
  }));

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={saveSchemas}
          loading={saving}
        >
          Save All Schemas
        </Button>
      </div>
      <Tabs items={tabItems} type="card" />
    </div>
  );
};

export default SchemaEditor;
