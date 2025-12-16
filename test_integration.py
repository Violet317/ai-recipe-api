#!/usr/bin/env python3
# test_integration.py - 环境变量管理系统集成测试
"""
集成测试脚本，验证环境变量管理系统与主应用的集成

运行方式:
    python test_integration.py
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch
import json


class TestEnvironmentIntegration(unittest.TestCase):
    """环境变量管理系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 保存原始环境变量
        self.original_env = dict(os.environ)
        
        # 设置测试环境变量
        os.environ["SECRET_KEY"] = "test_secret_key_with_sufficient_length_32chars"
        os.environ["CORS_ORIGINS"] = "http://localhost:5173,http://localhost:3000"
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境变量
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_main_app_imports_successfully(self):
        """测试主应用能够成功导入环境管理器"""
        try:
            from main import app
            from env_manager import env_manager, validate_environment
            self.assertIsNotNone(app)
            self.assertIsNotNone(env_manager)
        except ImportError as e:
            self.fail(f"导入失败: {e}")
    
    def test_environment_validation_in_main(self):
        """测试主应用中的环境验证"""
        from env_manager import validate_environment, ConfigStatus
        
        report = validate_environment()
        
        # 在有效环境变量的情况下，应该通过验证
        self.assertIn(report.overall_status, [ConfigStatus.VALID, ConfigStatus.WARNING])
    
    def test_cors_configuration_integration(self):
        """测试CORS配置集成"""
        from env_manager import env_manager
        
        origins = env_manager.get_cors_origins()
        expected_origins = ["http://localhost:5173", "http://localhost:3000"]
        
        self.assertEqual(origins, expected_origins)
    
    def test_api_base_url_configuration(self):
        """测试API基础URL配置"""
        from env_manager import env_manager
        
        # 测试默认情况
        url = env_manager.get_api_base_url()
        self.assertEqual(url, "http://localhost:8000")
        
        # 测试Railway环境
        os.environ["RAILWAY_STATIC_URL"] = "https://test.railway.app"
        url = env_manager.get_api_base_url()
        self.assertEqual(url, "https://test.railway.app")
    
    def test_health_check_endpoint_data(self):
        """测试健康检查端点数据结构"""
        from main import health_check
        
        # 调用健康检查函数
        health_data = health_check()
        
        # 验证返回数据结构
        self.assertIn("status", health_data)
        self.assertIn("service", health_data)
        self.assertIn("configuration", health_data)
        self.assertIn("api_base_url", health_data)
        self.assertIn("cors_origins", health_data)
        
        # 验证配置状态
        config = health_data["configuration"]
        self.assertIn("status", config)
        self.assertIn("summary", config)
    
    def test_config_status_endpoint_data(self):
        """测试配置状态端点数据结构"""
        from main import get_configuration_status
        
        # 调用配置状态函数
        config_data = get_configuration_status()
        
        # 验证返回数据结构
        self.assertIn("items", config_data)
        self.assertIn("overall_status", config_data)
        self.assertIn("summary", config_data)
        
        # 验证items结构
        self.assertIsInstance(config_data["items"], list)
        if config_data["items"]:
            item = config_data["items"][0]
            self.assertIn("name", item)
            self.assertIn("status", item)
            self.assertIn("message", item)
            self.assertIn("required", item)
    
    def test_validate_configuration_endpoint(self):
        """测试配置验证端点"""
        from main import validate_configuration
        
        # 调用配置验证函数
        validation_data = validate_configuration()
        
        # 验证返回数据结构
        self.assertIn("valid", validation_data)
        self.assertIn("report", validation_data)
        self.assertIn("recommendations", validation_data)
        
        # 验证数据类型
        self.assertIsInstance(validation_data["valid"], bool)
        self.assertIsInstance(validation_data["recommendations"], list)
    
    def test_environment_defaults_setup(self):
        """测试环境变量默认值设置"""
        from env_manager import env_manager
        
        # 清除环境变量
        keys_to_test = ["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL"]
        original_values = {}
        for key in keys_to_test:
            original_values[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        try:
            # 设置默认值
            env_manager.setup_environment_defaults()
            
            # 验证默认值已设置
            for key in keys_to_test:
                self.assertIsNotNone(os.environ.get(key), f"{key} 应该有默认值")
        
        finally:
            # 恢复原始值
            for key, value in original_values.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]


class TestValidationScript(unittest.TestCase):
    """验证脚本测试"""
    
    def test_validation_script_json_output(self):
        """测试验证脚本JSON输出"""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, "validate_config.py", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 验证能够生成JSON输出
            try:
                json_data = json.loads(result.stdout)
                self.assertIn("overall_status", json_data)
                self.assertIn("items", json_data)
            except json.JSONDecodeError:
                self.fail("验证脚本没有生成有效的JSON输出")
        
        except subprocess.TimeoutExpired:
            self.fail("验证脚本执行超时")
        except FileNotFoundError:
            self.skipTest("validate_config.py 文件不存在")


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行环境变量管理系统集成测试...")
    
    # 设置测试环境
    os.environ["SECRET_KEY"] = "test_secret_key_with_sufficient_length_32chars"
    os.environ["CORS_ORIGINS"] = "http://localhost:5173"
    
    try:
        # 测试基本导入
        from env_manager import env_manager, validate_environment
        from main import app, health_check
        
        print("✅ 基本导入测试通过")
        
        # 测试环境验证
        report = validate_environment()
        print(f"✅ 环境验证测试通过 - 状态: {report.overall_status.value}")
        
        # 测试健康检查
        health_data = health_check()
        print(f"✅ 健康检查测试通过 - 状态: {health_data['status']}")
        
        # 测试配置获取
        api_url = env_manager.get_api_base_url()
        cors_origins = env_manager.get_cors_origins()
        print(f"✅ 配置获取测试通过 - API: {api_url}, CORS: {cors_origins}")
        
        print("\n🎉 所有集成测试通过！")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='环境变量管理系统集成测试')
    parser.add_argument('--manual', action='store_true', help='运行手动集成测试')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.manual:
        success = run_integration_tests()
        sys.exit(0 if success else 1)
    else:
        # 运行单元测试
        if args.verbose:
            unittest.main(verbosity=2)
        else:
            unittest.main()