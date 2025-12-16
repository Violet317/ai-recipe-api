#!/bin/bash
# 部署验证脚本包装器
# 简化部署验证的使用

set -e

# 默认配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/validate_deployment.py"
CONFIG_FILE="$SCRIPT_DIR/deployment_config.json"
REPORT_FILE="deployment_validation_$(date +%Y%m%d_%H%M%S).json"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "部署验证脚本"
    echo ""
    echo "用法:"
    echo "  $0 --backend-url <URL>                    # 只验证后端"
    echo "  $0 --backend-url <URL> --frontend-url <URL>  # 验证前后端"
    echo "  $0 --config-file <FILE>                   # 使用配置文件"
    echo "  $0 --help                                 # 显示帮助"
    echo ""
    echo "选项:"
    echo "  --backend-url URL     后端服务URL"
    echo "  --frontend-url URL    前端服务URL（可选）"
    echo "  --config-file FILE    配置文件路径"
    echo "  --timeout SECONDS     请求超时时间（默认30秒）"
    echo "  --verbose             详细输出"
    echo "  --output FILE         保存报告到文件"
    echo "  --help                显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --backend-url https://my-api.railway.app"
    echo "  $0 --config-file deployment_config.json --verbose"
}

# 检查Python是否可用
check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python not found. Please install Python 3.6+${NC}"
        exit 1
    fi
    
    # 优先使用python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 Checking dependencies...${NC}"
    
    # 检查requests库
    if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Installing requests library...${NC}"
        $PYTHON_CMD -m pip install requests
    fi
    
    echo -e "${GREEN}✅ Dependencies OK${NC}"
}

# 运行验证
run_validation() {
    echo -e "${BLUE}🚀 Starting deployment validation...${NC}"
    echo ""
    
    # 构建Python命令
    cmd="$PYTHON_CMD $PYTHON_SCRIPT"
    
    # 添加参数
    for arg in "$@"; do
        cmd="$cmd \"$arg\""
    done
    
    # 执行验证
    if eval $cmd; then
        echo ""
        echo -e "${GREEN}🎉 Deployment validation completed successfully!${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Deployment validation failed. Please check the issues above.${NC}"
        return 1
    fi
}

# 主函数
main() {
    # 检查是否有参数
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    # 处理帮助参数
    for arg in "$@"; do
        if [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
            show_help
            exit 0
        fi
    done
    
    # 检查环境
    check_python
    check_dependencies
    
    # 运行验证
    run_validation "$@"
}

# 执行主函数
main "$@"