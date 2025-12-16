#!/usr/bin/env node

/**
 * 构建时配置验证脚本
 * 在构建过程中验证所有必需的环境变量
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 颜色输出函数
const colors = {
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`
};

// 必需的环境变量配置
const REQUIRED_VARS = {
  VITE_API_BASE_URL: {
    description: 'API基础URL',
    validator: (value) => {
      try {
        const url = new URL(value);
        return ['http:', 'https:'].includes(url.protocol);
      } catch {
        return false;
      }
    },
    errorMsg: 'VITE_API_BASE_URL必须是有效的HTTP/HTTPS URL'
  }
};

// 可选的环境变量配置
const OPTIONAL_VARS = {
  VITE_APP_TITLE: {
    description: '应用标题',
    default: 'AI食谱推荐',
    validator: (value) => value && value.length > 0
  },
  VITE_DEBUG: {
    description: '调试模式',
    default: 'false',
    validator: (value) => ['true', 'false'].includes(value.toLowerCase())
  },
  VITE_BUILD_TIME: {
    description: '构建时间戳',
    default: new Date().toISOString(),
    validator: (value) => {
      try {
        new Date(value);
        return true;
      } catch {
        return false;
      }
    }
  }
};

/**
 * 验证环境变量
 */
function validateEnvironmentVariables() {
  console.log(colors.bold('\n🔧 构建时环境变量验证\n'));
  
  let hasErrors = false;
  let hasWarnings = false;
  const results = [];

  // 验证必需变量
  console.log(colors.bold('必需变量:'));
  for (const [varName, config] of Object.entries(REQUIRED_VARS)) {
    const value = process.env[varName];
    
    if (!value) {
      console.log(colors.red(`  ✗ ${varName}: 缺失`));
      console.log(colors.red(`    ${config.errorMsg || config.description}`));
      hasErrors = true;
      results.push({ name: varName, status: 'error', message: '缺失' });
    } else if (!config.validator(value)) {
      console.log(colors.red(`  ✗ ${varName}: ${value}`));
      console.log(colors.red(`    ${config.errorMsg}`));
      hasErrors = true;
      results.push({ name: varName, status: 'error', message: '格式无效' });
    } else {
      console.log(colors.green(`  ✓ ${varName}: ${value}`));
      results.push({ name: varName, status: 'valid', value });
    }
  }

  // 验证可选变量
  console.log(colors.bold('\n可选变量:'));
  for (const [varName, config] of Object.entries(OPTIONAL_VARS)) {
    const value = process.env[varName];
    
    if (!value) {
      const defaultValue = config.default;
      console.log(colors.yellow(`  ⚠ ${varName}: 使用默认值 "${defaultValue}"`));
      hasWarnings = true;
      results.push({ name: varName, status: 'default', value: defaultValue });
      
      // 设置默认值到环境变量中
      process.env[varName] = defaultValue;
    } else if (!config.validator(value)) {
      console.log(colors.red(`  ✗ ${varName}: ${value}`));
      console.log(colors.red(`    格式无效，使用默认值 "${config.default}"`));
      hasWarnings = true;
      results.push({ name: varName, status: 'invalid', value: config.default });
      
      // 使用默认值
      process.env[varName] = config.default;
    } else {
      console.log(colors.green(`  ✓ ${varName}: ${value}`));
      results.push({ name: varName, status: 'valid', value });
    }
  }

  // 输出摘要
  console.log(colors.bold('\n📊 验证摘要:'));
  if (hasErrors) {
    console.log(colors.red('  状态: 失败 - 存在必需变量缺失或无效'));
    console.log(colors.red('  请设置所有必需的环境变量后重新构建'));
    return false;
  } else if (hasWarnings) {
    console.log(colors.yellow('  状态: 警告 - 使用了默认值'));
    console.log(colors.yellow('  建议明确设置所有环境变量'));
  } else {
    console.log(colors.green('  状态: 通过 - 所有变量配置正确'));
  }

  // 保存验证结果到文件
  const reportPath = path.join(__dirname, '../dist/build-config-report.json');
  const reportDir = path.dirname(reportPath);
  
  // 确保目录存在
  try {
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
  } catch (error) {
    console.log(colors.yellow(`⚠ 无法创建目录 ${reportDir}: ${error.message}`));
  }
  
  const report = {
    timestamp: new Date().toISOString(),
    status: hasErrors ? 'error' : hasWarnings ? 'warning' : 'success',
    results,
    environment: {
      NODE_ENV: process.env.NODE_ENV,
      npm_package_version: process.env.npm_package_version
    }
  };
  
  try {
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(colors.blue(`\n📄 验证报告已保存到: ${reportPath}`));
  } catch (error) {
    console.log(colors.yellow(`\n⚠ 无法保存验证报告: ${error.message}`));
  }

  return !hasErrors;
}

/**
 * 显示使用帮助
 */
function showHelp() {
  console.log(colors.bold('\n🔧 构建配置验证脚本\n'));
  console.log('用法:');
  console.log('  node scripts/validate-build-config.js');
  console.log('');
  console.log('环境变量:');
  console.log('  必需:');
  for (const [varName, config] of Object.entries(REQUIRED_VARS)) {
    console.log(`    ${varName} - ${config.description}`);
  }
  console.log('  可选:');
  for (const [varName, config] of Object.entries(OPTIONAL_VARS)) {
    console.log(`    ${varName} - ${config.description} (默认: ${config.default})`);
  }
  console.log('');
  console.log('示例:');
  console.log('  VITE_API_BASE_URL=https://api.example.com npm run build');
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    return;
  }

  const isValid = validateEnvironmentVariables();
  
  if (!isValid) {
    console.log(colors.red('\n❌ 构建配置验证失败'));
    process.exit(1);
  } else {
    console.log(colors.green('\n✅ 构建配置验证通过'));
  }
}

// 直接运行主函数
main();

export {
  validateEnvironmentVariables,
  REQUIRED_VARS,
  OPTIONAL_VARS
};