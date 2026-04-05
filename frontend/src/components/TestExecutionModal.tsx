import { useState, useEffect, useRef } from 'react';
import { Modal, Typography, Tag, Space } from 'antd';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;

interface TestExecutionModalProps {
  open: boolean;
  taskId: string;
  taskName: string;
  onClose: () => void;
}

interface OutputLine {
  type: 'stdout' | 'stderr' | 'result';
  content: string;
  passed?: number;
  failed?: number;
  duration?: string;
}

export function TestExecutionModal({ open, taskId, taskName, onClose }: TestExecutionModalProps) {
  const { t } = useTranslation();
  const [outputs, setOutputs] = useState<OutputLine[]>([]);
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running');
  const [summary, setSummary] = useState<{ passed: number; failed: number; duration: string } | null>(null);
  const outputRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (!open || !taskId) return;

    setOutputs([]);
    setStatus('running');
    setSummary(null);

    const eventSource = new EventSource(`/api/run-test/${taskId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'result') {
        setStatus(data.status === 'success' ? 'completed' : 'error');
        setSummary({
          passed: data.passed || 0,
          failed: data.failed || 0,
          duration: data.duration || '0s'
        });
        setOutputs(prev => [...prev, { type: 'result', content: '', ...data }]);
        eventSource.close();
      } else {
        setOutputs(prev => [...prev, { type: data.type, content: data.content }]);
      }
    };

    eventSource.onerror = () => {
      setStatus('error');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [open, taskId]);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [outputs]);

  const getStatusTag = () => {
    switch (status) {
      case 'running':
        return <Tag color="processing">{t('testExecution.running')}</Tag>;
      case 'completed':
        return <Tag color="success">{t('testExecution.completed')}</Tag>;
      case 'error':
        return <Tag color="error">{t('testExecution.error')}</Tag>;
    }
  };

  return (
    <Modal
      title={
        <Space>
          <span>{t('testExecution.title')}</span>
          <Tag>{taskName}</Tag>
          {getStatusTag()}
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnClose
    >
      <pre
        ref={outputRef}
        style={{
          background: '#1e1e1e',
          color: '#d4d4d4',
          padding: '16px',
          borderRadius: '4px',
          maxHeight: '400px',
          overflow: 'auto',
          fontFamily: 'Monaco, Menlo, monospace',
          fontSize: '12px',
          lineHeight: '1.5',
          margin: 0
        }}
      >
        {outputs.map((line, index) => {
          if (line.type === 'result') return null;
          const color = line.type === 'stderr' ? '#f48771' : '#d4d4d4';
          return (
            <div key={index} style={{ color }}>
              {line.content}
            </div>
          );
        })}
      </pre>

      {summary && (
        <div style={{ marginTop: 16 }}>
          <Space>
            <Tag color="green">{t('testExecution.passed')}: {summary.passed}</Tag>
            {summary.failed > 0 && <Tag color="red">{t('testExecution.failed')}: {summary.failed}</Tag>}
            <Text type="secondary">{t('testExecution.duration')}: {summary.duration}</Text>
          </Space>
        </div>
      )}
    </Modal>
  );
}
