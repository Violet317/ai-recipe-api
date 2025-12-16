#!/usr/bin/env python3
"""
Railway部署状态检查脚本
"""

import requests
import sys

def check_service(url, service_name):
    """检查服务状态"""
    print(f"\n🔍 检查 {service_name}: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {service_name} 运行正常")
            return True
        else:
            print(f"❌ {service_name} 返回状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name} 连接失败: {e}")
        return False

def check_cors(backend_url, frontend_url):
    """检查CORS配置"""
    print(f"\n🔍 检查CORS配置...")
    
    headers = {
        'Origin': frontend_url,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(f"{backend_url}/recommend", headers=headers, timeout=10)
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS配置正确")
            return True
        else:
            print("❌ CORS配置缺失")
            print(f"响应头: {dict(response.headers)}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Railway部署状态检查")
    print("=" * 50)
    
    # 这里需要替换为实际的Railway URL
    frontend_url = input("请输入前端URL (例: https://web-production-xxx.railway.app): ").strip()
    backend_url = input("请输入后端URL (例: https://ai-recipe-api-production-xxx.railway.app): ").strip()
    
    if not frontend_url or not backend_url:
        print("❌ 请提供有效的URL")
        sys.exit(1)
    
    # 检查服务状态
    frontend_ok = check_service(frontend_url, "前端服务")
    backend_ok = check_service(f"{backend_url}/health", "后端服务")
    
    # 检查CORS
    cors_ok = False
    if backend_ok:
        cors_ok = check_cors(backend_url, frontend_url)
    
    # 总结
    print("\n📋 检查结果:")
    print(f"前端服务: {'✅' if frontend_ok else '❌'}")
    print(f"后端服务: {'✅' if backend_ok else '❌'}")
    print(f"CORS配置: {'✅' if cors_ok else '❌'}")
    
    if frontend_ok and backend_ok and cors_ok:
        print("\n🎉 所有服务运行正常！")
    else:
        print("\n⚠️ 需要修复的问题:")
        if not frontend_ok:
            print("- 前端服务无法访问")
        if not backend_ok:
            print("- 后端服务无法访问")
        if not cors_ok:
            print("- CORS配置需要修复")
        
        print("\n💡 建议操作:")
        print("1. 检查Railway服务状态")
        print("2. 确认环境变量配置")
        print("3. 重新部署有问题的服务")

if __name__ == "__main__":
    main()