// envManager.ts - 前端环境变量管理和验证系统
export const ConfigStatus = {
  VALID: 'valid',
  MISSING: 'missing',
  INVALID: 'invalid',
  WARNING: 'warning'
} as const;

export type ConfigStatus = typeof ConfigStatus[keyof typeof ConfigStatus];

export interface ConfigItem {
  name: string;
  value: string | null;
  status: ConfigStatus;
  message: string;
  required: boolean;
}

export interface ConfigReport {
  items: ConfigItem[];
  overallStatus: ConfigStatus;
  summary: string;
}

export interface EnvironmentConfig {
  apiBaseUrl: string;
  isProduction: boolean;
  buildTime: string;
}

class FrontendEnvironmentManager {
  // 必需的环境变量配置
  private readonly REQUIRED_VARS = {
    VITE_API_BASE_URL: {
      description: 'API基础URL',
      validator: (value: string) => this.validateUrl(value),
      errorMsg: 'VITE_API_BASE_URL必须是有效的URL'
    }
  };

  // 可选的环境变量配置
  private readonly OPTIONAL_VARS = {
    VITE_APP_TITLE: {
      description: '应用标题',
      validator: (value: string) => value.length > 0,
      errorMsg: 'VITE_APP_TITLE不能为空',
      default: 'AI食谱推荐'
    },
    VITE_DEBUG: {
      description: '调试模式',
      validator: (value: string) => ['true', 'false'].includes(value.toLowerCase()),
      errorMsg: 'VITE_DEBUG必须是true或false',
      default: 'false'
    }
  };

  /**
   * 验证URL格式
   */
  private validateUrl(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return ['http:', 'https:'].includes(urlObj.protocol);
    } catch {
      return false;
    }
  }

  /**
   * 获取环境变量值
   */
  private getEnvVar(name: string): string | null {
    // 在构建时，Vite会将环境变量注入到import.meta.env中
    const value = (import.meta.env as any)[name];
    return value || null;
  }

  /**
   * 验证所有环境变量
   */
  public validateEnvironmentVariables(): ConfigReport {
    const items: ConfigItem[] = [];
    let hasErrors = false;
    let hasWarnings = false;

    // 检查必需变量
    for (const [varName, config] of Object.entries(this.REQUIRED_VARS)) {
      const value = this.getEnvVar(varName);

      if (value === null) {
        items.push({
          name: varName,
          value: null,
          status: ConfigStatus.MISSING,
          message: `缺少必需的环境变量: ${config.description}`,
          required: true
        });
        hasErrors = true;
      } else if (!config.validator(value)) {
        items.push({
          name: varName,
          value: value,
          status: ConfigStatus.INVALID,
          message: config.errorMsg,
          required: true
        });
        hasErrors = true;
      } else {
        items.push({
          name: varName,
          value: value,
          status: ConfigStatus.VALID,
          message: `✓ ${config.description}配置正确`,
          required: true
        });
      }
    }

    // 检查可选变量
    for (const [varName, config] of Object.entries(this.OPTIONAL_VARS)) {
      const value = this.getEnvVar(varName);

      if (value === null) {
        const defaultValue = config.default;
        items.push({
          name: varName,
          value: defaultValue,
          status: ConfigStatus.WARNING,
          message: `使用默认值: ${defaultValue}`,
          required: false
        });
        hasWarnings = true;
      } else if (!config.validator(value)) {
        items.push({
          name: varName,
          value: value,
          status: ConfigStatus.INVALID,
          message: config.errorMsg,
          required: false
        });
        hasWarnings = true;
      } else {
        items.push({
          name: varName,
          value: value,
          status: ConfigStatus.VALID,
          message: `✓ ${config.description}配置正确`,
          required: false
        });
      }
    }

    // 确定整体状态
    let overallStatus: ConfigStatus;
    let summary: string;

    if (hasErrors) {
      overallStatus = ConfigStatus.INVALID;
      summary = '配置验证失败：存在必需变量缺失或无效';
    } else if (hasWarnings) {
      overallStatus = ConfigStatus.WARNING;
      summary = '配置基本正确，但存在警告项';
    } else {
      overallStatus = ConfigStatus.VALID;
      summary = '所有配置项验证通过';
    }

    return {
      items,
      overallStatus,
      summary
    };
  }

  /**
   * 获取API基础URL
   */
  public getApiBaseUrl(): string {
    const configuredUrl = this.getEnvVar('VITE_API_BASE_URL');
    
    // 如果配置了环境变量且有效，使用它
    if (configuredUrl && this.validateUrl(configuredUrl)) {
      return configuredUrl;
    }

    // 在生产环境中，尝试自动检测
    if (import.meta.env.PROD) {
      // 如果是在Railway等平台部署，尝试使用相对路径
      const currentOrigin = window.location.origin;
      
      // 检查是否有Railway域名模式
      if (currentOrigin.includes('railway.app')) {
        // 尝试多种Railway后端URL模式
        const possibleBackendUrls = [
          currentOrigin.replace('-frontend', '-backend'),
          currentOrigin.replace('frontend-', 'backend-'),
          currentOrigin.replace('frontend.', 'backend.'),
          // 如果前端域名包含项目名，尝试构建后端URL
          currentOrigin.replace(/frontend/g, 'backend')
        ];
        
        // 返回第一个可能的URL（实际使用时会通过连接测试验证）
        return possibleBackendUrls[0];
      }
      
      // 默认假设后端在同一域名的不同端口或路径
      return currentOrigin;
    }

    // 开发环境默认值
    return 'http://localhost:8000';
  }

  /**
   * 获取构建时信息
   */
  public getBuildInfo(): { buildTime: string; version: string; environment: string } {
    return {
      buildTime: this.getEnvVar('VITE_BUILD_TIME') || 'unknown',
      version: (globalThis as any).__VERSION__ || '1.0.0',
      environment: import.meta.env.MODE || 'development'
    };
  }

  /**
   * 验证构建时配置
   */
  public validateBuildConfiguration(): { isValid: boolean; errors: string[]; warnings: string[] } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // 检查必需的构建时变量
    const apiUrl = this.getEnvVar('VITE_API_BASE_URL');
    if (!apiUrl) {
      errors.push('VITE_API_BASE_URL 未在构建时设置');
    } else if (!this.validateUrl(apiUrl)) {
      errors.push(`VITE_API_BASE_URL 格式无效: ${apiUrl}`);
    }

    // 检查构建时间戳
    const buildTime = this.getEnvVar('VITE_BUILD_TIME');
    if (!buildTime) {
      warnings.push('VITE_BUILD_TIME 未设置，可能影响缓存管理');
    }

    // 检查应用标题
    const appTitle = this.getEnvVar('VITE_APP_TITLE');
    if (!appTitle) {
      warnings.push('VITE_APP_TITLE 未设置，将使用默认标题');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * 获取环境配置
   */
  public getEnvironmentConfig(): EnvironmentConfig {
    return {
      apiBaseUrl: this.getApiBaseUrl(),
      isProduction: import.meta.env.PROD,
      buildTime: import.meta.env.VITE_BUILD_TIME || new Date().toISOString()
    };
  }

  /**
   * 打印配置状态到控制台
   */
  public printConfigStatus(): void {
    const report = this.validateEnvironmentVariables();
    
    console.group('🔧 环境变量配置状态报告');
    console.log(`整体状态: ${report.overallStatus.toUpperCase()}`);
    console.log(`摘要: ${report.summary}`);
    console.log('');

    // 按状态分组显示
    const statusOrder = [ConfigStatus.INVALID, ConfigStatus.MISSING, ConfigStatus.WARNING, ConfigStatus.VALID];
    
    for (const status of statusOrder) {
      const statusItems = report.items.filter(item => item.status === status);
      if (statusItems.length > 0) {
        console.group(`${status.toUpperCase()} 项目:`);
        for (const item of statusItems) {
          const requiredMark = item.required ? '[必需]' : '[可选]';
          console.log(`${requiredMark} ${item.name}: ${item.message}`);
        }
        console.groupEnd();
      }
    }
    
    console.groupEnd();
  }

  /**
   * 生成配置报告的JSON字符串
   */
  public generateConfigReportJson(): string {
    const report = this.validateEnvironmentVariables();
    return JSON.stringify(report, null, 2);
  }

  /**
   * 检查配置是否就绪
   */
  public isConfigurationReady(): boolean {
    const report = this.validateEnvironmentVariables();
    return report.overallStatus !== ConfigStatus.INVALID;
  }
}

// 创建全局实例
export const frontendEnvManager = new FrontendEnvironmentManager();

// 便捷函数
export function validateFrontendEnvironment(): ConfigReport {
  return frontendEnvManager.validateEnvironmentVariables();
}

export function getFrontendConfig(): EnvironmentConfig {
  return frontendEnvManager.getEnvironmentConfig();
}

export function getApiBaseUrl(): string {
  return frontendEnvManager.getApiBaseUrl();
}

// 在开发模式下自动打印配置状态
if (import.meta.env.DEV) {
  frontendEnvManager.printConfigStatus();
}