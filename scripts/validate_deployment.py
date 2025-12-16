#!/usr/bin/env python3
"""
部署验证脚本
自动化验证部署后的前后端连接和功能完整性

用法:
    python scripts/validate_deployment.py --backend-url https://your-backend.railway.app
    python scripts/validate_deployment.py --frontend-url https://your-frontend.railway.app --backend-url https://your-backend.railway.app
    python scripts/validate_deployment.py --config-file deployment_config.json
"""

import argparse
import json
import sys
import time
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin
import concurrent.futures


@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    success: bool
    duration_ms: int
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class DeploymentReport:
    """部署验证报告"""
    timestamp: str
    backend_url: str
    frontend_url: Optional[str]
    overall_success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[TestResult]
    recommendations: List[str]


class DeploymentValidator:
    """部署验证器"""
    
    def __init__(self, backend_url: str, frontend_url: Optional[str] = None, timeout: int = 30):
        self.backend_url = backend_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/') if frontend_url else None
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'DeploymentValidator/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def run_test(self, test_name: str, test_func) -> TestResult:
        """运行单个测试并记录结果"""
        print(f"🔍 Running: {test_name}")
        start_time = time.time()
        
        try:
            success, message, details = test_func()
            duration_ms = int((time.time() - start_time) * 1000)
            
            result = TestResult(
                name=test_name,
                success=success,
                duration_ms=duration_ms,
                message=message,
                details=details
            )
            
            status = "✅" if success else "❌"
            print(f"  {status} {message} ({duration_ms}ms)")
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            result = TestResult(
                name=test_name,
                success=False,
                duration_ms=duration_ms,
                message=f"Test failed with exception",
                error=str(e)
            )
            print(f"  ❌ Exception: {str(e)} ({duration_ms}ms)")
            return result
    
    def test_backend_health(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试后端健康检查"""
        try:
            response = self.session.get(f"{self.backend_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                return True, f"Backend health check passed", {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "health_data": health_data
                }
            else:
                return False, f"Health check failed with status {response.status_code}", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200]
                }
        except requests.RequestException as e:
            return False, f"Health check request failed: {str(e)}", {"error": str(e)}
    
    def test_backend_root_endpoint(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试后端根端点"""
        try:
            response = self.session.get(f"{self.backend_url}/")
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "AI食谱API服务正常"
                if data.get("message") == expected_message:
                    return True, "Root endpoint working correctly", {
                        "status_code": response.status_code,
                        "message": data.get("message")
                    }
                else:
                    return False, f"Unexpected message: {data.get('message')}", {
                        "status_code": response.status_code,
                        "actual_message": data.get("message"),
                        "expected_message": expected_message
                    }
            else:
                return False, f"Root endpoint failed with status {response.status_code}", {
                    "status_code": response.status_code
                }
        except requests.RequestException as e:
            return False, f"Root endpoint request failed: {str(e)}", {"error": str(e)}
    
    def test_recipe_recommendation_api(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试食谱推荐API"""
        try:
            test_data = {
                "ingredients": ["番茄", "鸡蛋"],
                "tags": []
            }
            
            response = self.session.post(f"{self.backend_url}/recommend", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证响应格式
                required_fields = ["user_ingredients", "recommendations", "total"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    return False, f"Missing required fields: {missing_fields}", {
                        "status_code": response.status_code,
                        "missing_fields": missing_fields,
                        "response_keys": list(data.keys())
                    }
                
                recommendations = data.get("recommendations", [])
                return True, f"Recipe API working, returned {len(recommendations)} recipes", {
                    "status_code": response.status_code,
                    "recipe_count": len(recommendations),
                    "test_ingredients": test_data["ingredients"],
                    "sample_recipe": recommendations[0] if recommendations else None
                }
            else:
                return False, f"Recipe API failed with status {response.status_code}", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200]
                }
        except requests.RequestException as e:
            return False, f"Recipe API request failed: {str(e)}", {"error": str(e)}
    
    def test_user_registration_api(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试用户注册API"""
        try:
            # 使用时间戳确保唯一性
            timestamp = str(int(time.time()))
            test_data = {
                "username": f"test_deploy_user_{timestamp}",
                "email": f"test_deploy_{timestamp}@example.com",
                "password": "test_password_123"
            }
            
            response = self.session.post(f"{self.backend_url}/register", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user_id" in data:
                    return True, "User registration API working", {
                        "status_code": response.status_code,
                        "user_id": data.get("user_id"),
                        "message": data.get("message")
                    }
                else:
                    return False, "Registration response missing user_id", {
                        "status_code": response.status_code,
                        "response": data
                    }
            else:
                return False, f"Registration failed with status {response.status_code}", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200]
                }
        except requests.RequestException as e:
            return False, f"Registration API request failed: {str(e)}", {"error": str(e)}
    
    def test_user_login_api(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试用户登录API（需要先创建用户）"""
        try:
            # 先创建一个测试用户
            timestamp = str(int(time.time()))
            test_user = {
                "username": f"test_login_user_{timestamp}",
                "email": f"test_login_{timestamp}@example.com",
                "password": "login_test_password"
            }
            
            # 注册用户
            reg_response = self.session.post(f"{self.backend_url}/register", json=test_user)
            if reg_response.status_code != 200:
                return False, "Failed to create test user for login test", {
                    "registration_status": reg_response.status_code
                }
            
            # 尝试登录
            login_data = {
                "username": test_user["username"],
                "password": test_user["password"]
            }
            
            login_response = self.session.post(f"{self.backend_url}/login", json=login_data)
            
            if login_response.status_code == 200:
                data = login_response.json()
                if "access_token" in data and "token_type" in data:
                    return True, "User login API working", {
                        "status_code": login_response.status_code,
                        "token_type": data.get("token_type"),
                        "has_access_token": bool(data.get("access_token"))
                    }
                else:
                    return False, "Login response missing token fields", {
                        "status_code": login_response.status_code,
                        "response": data
                    }
            else:
                return False, f"Login failed with status {login_response.status_code}", {
                    "status_code": login_response.status_code,
                    "response_text": login_response.text[:200]
                }
        except requests.RequestException as e:
            return False, f"Login API request failed: {str(e)}", {"error": str(e)}
    
    def test_cors_configuration(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试CORS配置"""
        try:
            # 发送OPTIONS请求测试CORS
            headers = {
                'Origin': 'https://example.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = self.session.options(f"{self.backend_url}/recommend", headers=headers)
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
            }
            
            # 检查是否有CORS头部
            has_cors_headers = any(cors_headers.values())
            
            if has_cors_headers:
                return True, "CORS headers present", {
                    "status_code": response.status_code,
                    "cors_headers": cors_headers
                }
            else:
                return False, "No CORS headers found", {
                    "status_code": response.status_code,
                    "all_headers": dict(response.headers)
                }
        except requests.RequestException as e:
            return False, f"CORS test request failed: {str(e)}", {"error": str(e)}
    
    def test_frontend_accessibility(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试前端可访问性（如果提供了前端URL）"""
        if not self.frontend_url:
            return True, "Frontend URL not provided, skipping test", {}
        
        try:
            response = self.session.get(self.frontend_url)
            
            if response.status_code == 200:
                # 检查是否是HTML内容
                content_type = response.headers.get('content-type', '').lower()
                if 'html' in content_type:
                    return True, "Frontend accessible and serving HTML", {
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "content_length": len(response.content)
                    }
                else:
                    return False, f"Frontend not serving HTML content: {content_type}", {
                        "status_code": response.status_code,
                        "content_type": content_type
                    }
            else:
                return False, f"Frontend not accessible, status: {response.status_code}", {
                    "status_code": response.status_code
                }
        except requests.RequestException as e:
            return False, f"Frontend accessibility test failed: {str(e)}", {"error": str(e)}
    
    def test_configuration_endpoints(self) -> tuple[bool, str, Dict[str, Any]]:
        """测试配置相关端点"""
        try:
            # 测试配置状态端点
            response = self.session.get(f"{self.backend_url}/config/status")
            
            if response.status_code == 200:
                config_data = response.json()
                return True, "Configuration endpoints working", {
                    "status_code": response.status_code,
                    "config_status": config_data
                }
            else:
                return False, f"Config status endpoint failed: {response.status_code}", {
                    "status_code": response.status_code
                }
        except requests.RequestException as e:
            return False, f"Configuration endpoint test failed: {str(e)}", {"error": str(e)}
    
    def run_all_tests(self) -> DeploymentReport:
        """运行所有部署验证测试"""
        print("🚀 Starting Deployment Validation")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        if self.frontend_url:
            print(f"Frontend URL: {self.frontend_url}")
        print("=" * 60)
        
        # 定义所有测试
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Backend Root Endpoint", self.test_backend_root_endpoint),
            ("Recipe Recommendation API", self.test_recipe_recommendation_api),
            ("User Registration API", self.test_user_registration_api),
            ("User Login API", self.test_user_login_api),
            ("CORS Configuration", self.test_cors_configuration),
            ("Configuration Endpoints", self.test_configuration_endpoints),
            ("Frontend Accessibility", self.test_frontend_accessibility),
        ]
        
        results = []
        
        # 运行测试
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append(result)
        
        # 计算统计信息
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = len(results) - passed_tests
        overall_success = failed_tests == 0
        
        # 生成建议
        recommendations = self._generate_recommendations(results)
        
        # 创建报告
        report = DeploymentReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            backend_url=self.backend_url,
            frontend_url=self.frontend_url,
            overall_success=overall_success,
            total_tests=len(results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            results=results,
            recommendations=recommendations
        )
        
        return report
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """根据测试结果生成建议"""
        recommendations = []
        
        failed_results = [r for r in results if not r.success]
        
        if not failed_results:
            recommendations.append("🎉 所有测试都通过了！部署看起来很健康。")
            return recommendations
        
        # 分析失败的测试并提供建议
        for result in failed_results:
            if "Health Check" in result.name:
                recommendations.append("❌ 后端健康检查失败 - 检查服务是否正在运行")
            elif "Root Endpoint" in result.name:
                recommendations.append("❌ 后端根端点失败 - 检查API服务配置")
            elif "Recipe" in result.name:
                recommendations.append("❌ 食谱API失败 - 检查数据库连接和业务逻辑")
            elif "Registration" in result.name:
                recommendations.append("❌ 用户注册失败 - 检查数据库和认证配置")
            elif "Login" in result.name:
                recommendations.append("❌ 用户登录失败 - 检查认证系统")
            elif "CORS" in result.name:
                recommendations.append("❌ CORS配置问题 - 检查环境变量CORS_ORIGINS")
            elif "Frontend" in result.name:
                recommendations.append("❌ 前端访问失败 - 检查前端服务部署")
            elif "Configuration" in result.name:
                recommendations.append("❌ 配置端点失败 - 检查环境变量管理")
        
        # 通用建议
        if len(failed_results) > len(results) // 2:
            recommendations.append("⚠️  多个测试失败，建议检查整体部署配置")
        
        recommendations.append("💡 查看详细的测试结果以获取更多诊断信息")
        
        return recommendations


def print_report(report: DeploymentReport, verbose: bool = False):
    """打印部署验证报告"""
    print("\n" + "=" * 60)
    print("📋 DEPLOYMENT VALIDATION REPORT")
    print("=" * 60)
    print(f"Timestamp: {report.timestamp}")
    print(f"Backend URL: {report.backend_url}")
    if report.frontend_url:
        print(f"Frontend URL: {report.frontend_url}")
    print(f"Overall Status: {'✅ SUCCESS' if report.overall_success else '❌ FAILURE'}")
    print(f"Tests: {report.passed_tests}/{report.total_tests} passed")
    
    if verbose or not report.overall_success:
        print("\n📊 Test Results:")
        print("-" * 40)
        for result in report.results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.name}")
            print(f"   {result.message} ({result.duration_ms}ms)")
            if result.error:
                print(f"   Error: {result.error}")
            if verbose and result.details:
                print(f"   Details: {json.dumps(result.details, indent=2)}")
    
    if report.recommendations:
        print("\n💡 Recommendations:")
        print("-" * 40)
        for rec in report.recommendations:
            print(f"  {rec}")
    
    print("\n" + "=" * 60)


def save_report(report: DeploymentReport, filename: str):
    """保存报告到JSON文件"""
    report_dict = asdict(report)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)
    print(f"📄 Report saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description='Validate deployment of frontend-backend application')
    parser.add_argument('--backend-url', required=True, help='Backend service URL')
    parser.add_argument('--frontend-url', help='Frontend service URL (optional)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', help='Save report to JSON file')
    parser.add_argument('--config-file', help='Load configuration from JSON file')
    
    args = parser.parse_args()
    
    # 如果提供了配置文件，从文件加载配置
    if args.config_file:
        try:
            with open(args.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            backend_url = config.get('backend_url', args.backend_url)
            frontend_url = config.get('frontend_url', args.frontend_url)
            timeout = config.get('timeout', args.timeout)
        except Exception as e:
            print(f"❌ Failed to load config file: {e}")
            sys.exit(1)
    else:
        backend_url = args.backend_url
        frontend_url = args.frontend_url
        timeout = args.timeout
    
    # 创建验证器并运行测试
    validator = DeploymentValidator(backend_url, frontend_url, timeout)
    report = validator.run_all_tests()
    
    # 打印报告
    print_report(report, args.verbose)
    
    # 保存报告（如果指定了输出文件）
    if args.output:
        save_report(report, args.output)
    
    # 设置退出码
    sys.exit(0 if report.overall_success else 1)


if __name__ == "__main__":
    main()