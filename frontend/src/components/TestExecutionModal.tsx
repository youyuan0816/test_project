import { useState, useEffect, useRef } from 'react';
import { Modal, Typography, Tag, Space, Tabs, Button } from 'antd';
import { ExpandOutlined, CompressOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;

interface TestExecutionModalProps {
  open: boolean;
  taskId: string;
  taskName: string;
  onClose: () => void;
  onComplete?: (taskId: string) => void;
  historyMode?: boolean;
  initialContent?: string;
  reportUrl?: string;
}

interface OutputLine {
  type: 'stdout' | 'stderr' | 'result';
  content: string;
  passed?: number;
  failed?: number;
  duration?: string;
}

export function TestExecutionModal({ open, taskId, taskName, onClose, onComplete, historyMode = false, initialContent = '', reportUrl }: TestExecutionModalProps) {
  const { t } = useTranslation();
  const [outputs, setOutputs] = useState<OutputLine[]>([]);
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running');
  const [summary, setSummary] = useState<{ passed: number; failed: number; duration: string } | null>(null);
  const [fullScreen, setFullScreen] = useState(false);
  const outputRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (!open || !taskId) return;

    setOutputs([]);
    setStatus('running');
    setSummary(null);
    setFullScreen(false);

    // History mode: skip SSE, use initialContent directly
    if (historyMode) {
      if (initialContent) {
        setOutputs([{ type: 'stdout', content: initialContent }]);
        setStatus('completed');
      }
      return;
    }

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
        if (onComplete) {
          onComplete(taskId);
        }
      } else {
        setOutputs(prev => [...prev, { type: data.type, content: data.content }]);
      }
    };

    eventSource.onerror = () => {
      setStatus('error');
      eventSource.close();
      if (onComplete) {
        onComplete(taskId);
      }
    };

    return () => {
      eventSource.close();
    };
  }, [open, taskId, historyMode, initialContent, onComplete]);

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
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <span>{t('testExecution.title')}</span>
            <Tag>{taskName}</Tag>
            {getStatusTag()}
          </Space>
          <Button
            type="text"
            icon={fullScreen ? <CompressOutlined /> : <ExpandOutlined />}
            onClick={() => setFullScreen(!fullScreen)}
          />
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={fullScreen ? '100%' : 900}
      height={fullScreen ? '100%' : undefined}
      style={fullScreen ? { top: 0, paddingBottom: 0 } : undefined}
      styles={fullScreen ? { body: { height: 'calc(100vh - 110px)' } } : {}}
      destroyOnClose
    >
      <Tabs
        defaultActiveKey="log"
        items={[
          {
            key: 'log',
            label: t('testExecution.log'),
            children: (
              <>
                <pre
                  ref={outputRef}
                  style={{
                    background: '#1e1e1e',
                    color: '#d4d4d4',
                    padding: '16px',
                    borderRadius: '4px',
                    maxHeight: fullScreen ? 'calc(100vh - 200px)' : '400px',
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
              </>
            ),
          },
          ...(reportUrl ? [{
            key: 'report',
            label: t('testExecution.report'),
            children: (
              <iframe
                src={reportUrl}
                style={{ width: '100%', height: fullScreen ? 'calc(100vh - 200px)' : '500px', border: 'none' }}
                title="Test Report"
              />
            ),
          }] : []),
        ]}
      />
    </Modal>
  );
}
