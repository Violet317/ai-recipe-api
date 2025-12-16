// ConfigStatus.tsx - 前端配置状态显示组件
import React, { useState, useEffect } from 'react';
import { frontendEnvManager, ConfigStatus as Status } from '../envManager';
import type { ConfigReport } from '../envManager';
import { performConnectionDiagnostics } from '../utils/connectionTest';

interface ConfigStatusProps {
  showDetails?: boolean;
  onConfigReady?: (isReady: boolean) => void;
}

const ConfigStatusComponent: React.FC<ConfigStatusProps> = ({ 
  showDetails = false, 
  onConfigReady 
}) => {
  const [report, setReport] = useState<ConfigReport | null>(null);
  const [buildValidation, setBuildValidation] = useState<any>(null);
  const [connectionTest, setConnectionTest] = useState<any>(null);
  const [isExpanded, setIsExpanded] = useState(showDetails);
  const [isTestingConnection, setIsTestingConnection] = useState(false);

  useEffect(() => {
    const configReport = frontendEnvManager.validateEnvironmentVariables();
    const buildConfig = frontendEnvManager.validateBuildConfiguration();
    setReport(configReport);
    setBuildValidation(buildConfig);
    
    if (onConfigReady) {
      onConfigReady(configReport.overallStatus !== Status.INVALID && buildConfig.isValid);
    }
  }, [onConfigReady]);

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    try {
      const diagnostics = await performConnectionDiagnostics();
      setConnectionTest(diagnostics);
    } catch (error) {
      setConnectionTest({
        configuredUrl: {
          success: false,
          apiUrl: frontendEnvManager.getApiBaseUrl(),
          responseTime: 0,
          error: error instanceof Error ? error.message : '测试失败'
        },
        discoveredUrls: [],
        recommendations: ['连接测试失败，请检查网络连接']
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  if (!report || !buildValidation) {
    return <div>加载配置状态...</div>;
  }

  const getStatusIcon = (status: Status): string => {
    switch (status) {
      case Status.VALID:
        return '✅';
      case Status.WARNING:
        return '⚠️';
      case Status.INVALID:
        return '❌';
      case Status.MISSING:
        return '🔍';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status: Status): string => {
    switch (status) {
      case Status.VALID:
        return '#10b981'; // green
      case Status.WARNING:
        return '#f59e0b'; // yellow
      case Status.INVALID:
      case Status.MISSING:
        return '#ef4444'; // red
      default:
        return '#6b7280'; // gray
    }
  };

  const criticalIssues = report.items.filter(
    item => item.required && (item.status === Status.INVALID || item.status === Status.MISSING)
  );

  return (
    <div style={{ 
      border: `2px solid ${getStatusColor(report.overallStatus)}`,
      borderRadius: '8px',
      padding: '16px',
      margin: '16px 0',
      backgroundColor: '#f9fafb'
    }}>
      <div 
        style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          cursor: 'pointer'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '20px' }}>
            {getStatusIcon(report.overallStatus)}
          </span>
          <h3 style={{ margin: 0, color: getStatusColor(report.overallStatus) }}>
            配置状态: {report.overallStatus.toUpperCase()}
          </h3>
        </div>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>
          {isExpanded ? '收起' : '展开'}
        </span>
      </div>

      <p style={{ margin: '8px 0', color: '#374151' }}>
        {report.summary}
      </p>

      {/* 构建时配置验证状态 */}
      <div style={{ 
        backgroundColor: buildValidation.isValid ? '#ecfdf5' : '#fef2f2',
        border: `1px solid ${buildValidation.isValid ? '#10b981' : '#ef4444'}`,
        borderRadius: '4px',
        padding: '12px',
        margin: '12px 0'
      }}>
        <h4 style={{ margin: '0 0 8px 0', color: buildValidation.isValid ? '#059669' : '#dc2626' }}>
          {buildValidation.isValid ? '✅' : '❌'} 构建时配置验证
        </h4>
        {buildValidation.errors.length > 0 && (
          <div style={{ marginBottom: '8px' }}>
            <strong style={{ color: '#dc2626' }}>错误:</strong>
            <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
              {buildValidation.errors.map((error: string, index: number) => (
                <li key={index} style={{ color: '#dc2626', fontSize: '14px' }}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        {buildValidation.warnings.length > 0 && (
          <div>
            <strong style={{ color: '#d97706' }}>警告:</strong>
            <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
              {buildValidation.warnings.map((warning: string, index: number) => (
                <li key={index} style={{ color: '#d97706', fontSize: '14px' }}>{warning}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* API连接测试 */}
      <div style={{ 
        backgroundColor: '#f0f9ff',
        border: '1px solid #bae6fd',
        borderRadius: '4px',
        padding: '12px',
        margin: '12px 0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h4 style={{ margin: 0, color: '#0369a1' }}>🌐 API连接测试</h4>
          <button 
            onClick={handleTestConnection}
            disabled={isTestingConnection}
            style={{
              padding: '4px 12px',
              fontSize: '12px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isTestingConnection ? 'not-allowed' : 'pointer',
              opacity: isTestingConnection ? 0.6 : 1
            }}
          >
            {isTestingConnection ? '测试中...' : '测试连接'}
          </button>
        </div>
        
        {connectionTest && (
          <div style={{ fontSize: '14px' }}>
            <div style={{ 
              padding: '8px',
              backgroundColor: connectionTest.configuredUrl.success ? '#ecfdf5' : '#fef2f2',
              borderRadius: '4px',
              marginBottom: '8px'
            }}>
              <strong>API URL: {connectionTest.configuredUrl.apiUrl}</strong>
              <br />
              状态: {connectionTest.configuredUrl.success ? '✅ 连接成功' : '❌ 连接失败'}
              <br />
              响应时间: {connectionTest.configuredUrl.responseTime}ms
              {connectionTest.configuredUrl.error && (
                <div style={{ color: '#dc2626', marginTop: '4px' }}>
                  错误: {connectionTest.configuredUrl.error}
                </div>
              )}
            </div>
            
            {connectionTest.recommendations.length > 0 && (
              <div>
                <strong>建议:</strong>
                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                  {connectionTest.recommendations.map((rec: string, index: number) => (
                    <li key={index} style={{ fontSize: '13px' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {criticalIssues.length > 0 && (
        <div style={{ 
          backgroundColor: '#fef2f2', 
          border: '1px solid #fecaca',
          borderRadius: '4px',
          padding: '12px',
          margin: '12px 0'
        }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#dc2626' }}>
            ❌ 关键问题 ({criticalIssues.length})
          </h4>
          {criticalIssues.map((item, index) => (
            <div key={index} style={{ marginBottom: '4px', fontSize: '14px' }}>
              <strong>{item.name}:</strong> {item.message}
            </div>
          ))}
        </div>
      )}

      {isExpanded && (
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ margin: '0 0 12px 0', color: '#374151' }}>
            详细配置项
          </h4>
          
          {Object.values(Status).map(status => {
            const statusItems = report.items.filter(item => item.status === status);
            if (statusItems.length === 0) return null;

            return (
              <div key={status} style={{ marginBottom: '16px' }}>
                <h5 style={{ 
                  margin: '0 0 8px 0', 
                  color: getStatusColor(status),
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {getStatusIcon(status)} {status.toUpperCase()} ({statusItems.length})
                </h5>
                
                {statusItems.map((item, index) => (
                  <div 
                    key={index}
                    style={{ 
                      marginLeft: '24px',
                      marginBottom: '8px',
                      padding: '8px',
                      backgroundColor: 'white',
                      borderRadius: '4px',
                      border: '1px solid #e5e7eb'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '4px'
                    }}>
                      <strong style={{ color: '#1f2937' }}>
                        {item.name}
                      </strong>
                      <span style={{ 
                        fontSize: '12px',
                        padding: '2px 6px',
                        borderRadius: '12px',
                        backgroundColor: item.required ? '#dbeafe' : '#f3f4f6',
                        color: item.required ? '#1e40af' : '#6b7280'
                      }}>
                        {item.required ? '必需' : '可选'}
                      </span>
                    </div>
                    
                    <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
                      {item.message}
                    </div>
                    
                    {item.value && (
                      <div style={{ 
                        fontSize: '12px', 
                        fontFamily: 'monospace',
                        backgroundColor: '#f9fafb',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        color: '#374151'
                      }}>
                        值: {item.value}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            );
          })}

          <div style={{ 
            marginTop: '16px',
            padding: '12px',
            backgroundColor: '#f0f9ff',
            borderRadius: '4px',
            border: '1px solid #bae6fd'
          }}>
            <h5 style={{ margin: '0 0 8px 0', color: '#0369a1' }}>
              💡 当前环境信息
            </h5>
            <div style={{ fontSize: '14px', color: '#0c4a6e' }}>
              <div>API基础URL: {frontendEnvManager.getApiBaseUrl()}</div>
              <div>生产环境: {import.meta.env.PROD ? '是' : '否'}</div>
              <div>构建时间: {frontendEnvManager.getBuildInfo().buildTime}</div>
              <div>版本: {frontendEnvManager.getBuildInfo().version}</div>
              <div>环境模式: {frontendEnvManager.getBuildInfo().environment}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigStatusComponent;