#!/usr/bin/env python3
# test_env_manager.py - 环境变量管理器测试
"""
环境变量管理器的测试脚本

运行方式:
    python test_env_manager.py
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from env_manager import EnvironmentManager, ConfigStatus, ConfigReport


class TestEnvironmentManager(unittest.TestCase):
    """环境变量管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = EnvironmentManager()
        # 保存原始环境变量
        self.original_env = dict(os.environ)
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境变量
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_validate_cors_origins_valid(self):
        """测试有效的CORS源验证"""
        valid_origins = [
            "http://localhost:3000",
            "https://example.com",
            "http://localhost:5173,https://myapp.railway.app",
            "*"
        ]
        
        for origin in valid_origins:
            with self.subTest(origin=origin):
                self.assertTrue(
                    EnvironmentManager._validate_cors_origins(origin),
                    f"应该接受有效的CORS源: {origin}"
                )
    
    def test_validate_cors_origins_invalid(self):
        """测试无效的CORS源验证"""
        invalid_origins = [
            "",
            "invalid-url",
            "ftp://example.com",
            "http://",
            "localhost:3000"  # 缺少协议
        ]
        
        for origin in invalid_origins:
            with self.subTest(origin=origin):
                self.assertFalse(
                    EnvironmentManager._validate_cors_origins(origin),
                    f"应该拒绝无效的CORS源: {origin}"
                )
    
    def test_validate_environment_all_valid(self):
        """测试所有环境变量都有效的情况"""
        # 设置有效的环境变量（包括可选的）
        os.environ["SECRET_KEY"] = "a" * 32  # 32个字符的密钥
        os.environ["CORS_ORIGINS"] = "http://localhost:5173,https://example.com"
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        os.environ["RAILWAY_STATIC_URL"] = "https://example.railway.app"
        
        report = self.manager.validate_environment_variables()
        
        self.assertEqual(report.overall_status, ConfigStatus.VALID)
        self.assertIn("验证通过", report.summary)
        
        # 检查所有必需变量都是有效的
        required_items = [item for item in report.items if item.required]
        for item in required_items:
            self.assertEqual(item.status, ConfigStatus.VALID)
    
    def test_validate_environment_missing_required(self):
        """测试缺少必需环境变量的情况"""
        # 清除所有环境变量
        for key in list(os.environ.keys()):
            if key.startswith(("SECRET_KEY", "CORS_ORIGINS")):
                del os.environ[key]
        
        report = self.manager.validate_environment_variables()
        
        self.assertEqual(report.overall_status, ConfigStatus.INVALID)
        self.assertIn("失败", report.summary)
        
        # 检查是否正确识别缺失的变量
        missing_items = [item for item in report.items if item.status == ConfigStatus.MISSING]
        self.assertGreater(len(missing_items), 0)
    
    def test_validate_environment_invalid_format(self):
        """测试环境变量格式无效的情况"""
        # 设置格式无效的环境变量
        os.environ["SECRET_KEY"] = "short"  # 太短
        os.environ["CORS_ORIGINS"] = "invalid-url"  # 无效URL
        
        report = self.manager.validate_environment_variables()
        
        self.assertEqual(report.overall_status, ConfigStatus.INVALID)
        
        # 检查是否正确识别无效的变量
        invalid_items = [item for item in report.items if item.status == ConfigStatus.INVALID]
        self.assertGreater(len(invalid_items), 0)
    
    def test_get_api_base_url_railway(self):
        """测试Railway环境下的API URL获取"""
        railway_url = "https://myapp-backend.railway.app"
        os.environ["RAILWAY_STATIC_URL"] = railway_url
        
        result = self.manager.get_api_base_url()
        self.assertEqual(result, railway_url)
    
    def test_get_api_base_url_default(self):
        """测试默认API URL获取"""
        # 确保没有Railway URL
        if "RAILWAY_STATIC_URL" in os.environ:
            del os.environ["RAILWAY_STATIC_URL"]
        
        result = self.manager.get_api_base_url()
        self.assertEqual(result, "http://localhost:8000")
    
    def test_get_cors_origins(self):
        """测试CORS源获取"""
        test_origins = "http://localhost:5173,https://example.com"
        os.environ["CORS_ORIGINS"] = test_origins
        
        result = self.manager.get_cors_origins()
        expected = ["http://localhost:5173", "https://example.com"]
        self.assertEqual(result, expected)
    
    def test_get_cors_origins_default(self):
        """测试默认CORS源获取"""
        if "CORS_ORIGINS" in os.environ:
            del os.environ["CORS_ORIGINS"]
        
        result = self.manager.get_cors_origins()
        self.assertEqual(result, ["http://localhost:5173"])
    
    def test_setup_environment_defaults(self):
        """测试环境变量默认值设置"""
        # 清除相关环境变量
        keys_to_clear = ["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL"]
        for key in keys_to_clear:
            if key in os.environ:
                del os.environ[key]
        
        self.manager.setup_environment_defaults()
        
        # 检查是否设置了默认值
        self.assertIsNotNone(os.environ.get("SECRET_KEY"))
        self.assertIsNotNone(os.environ.get("CORS_ORIGINS"))
        self.assertIsNotNone(os.environ.get("DATABASE_URL"))
    
    def test_config_report_to_dict(self):
        """测试配置报告转换为字典"""
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["CORS_ORIGINS"] = "http://localhost:5173"
        
        report = self.manager.validate_environment_variables()
        report_dict = report.to_dict()
        
        # 检查字典结构
        self.assertIn("items", report_dict)
        self.assertIn("overall_status", report_dict)
        self.assertIn("summary", report_dict)
        
        # 检查items结构
        self.assertIsInstance(report_dict["items"], list)
        if report_dict["items"]:
            item = report_dict["items"][0]
            self.assertIn("name", item)
            self.assertIn("status", item)
            self.assertIn("message", item)
    
    def test_generate_config_report_json(self):
        """测试JSON格式配置报告生成"""
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["CORS_ORIGINS"] = "http://localhost:5173"
        
        json_report = self.manager.generate_config_report_json()
        
        # 检查是否是有效的JSON
        import json
        try:
            parsed = json.loads(json_report)
            self.assertIn("overall_status", parsed)
            self.assertIn("items", parsed)
        except json.JSONDecodeError:
            self.fail("生成的报告不是有效的JSON")


class TestEnvironmentManagerIntegration(unittest.TestCase):
    """环境变量管理器集成测试"""
    
    def test_real_environment_validation(self):
        """测试真实环境的验证"""
        manager = EnvironmentManager()
        
        # 这个测试使用真实的环境变量
        report = manager.validate_environment_variables()
        
        # 基本检查
        self.assertIsInstance(report, ConfigReport)
        self.assertIsInstance(report.items, list)
        self.assertIsInstance(report.overall_status, ConfigStatus)
        self.assertIsInstance(report.summary, str)
        
        # 检查是否包含必需的变量检查
        item_names = [item.name for item in report.items]
        self.assertIn("SECRET_KEY", item_names)
        self.assertIn("CORS_ORIGINS", item_names)
    
    def test_print_config_status_no_error(self):
        """测试打印配置状态不会出错"""
        manager = EnvironmentManager()
        
        # 这个测试主要确保print_config_status不会抛出异常
        try:
            manager.print_config_status()
        except Exception as e:
            self.fail(f"print_config_status抛出了异常: {e}")


def run_manual_tests():
    """运行手动测试"""
    print("🧪 运行环境变量管理器手动测试...")
    
    manager = EnvironmentManager()
    
    print("\n1. 当前环境验证:")
    manager.print_config_status()
    
    print("\n2. JSON报告:")
    json_report = manager.generate_config_report_json()
    print(json_report[:200] + "..." if len(json_report) > 200 else json_report)
    
    print("\n3. API配置:")
    print(f"API基础URL: {manager.get_api_base_url()}")
    print(f"CORS源: {manager.get_cors_origins()}")
    
    print("\n✅ 手动测试完成")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='环境变量管理器测试')
    parser.add_argument('--manual', action='store_true', help='运行手动测试')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.manual:
        run_manual_tests()
    else:
        # 运行单元测试
        if args.verbose:
            unittest.main(verbosity=2)
        else:
            unittest.main()