import React, { useState, useEffect } from 'react';
import {
  Table, Button, Select, Switch, Tag, Typography, Space,
  Card, message, Tooltip, Popconfirm,
} from 'antd';
import {
  PlusOutlined, DeleteOutlined, SaveOutlined,
} from '@ant-design/icons';
import { getSchema, updateSchema } from '../../services/api';

const { Text } = Typography;
const { Option } = Select;

const FIELD_TYPES = ['string', 'number', 'date', 'currency'];

const SchemaEditor = ({ entityId }) => {
  const [schemaData, setSchemaData] = useState({});
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (entityId) loadSchema();
  }, [entityId]);

  const loadSchema = async () => {
    setLoading(true);
    try {
      const result = await getSchema(entityId);
      setSchemaData(result.schema_data || {});
      const categories = Object.keys(result.schema_data || {});
      if (categories.length > 0) setSelectedCategory(categories[0]);
    } catch (err) {
      message.error('Failed to load schema');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSchema(entityId, schemaData);
      message.success('Schema saved successfully');
    } catch (err) {
      message.error('Failed to save schema');
    } finally {
      setSaving(false);
    }
  };

  const currentSchema = selectedCategory ? (schemaData[selectedCategory] || []) : [];

  const handleCellEdit = (index, field, value) => {
    const updated = [...currentSchema];
    updated[index] = { ...updated[index], [field]: value };
    setSchemaData((prev) => ({ ...prev, [selectedCategory]: updated }));
  };

  const handleAddField = () => {
    const newField = {
      field_name: 'new_field',
      field_type: 'string',
      required: false,
      description: '',
    };
    setSchemaData((prev) => ({
      ...prev,
      [selectedCategory]: [...currentSchema, newField],
    }));
  };

  const handleDeleteField = (index) => {
    const updated = currentSchema.filter((_, i) => i !== index);
    setSchemaData((prev) => ({ ...prev, [selectedCategory]: updated }));
  };

  const columns = [
    {
      title: 'Field Name',
      dataIndex: 'field_name',
      key: 'field_name',
      render: (val, _, index) => (
        <input
          value={val}
          onChange={(e) => handleCellEdit(index, 'field_name', e.target.value)}
          style={{
            border: '1px solid #d9d9d9',
            borderRadius: 4,
            padding: '4px 8px',
            fontSize: 13,
            width: '100%',
          }}
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
          size="small"
          style={{ width: '100%' }}
          onChange={(v) => handleCellEdit(index, 'field_type', v)}
        >
          {FIELD_TYPES.map((t) => <Option key={t} value={t}>{t}</Option>)}
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
          size="small"
          onChange={(v) => handleCellEdit(index, 'required', v)}
        />
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (val, _, index) => (
        <input
          value={val}
          onChange={(e) => handleCellEdit(index, 'description', e.target.value)}
          style={{
            border: '1px solid #d9d9d9',
            borderRadius: 4,
            padding: '4px 8px',
            fontSize: 13,
            width: '100%',
          }}
        />
      ),
    },
    {
      title: '',
      key: 'action',
      width: 50,
      render: (_, __, index) => (
        <Popconfirm
          title="Delete this field?"
          onConfirm={() => handleDeleteField(index)}
          okText="Delete"
          okButtonProps={{ danger: true }}
        >
          <Button danger size="small" icon={<DeleteOutlined />} type="text" />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <Text strong>Category:</Text>
          <Select
            value={selectedCategory}
            onChange={setSelectedCategory}
            style={{ minWidth: 280 }}
            placeholder="Select document category"
          >
            {Object.keys(schemaData).map((cat) => (
              <Option key={cat} value={cat}>{cat}</Option>
            ))}
          </Select>
        </Space>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          loading={saving}
        >
          Save Schema
        </Button>
      </div>

      {selectedCategory && (
        <Card
          size="small"
          style={{ borderRadius: 10 }}
          extra={
            <Button
              size="small"
              icon={<PlusOutlined />}
              type="dashed"
              onClick={handleAddField}
            >
              Add Field
            </Button>
          }
          title={<Text strong>Fields for: {selectedCategory}</Text>}
        >
          <Table
            dataSource={currentSchema.map((item, i) => ({ ...item, key: i }))}
            columns={columns}
            pagination={false}
            size="small"
            loading={loading}
          />
        </Card>
      )}
    </div>
  );
};

export default SchemaEditor;
