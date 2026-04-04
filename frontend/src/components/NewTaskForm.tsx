import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Form, Input, Button, Space, message } from 'antd';

interface NewTaskFormProps {
  onClose: () => void;
}

export function NewTaskForm({ onClose }: NewTaskFormProps) {
  const [form] = Form.useForm();
  const { addTask } = useTaskStore();

  const mutation = useMutation({
    mutationFn: async (data: { url: string; filepath: string; description: string; username?: string; password?: string }) => {
      const response = await api.generate(data);
      return response;
    },
    onSuccess: (response, variables) => {
      // Use backend's task_id, not local generated one
      addTask({
        id: response.task_id,  // Use backend's task_id
        name: variables.filepath || `Task-${Date.now()}`,
        url: variables.url,
        description: variables.description,
        status: 'pending',
      });
      message.success('Task created successfully');
      onClose();
    },
    onError: (error: Error) => {
      console.error('Generation failed:', error);
      message.error('Failed to create task: ' + error.message);
      onClose();
    },
  });

  const onFinish = (values: {
    url: string;
    filepath?: string;
    username?: string;
    password?: string;
    description: string;
  }) => {
    mutation.mutate({
      url: values.url,
      filepath: values.filepath || `test_cases/${Date.now()}.xlsx`,
      username: values.username,
      password: values.password,
      description: values.description,
    });
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item
        name="url"
        label="URL"
        rules={[{ required: true, message: 'Please input the URL' }]}
      >
        <Input placeholder="https://example.com" />
      </Form.Item>

      <Form.Item name="filepath" label="Save Path">
        <Input placeholder="test_cases/my_test.xlsx" />
      </Form.Item>

      <Space style={{ width: '100%' }} size="middle">
        <Form.Item name="username" label="Username" style={{ flex: 1 }}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="Password" style={{ flex: 1 }}>
          <Input.Password />
        </Form.Item>
      </Space>

      <Form.Item
        name="description"
        label="Description"
        rules={[{ required: true, message: 'Please input the description' }]}
      >
        <Input.TextArea rows={3} placeholder="Describe what you want to test..." />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={mutation.isPending}>
            {mutation.isPending ? 'Generating...' : 'Generate'}
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
}
