#!/bin/bash

# =============================================================================
# RFC Auto Grabber - 二进制版本一键安装脚本
# 下载编译后的二进制文件，保护源码不被泄露
# 使用方法: bash <(curl -Ls https://your-domain.com/install_binary.sh)
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_step() { echo -e "${PURPLE}🔄 $1${NC}"; }

# 项目信息
PROJECT_NAME="RFC Auto Grabber"
VERSION="1.0.0"
# 请将此URL替换为您的实际下载地址
BINARY_DOWNLOAD_URL="https://github.com/jieziz/rfc/releases/download/v${VERSION}/rfc-auto-grabber-v${VERSION}.zip"
INSTALL_DIR="$HOME/rfc-auto-grabber"

# 显示欢迎信息
show_welcome() {
    echo "
╔══════════════════════════════════════════════════════════════╗
║                    🚀 RFC Auto Grabber                      ║
║                     二进制版本安装器                          ║
║                                                              ║
║  ✨ 特点:                                                    ║
║  • 🔒 源码保护 - 编译后的二进制文件                          ║
║  • 🚀 一键安装 - 无需Python环境                             ║
║  • 🎯 开箱即用 - 配置即可使用                               ║
║  • 🛡️ 安全可靠 - 无法查看源代码                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"
}

# 检查系统环境
check_system() {
    print_step "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        BINARY_NAME="rfc-grabber"
        print_success "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        BINARY_NAME="rfc-grabber.exe"
        print_success "检测到 Windows 系统 (Git Bash)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        BINARY_NAME="rfc-grabber"
        print_success "检测到 macOS 系统"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查必要工具
    local missing_tools=()
    
    if ! command -v curl >/dev/null 2>&1; then
        missing_tools+=("curl")
    fi
    
    if ! command -v unzip >/dev/null 2>&1; then
        missing_tools+=("unzip")
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
        read -p "是否覆盖安装？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "安装已取消"
            exit 0
        fi
        rm -rf "$INSTALL_DIR"
    fi
    
    mkdir -p "$INSTALL_DIR"
    print_success "安装目录创建完成: $INSTALL_DIR"
}

# 下载二进制文件
download_binary() {
    print_step "下载二进制文件..."
    
    local temp_file="/tmp/rfc-auto-grabber.zip"
    
    print_info "下载地址: $BINARY_DOWNLOAD_URL"
    
    if curl -fsSL "$BINARY_DOWNLOAD_URL" -o "$temp_file"; then
        print_success "二进制文件下载完成"
    else
        print_error "二进制文件下载失败"
        print_info "请检查网络连接或联系技术支持"
        exit 1
    fi
    
    # 解压文件
    print_step "解压安装文件..."
    cd "$INSTALL_DIR"
    
    if unzip -q "$temp_file"; then
        print_success "文件解压完成"
        rm -f "$temp_file"
    else
        print_error "文件解压失败"
        exit 1
    fi
    
    # 设置执行权限
    if [[ "$OS" != "windows" ]]; then
        chmod +x "$BINARY_NAME" 2>/dev/null || true
        chmod +x "fast-grabber" 2>/dev/null || true
        chmod +x "stable-grabber" 2>/dev/null || true
        chmod +x "concurrent-grabber" 2>/dev/null || true
        chmod +x "start.sh" 2>/dev/null || true
        print_success "执行权限设置完成"
    else
        print_info "Windows环境，跳过权限设置"
    fi
}

# 配置向导
configure_application() {
    print_step "配置应用程序..."
    
    cd "$INSTALL_DIR"
    
    if [[ ! -f ".env.template" ]]; then
        print_error "配置模板文件不存在"
        exit 1
    fi
    
    echo
    print_info "请输入以下信息来配置抢购脚本："
    echo
    
    # 输入邮箱
    while true; do
        read -p "请输入您的邮箱账号: " USER_EMAIL
        if [[ -n "$USER_EMAIL" && "$USER_EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            break
        else
            print_error "请输入有效的邮箱地址"
        fi
    done
    
    # 输入密码
    while true; do
        read -s -p "请输入您的密码: " USER_PASSWORD
        echo
        if [[ -n "$USER_PASSWORD" ]]; then
            read -s -p "请再次确认密码: " USER_PASSWORD_CONFIRM
            echo
            if [[ "$USER_PASSWORD" == "$USER_PASSWORD_CONFIRM" ]]; then
                break
            else
                print_error "两次输入的密码不一致，请重新输入"
            fi
        else
            print_error "密码不能为空"
        fi
    done
    
    # 输入商品PID
    while true; do
        read -p "请输入要抢购的商品PID: " PRODUCT_PID
        if [[ -n "$PRODUCT_PID" && "$PRODUCT_PID" =~ ^[0-9]+$ ]]; then
            break
        else
            print_error "请输入有效的数字PID"
        fi
    done
    
    # 生成配置文件
    cp ".env.template" ".env"
    
    # 替换配置值
    if [[ "$OS" == "macos" ]]; then
        sed -i '' "s/your_email@example.com/$USER_EMAIL/g" ".env"
        sed -i '' "s/your_password/$USER_PASSWORD/g" ".env"
        sed -i '' "s/YOUR_PID/$PRODUCT_PID/g" ".env"
    else
        sed -i "s/your_email@example.com/$USER_EMAIL/g" ".env"
        sed -i "s/your_password/$USER_PASSWORD/g" ".env"
        sed -i "s/YOUR_PID/$PRODUCT_PID/g" ".env"
    fi
    
    print_success "配置文件生成完成"
}

# 显示完成信息
show_completion() {
    echo
    print_success "🎉 安装完成！"
    echo
    print_info "安装位置: $INSTALL_DIR"
    echo
    print_step "启动方法："
    
    if [[ "$OS" == "windows" ]]; then
        echo "  方式1: 双击 start.bat"
        echo "  方式2: 在Git Bash中运行 ./start.sh"
        echo "  方式3: 直接运行 ./$BINARY_NAME"
    else
        echo "  方式1: 运行 ./start.sh"
        echo "  方式2: 直接运行 ./$BINARY_NAME"
    fi
    
    echo
    print_step "可用程序："
    echo "  • $BINARY_NAME - 主程序 (交互式界面)"
    echo "  • fast-grabber - 快速模式"
    echo "  • stable-grabber - 稳定模式"
    echo "  • concurrent-grabber - 并发模式"
    echo
    print_warning "⚠️  源码已被保护，无法查看Python代码"
    print_info "📖 详细说明请查看 README.txt"
    echo
    
    # 询问是否立即启动
    read -p "是否立即启动程序？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "启动程序..."
        if [[ "$OS" == "windows" ]]; then
            cmd //c "start.bat"
        else
            ./start.sh
        fi
    fi
}

# 错误处理
handle_error() {
    print_error "安装过程中发生错误"
    print_info "请检查网络连接和系统权限"
    print_info "如需帮助，请联系技术支持"
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
    download_binary
    configure_application
    show_completion
}

# 运行主函数
main "$@"
