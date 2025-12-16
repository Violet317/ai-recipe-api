/**
 * 前后端连接测试工具
 * 用于验证API连接状态和配置正确性
 */

import { getApiBaseUrl } from '../envManager';

export interface ConnectionTestResult {
  success: boolean;
  apiUrl: string;
  responseTime: number;
  error?: string;
  details?: {
    status?: number;
    headers?: Record<string, string>;
    cors?: boolean;
  };
}

/**
 * 测试API连接
 */
export async function testApiConnection(): Promise<ConnectionTestResult> {
  const apiUrl = getApiBaseUrl();
  const startTime = Date.now();
  
  try {
    // 尝试访问健康检查端点
    const response = await fetch(`${apiUrl}/health`, {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const responseTime = Date.now() - startTime;
    
    if (response.ok) {
      return {
        success: true,
        apiUrl,
        responseTime,
        details: {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries()),
          cors: true
        }
      };
    } else {
      return {
        success: false,
        apiUrl,
        responseTime,
        error: `HTTP ${response.status}: ${response.statusText}`,
        details: {
          status: response.status,
          cors: true
        }
      };
    }
  } catch (error) {
    const responseTime = Date.now() - startTime;
    
    if (error instanceof TypeError && error.message.includes('CORS')) {
      return {
        success: false,
        apiUrl,
        responseTime,
        error: 'CORS错误 - 跨域请求被阻止',
        details: {
          cors: false
        }
      };
    }
    
    return {
      success: false,
      apiUrl,
      responseTime,
      error: error instanceof Error ? error.message : '未知错误'
    };
  }
}

/**
 * 测试多个可能的API URL
 */
export async function testMultipleApiUrls(urls: string[]): Promise<ConnectionTestResult[]> {
  const results = await Promise.allSettled(
    urls.map(async (url) => {
      // 临时覆盖API URL
      (window as any).tempApiUrl = url;
      
      try {
        const result = await testApiConnection();
        return { ...result, apiUrl: url };
      } finally {
        delete (window as any).tempApiUrl;
      }
    })
  );
  
  return results.map((result, index) => {
    if (result.status === 'fulfilled') {
      return result.value;
    } else {
      return {
        success: false,
        apiUrl: urls[index],
        responseTime: 0,
        error: result.reason?.message || '测试失败'
      };
    }
  });
}

/**
 * 自动发现Railway后端URL
 */
export function discoverRailwayBackendUrls(): string[] {
  const currentOrigin = window.location.origin;
  
  if (!currentOrigin.includes('railway.app')) {
    return [];
  }
  
  // 生成可能的后端URL模式
  const patterns = [
    currentOrigin.replace('-frontend', '-backend'),
    currentOrigin.replace('frontend-', 'backend-'),
    currentOrigin.replace('frontend.', 'backend.'),
    currentOrigin.replace(/frontend/g, 'backend'),
    // 尝试不同的子域名模式
    currentOrigin.replace(/^https:\/\/([^.]+)/, 'https://backend'),
    currentOrigin.replace(/^https:\/\/([^.]+)/, 'https://api'),
  ];
  
  // 去重并过滤掉与当前URL相同的
  return [...new Set(patterns)].filter(url => url !== currentOrigin);
}

/**
 * 执行完整的连接诊断
 */
export async function performConnectionDiagnostics(): Promise<{
  configuredUrl: ConnectionTestResult;
  discoveredUrls: ConnectionTestResult[];
  recommendations: string[];
}> {
  // 测试配置的URL
  const configuredUrl = await testApiConnection();
  
  // 测试发现的URL
  const discoveredUrls = await testMultipleApiUrls(discoverRailwayBackendUrls());
  
  // 生成建议
  const recommendations: string[] = [];
  
  if (!configuredUrl.success) {
    recommendations.push('配置的API URL无法连接，请检查VITE_API_BASE_URL环境变量');
    
    const workingUrls = discoveredUrls.filter(result => result.success);
    if (workingUrls.length > 0) {
      recommendations.push(`发现可用的API URL: ${workingUrls[0].apiUrl}`);
      recommendations.push('建议更新环境变量配置');
    }
    
    if (discoveredUrls.some(result => result.details?.cors === false)) {
      recommendations.push('检测到CORS问题，请检查后端CORS配置');
    }
  }
  
  return {
    configuredUrl,
    discoveredUrls,
    recommendations
  };
}