# env_manager.py - 环境变量管理和验证系统
import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json


class ConfigStatus(Enum):
    """配置状态枚举"""
    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"
    WARNING = "warning"


@dataclass
class ConfigItem:
    """配置项数据类"""
    name: str
    value: Optional[str]
    status: ConfigStatus
    message: str
    required: bool = True


@dataclass
class ConfigReport:
    """配置状态报告"""
    items: List[ConfigItem]
    overall_status: ConfigStatus
    summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "items": [
                {
                    "name": item.name,
                    "value": item.value,
                    "status": item.status.value,
                    "message": item.message,
                    "required": item.required
                }
                for item in self.items
            ],
            "overall_status": self.overall_status.value,
            "summary": self.summary
        }


class EnvironmentManager:
    """环境变量管理器"""
    
    # 必需的环境变量配置
    REQUIRED_VARS = {
        "SECRET_KEY": {
            "description": "JWT密钥",
            "validator": lambda x: len(x) >= 32,
            "error_msg": "SECRET_KEY必须至少32个字符"
        },
        "CORS_ORIGINS": {
            "description": "CORS允许的源",
            "validator": lambda x: EnvironmentManager._validate_cors_origins(x),
            "error_msg": "CORS_ORIGINS格式无效，应为逗号分隔的URL列表"
        }
    }
    
    # 可选的环境变量配置
    OPTIONAL_VARS = {
        "DATABASE_URL": {
            "description": "数据库连接URL",
            "validator": lambda x: x.startswith(("sqlite://", "postgresql://", "mysql://")),
            "error_msg": "DATABASE_URL格式无效",
            "default": "sqlite:///./recipes.db"
        },
        "RAILWAY_STATIC_URL": {
            "description": "Railway静态URL",
            "validator": lambda x: x.startswith("https://"),
            "error_msg": "RAILWAY_STATIC_URL必须是HTTPS URL",
            "default": None
        }
    }
    
    @staticmethod
    def _validate_cors_origins(origins_str: str) -> bool:
        """验证CORS源格式"""
        if not origins_str:
            return False
        
        origins = [o.strip() for o in origins_str.split(",") if o.strip()]
        if not origins:
            return False
        
        # 允许 * 或有效的URL
        for origin in origins:
            if origin == "*":
                continue
            if not re.match(r'^https?://[a-zA-Z0-9.-]+(?::\d+)?$', origin):
                return False
        
        return True
    
    @staticmethod
    def _validate_url(url: str) -> bool:
        """验证URL格式"""
        url_pattern = re.compile(
            r'^https?://'  # http:// 或 https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
            r'(?::\d+)?'  # 可选端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def validate_environment_variables(self) -> ConfigReport:
        """验证所有环境变量"""
        items = []
        has_errors = False
        has_warnings = False
        
        # 检查必需变量
        for var_name, config in self.REQUIRED_VARS.items():
            value = os.getenv(var_name)
            
            if value is None:
                items.append(ConfigItem(
                    name=var_name,
                    value=None,
                    status=ConfigStatus.MISSING,
                    message=f"缺少必需的环境变量: {config['description']}",
                    required=True
                ))
                has_errors = True
            elif not config["validator"](value):
                items.append(ConfigItem(
                    name=var_name,
                    value=value,
                    status=ConfigStatus.INVALID,
                    message=config["error_msg"],
                    required=True
                ))
                has_errors = True
            else:
                items.append(ConfigItem(
                    name=var_name,
                    value=value,
                    status=ConfigStatus.VALID,
                    message=f"✓ {config['description']}配置正确",
                    required=True
                ))
        
        # 检查可选变量
        for var_name, config in self.OPTIONAL_VARS.items():
            value = os.getenv(var_name)
            
            if value is None:
                default_value = config.get("default")
                if default_value:
                    items.append(ConfigItem(
                        name=var_name,
                        value=default_value,
                        status=ConfigStatus.WARNING,
                        message=f"使用默认值: {default_value}",
                        required=False
                    ))
                    has_warnings = True
                else:
                    items.append(ConfigItem(
                        name=var_name,
                        value=None,
                        status=ConfigStatus.WARNING,
                        message=f"可选变量未设置: {config['description']}",
                        required=False
                    ))
                    has_warnings = True
            elif not config["validator"](value):
                items.append(ConfigItem(
                    name=var_name,
                    value=value,
                    status=ConfigStatus.INVALID,
                    message=config["error_msg"],
                    required=False
                ))
                has_warnings = True
            else:
                items.append(ConfigItem(
                    name=var_name,
                    value=value,
                    status=ConfigStatus.VALID,
                    message=f"✓ {config['description']}配置正确",
                    required=False
                ))
        
        # 确定整体状态
        if has_errors:
            overall_status = ConfigStatus.INVALID
            summary = "配置验证失败：存在必需变量缺失或无效"
        elif has_warnings:
            overall_status = ConfigStatus.WARNING
            summary = "配置基本正确，但存在警告项"
        else:
            overall_status = ConfigStatus.VALID
            summary = "所有配置项验证通过"
        
        return ConfigReport(
            items=items,
            overall_status=overall_status,
            summary=summary
        )
    
    def get_api_base_url(self) -> str:
        """获取API基础URL"""
        # 优先使用Railway提供的URL
        railway_url = os.getenv("RAILWAY_STATIC_URL")
        if railway_url:
            return railway_url
        
        # 回退到本地开发URL
        return "http://localhost:8000"
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS允许的源"""
        origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
        origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
        return origins
    
    def setup_environment_defaults(self) -> None:
        """设置环境变量默认值（如果未设置）"""
        defaults = {
            "SECRET_KEY": "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
            "CORS_ORIGINS": "http://localhost:5173",
            "DATABASE_URL": "sqlite:///./recipes.db"
        }
        
        for key, default_value in defaults.items():
            if not os.getenv(key):
                os.environ[key] = default_value
    
    def generate_config_report_json(self) -> str:
        """生成JSON格式的配置报告"""
        report = self.validate_environment_variables()
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
    
    def print_config_status(self) -> None:
        """打印配置状态到控制台"""
        report = self.validate_environment_variables()
        
        print("=" * 50)
        print("环境变量配置状态报告")
        print("=" * 50)
        print(f"整体状态: {report.overall_status.value.upper()}")
        print(f"摘要: {report.summary}")
        print()
        
        # 按状态分组显示
        for status in [ConfigStatus.INVALID, ConfigStatus.MISSING, ConfigStatus.WARNING, ConfigStatus.VALID]:
            status_items = [item for item in report.items if item.status == status]
            if status_items:
                print(f"{status.value.upper()} 项目:")
                for item in status_items:
                    required_mark = "[必需]" if item.required else "[可选]"
                    print(f"  {required_mark} {item.name}: {item.message}")
                print()


# 全局环境管理器实例
env_manager = EnvironmentManager()


def validate_environment() -> ConfigReport:
    """验证环境变量的便捷函数"""
    return env_manager.validate_environment_variables()


def get_config_status() -> Dict[str, Any]:
    """获取配置状态的便捷函数"""
    report = env_manager.validate_environment_variables()
    return report.to_dict()


if __name__ == "__main__":
    # 测试环境变量管理器
    manager = EnvironmentManager()
    manager.print_config_status()