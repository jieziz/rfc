fix#!/bin/bash

# =============================================================================
# RFC Auto Grabber - 一键安装脚本
# 支持远程一条命令安装: bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/install.sh)
# 自动检测系统环境，下载并运行完整部署脚本
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="RFC Auto Grabber"
GITHUB_REPO="https://github.com/jieziz/rfc.git"
GITHUB_RAW_URL="https://raw.githubusercontent.com/jieziz/rfc/main"
INSTALL_DIR="$HOME/rfc-auto-grabber"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

print_success() { print_message "$GREEN" "✅ $1"; }
print_error() { print_message "$RED" "❌ $1"; }
print_warning() { print_message "$YELLOW" "⚠️  $1"; }
print_info() { print_message "$BLUE" "ℹ️  $1"; }
print_step() { print_message "$PURPLE" "🔄 $1"; }

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "=============================================="
    echo "    🚀 RFC Auto Grabber - 一键安装"
    echo "=============================================="
    echo -e "${NC}"
    echo
    print_info "🎯 专业级RFC/WHCMS自动抢购工具"
    print_info "🌐 支持多平台: Windows Git Bash、Linux、macOS"
    print_info "⚡ 极速部署: 自动安装所有依赖"
    echo
    print_step "开始一键安装流程..."
    echo
}

# 检查系统环境
check_system() {
    print_step "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "检测到 Windows 系统 (Git Bash/Cygwin)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "检测到 macOS 系统"
    else
        OS="unknown"
        print_warning "未知系统类型: $OSTYPE"
    fi
    
    # 检查必要工具
    local missing_tools=()
    
    if ! command -v curl >/dev/null 2>&1; then
        missing_tools+=("curl")
    fi
    
    if ! command -v git >/dev/null 2>&1; then
        missing_tools+=("git")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_error "缺少必要工具: ${missing_tools[*]}"
        print_info "请先安装缺少的工具后重新运行"
        exit 1
    fi
    
    print_success "系统环境检查通过"
}

# 创建安装目录
create_install_dir() {
    print_step "创建安装目录..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "安装目录已存在: $INSTALL_DIR"
        read -p "是否删除现有目录并重新安装? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
            print_info "已删除现有目录"
        else
            print_info "使用现有目录"
        fi
    fi
    
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    print_success "安装目录创建完成: $INSTALL_DIR"
}

# 下载并执行部署脚本
download_and_run() {
    print_step "下载部署脚本..."
    
    local deploy_script="$INSTALL_DIR/deploy.sh"
    
    # 下载部署脚本
    if curl -fsSL "$GITHUB_RAW_URL/scripts/deploy.sh" -o "$deploy_script"; then
        print_success "部署脚本下载完成"
    else
        print_error "部署脚本下载失败"
        print_info "请检查网络连接或手动克隆项目："
        print_info "git clone $GITHUB_REPO"
        exit 1
    fi
    
    # 给脚本执行权限
    chmod +x "$deploy_script"
    
    print_step "启动部署脚本..."
    echo
    
    # 设置环境变量标识远程安装
    export REMOTE_INSTALL=true
    export PROJECT_DIR="$INSTALL_DIR"
    
    # 执行部署脚本
    bash "$deploy_script"
}

# 显示安装完成信息
show_completion() {
    echo
    print_success "🎉 一键安装完成！"
    echo
    print_info "安装位置: $INSTALL_DIR"
    print_info "项目代码: $INSTALL_DIR/rfc_repo"
    echo
    print_step "快速启动命令："
    echo "  cd $INSTALL_DIR/rfc_repo"
    echo "  source $INSTALL_DIR/venv/bin/activate"
    echo "  python quick_start.py"
    echo
    print_step "或使用启动脚本："
    echo "  $INSTALL_DIR/start_grabber.sh"
    echo
    print_warning "⚠️  请记住安装路径，以便后续使用"
    echo
}

# 错误处理
handle_error() {
    print_error "安装过程中发生错误"
    print_info "请检查网络连接和系统权限"
    print_info "如需帮助，请访问: $GITHUB_REPO"
    exit 1
}

# 主函数
main() {
    # 设置错误处理
    trap handle_error ERR
    
    # 执行安装步骤
    show_welcome
    check_system
    create_install_dir
    download_and_run
    show_completion
}

# 运行主函数
main "$@"
