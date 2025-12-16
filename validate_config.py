#!/usr/bin/env python3
# validate_config.py - 独立的配置验证脚本
"""
环境变量配置验证脚本

用法:
    python validate_config.py                    # 验证当前环境
    python validate_config.py --json            # 输出JSON格式报告
    python validate_config.py --fix             # 尝试修复常见问题
    python validate_config.py --check-cors URL  # 检查CORS配置
"""

import sys
import argparse
import json
import os
from typing import List, Dict, Any
import requests
from env_manager import EnvironmentManager, ConfigStatus


def main():
    parser = argparse.ArgumentParser(description='验证环境变量配置')
    parser.add_argument('--json', action='store_true', help='输出JSON格式报告')
    parser.add_argument('--fix', action='store_true', help='尝试修复常见配置问题')
    parser.add_argument('--check-cors', metavar='URL', help='检查指定URL的CORS配置')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式，只输出错误')
    
    args = parser.parse_args()
    
    manager = EnvironmentManager()
    
    if args.fix:
        fix_common_issues(manager)
    
    if args.check_cors:
        check_cors_configuration(args.check_cors, manager)
        return
    
    # 验证配置
    report = manager.validate_environment_variables()
    
    if args.json:
        print(manager.generate_config_report_json())
    elif not args.quiet:
        manager.print_config_status()
        print_recommendations(report)
    
    # 设置退出码
    if report.overall_status == ConfigStatus.INVALID:
        sys.exit(1)
    elif report.overall_status == ConfigStatus.WARNING and not args.quiet:
        print("⚠️  存在警告，但可以继续运行")
    elif not args.quiet:
        print("✅ 配置验证通过")


def fix_common_issues(manager: EnvironmentManager):
    """尝试修复常见的配置问题"""
    print("🔧 尝试修复常见配置问题...")
    
    fixes_applied = []
    
    # 检查SECRET_KEY
    if not os.getenv("SECRET_KEY"):
        # 生成一个安全的密钥
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"建议设置 SECRET_KEY={secret_key}")
        fixes_applied.append("生成了新的SECRET_KEY建议")
    
    # 检查CORS_ORIGINS
    cors_origins = os.getenv("CORS_ORIGINS")
    if not cors_origins:
        suggested_origins = "http://localhost:5173,http://localhost:3000"
        print(f"建议设置 CORS_ORIGINS={suggested_origins}")
        fixes_applied.append("提供了CORS_ORIGINS建议")
    
    # 检查Railway环境
    if os.getenv("RAILWAY_ENVIRONMENT"):
        railway_url = os.getenv("RAILWAY_STATIC_URL")
        if not railway_url:
            print("检测到Railway环境，但缺少RAILWAY_STATIC_URL")
            print("请在Railway项目设置中添加此环境变量")
            fixes_applied.append("检测到Railway配置问题")
    
    if fixes_applied:
        print(f"应用了 {len(fixes_applied)} 个修复建议")
        for fix in fixes_applied:
            print(f"  - {fix}")
    else:
        print("未发现需要修复的常见问题")


def check_cors_configuration(url: str, manager: EnvironmentManager):
    """检查CORS配置是否正确"""
    print(f"🌐 检查CORS配置: {url}")
    
    try:
        # 发送OPTIONS请求检查CORS
        response = requests.options(
            url,
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("CORS响应头:")
        for header, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"  {status} {header}: {value or '未设置'}")
        
        # 检查配置的CORS源
        configured_origins = manager.get_cors_origins()
        print(f"\n配置的CORS源: {configured_origins}")
        
        # 验证是否匹配
        allow_origin = cors_headers.get('Access-Control-Allow-Origin')
        if allow_origin == '*' or 'http://localhost:5173' in configured_origins:
            print("✅ CORS配置看起来正确")
        else:
            print("⚠️  CORS配置可能有问题")
            
    except requests.RequestException as e:
        print(f"❌ 无法连接到 {url}: {e}")
        print("请检查URL是否正确，服务是否正在运行")


def print_recommendations(report) -> None:
    """打印配置建议"""
    recommendations = []
    
    for item in report.items:
        if item.status == ConfigStatus.MISSING and item.required:
            recommendations.append(f"设置必需的环境变量: export {item.name}=<值>")
        elif item.status == ConfigStatus.INVALID:
            recommendations.append(f"修复环境变量 {item.name} 的格式")
    
    if recommendations:
        print("\n📋 建议操作:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Railway特定建议
    if os.getenv("RAILWAY_ENVIRONMENT"):
        print("\n🚂 Railway部署建议:")
        print("  - 在Railway项目设置中配置环境变量")
        print("  - 确保前后端服务都设置了正确的URL")
        print("  - 检查域名配置是否正确")


if __name__ == "__main__":
    main()