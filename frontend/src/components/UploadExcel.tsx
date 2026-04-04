import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Upload, Button, Space } from 'antd';
import type { UploadFile } from 'antd/es/upload/interface';

interface UploadExcelProps {
  onClose: () => void;
}

export function UploadExcel({ onClose }: UploadExcelProps) {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const { addTask } = useTaskStore();

  const mutation = useMutation({
    mutationFn: api.continueSession,
    onSuccess: (_data, _variables) => {
      onClose();
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });

  const handleSubmit = () => {
    if (fileList.length === 0) return;

    const file = fileList[0];
    const filepath = `test_cases/${file.name}`;

    addTask({
      name: file.name,
      url: '',
      description: 'Continue session from Excel',
      status: 'running',
    });

    mutation.mutate({ excel_file: filepath });
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Upload.Dragger
        fileList={fileList}
        onChange={({ fileList }) => setFileList(fileList)}
        accept=".xlsx"
        maxCount={1}
      >
        <p>Click or drag Excel file to upload</p>
      </Upload.Dragger>

      <Space>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          type="primary"
          onClick={handleSubmit}
          disabled={fileList.length === 0}
          loading={mutation.isPending}
        >
          {mutation.isPending ? 'Processing...' : 'Upload & Continue'}
        </Button>
      </Space>
    </Space>
  );
}
