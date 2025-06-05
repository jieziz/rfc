#!/bin/bash

# =============================================================================
# 部署脚本测试工具
# 用于验证部署脚本的基本功能和语法
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo "🔍 部署脚本测试工具"
echo "===================="
echo

# 检查脚本文件是否存在
print_info "检查脚本文件..."

scripts=(
    "deploy_gitbash.sh"
    "deploy.sh"
)

for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        print_success "$script 存在"
    else
        print_error "$script 不存在"
    fi
done

echo

# 检查脚本语法（仅对bash脚本）
print_info "检查bash脚本语法..."

bash_scripts=(
    "deploy_gitbash.sh"
    "deploy.sh"
)

for script in "${bash_scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if bash -n "$script" 2>/dev/null; then
            print_success "$script 语法正确"
        else
            print_error "$script 语法错误"
            echo "错误详情："
            bash -n "$script"
        fi
    fi
done

echo

# 检查脚本权限
print_info "检查脚本权限..."

for script in "${bash_scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            print_success "$script 有执行权限"
        else
            print_warning "$script 没有执行权限"
            echo "  修复命令: chmod +x $script"
        fi
    fi
done

echo

# 检查必要工具
print_info "检查系统必要工具..."

tools=(
    "git"
    "python"
    "pip"
)

for tool in "${tools[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        version=$($tool --version 2>/dev/null | head -n1)
        print_success "$tool 已安装: $version"
    else
        print_warning "$tool 未安装"
    fi
done

# 检查python3和pip3
if command -v python3 >/dev/null 2>&1; then
    version=$(python3 --version 2>/dev/null)
    print_success "python3 已安装: $version"
else
    print_warning "python3 未安装"
fi

if command -v pip3 >/dev/null 2>&1; then
    version=$(pip3 --version 2>/dev/null | head -n1)
    print_success "pip3 已安装: $version"
else
    print_warning "pip3 未安装"
fi

echo

# 检查网络连接
print_info "检查网络连接..."

if ping -c 1 github.com >/dev/null 2>&1; then
    print_success "GitHub 连接正常"
else
    print_warning "GitHub 连接失败，可能影响代码下载"
fi

echo

# 显示使用建议
print_info "使用建议："
echo "1. 确保所有必要工具已安装"
echo "2. 给bash脚本添加执行权限: chmod +x deploy_gitbash.sh"
echo "3. 运行部署脚本: ./deploy_gitbash.sh"
echo "4. 按提示输入配置信息"
echo

print_success "测试完成！"
