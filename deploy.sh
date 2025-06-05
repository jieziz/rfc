#!/bin/bash

# =============================================================================
# WHCMS Auto Grabber - Linux Debian 一键部署脚本
# 支持 Debian/Ubuntu 系统的自动化部署和启动
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
PROJECT_NAME="WHCMS Auto Grabber"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_VERSION="3.8"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/deploy.log"

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

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "检测到root用户，建议使用普通用户运行此脚本"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统类型
check_system() {
    print_step "检查系统环境..."
    
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        print_success "检测到 Debian/Ubuntu 系统"
    else
        print_error "此脚本仅支持 Debian/Ubuntu 系统"
        exit 1
    fi
    
    # 检查架构
    ARCH=$(uname -m)
    print_info "系统架构: $ARCH"
    
    log "系统检查完成: $OS, $ARCH"
}

# 更新系统包
update_system() {
    print_step "更新系统包列表..."
    
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq
        print_success "系统包列表更新完成"
    else
        print_error "未找到 apt-get 包管理器"
        exit 1
    fi
    
    log "系统包更新完成"
}

# 安装系统依赖
install_system_dependencies() {
    print_step "安装系统依赖包..."
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "wget"
        "curl"
        "unzip"
        "xvfb"
        "fonts-liberation"
        "libasound2"
        "libatk-bridge2.0-0"
        "libdrm2"
        "libxcomposite1"
        "libxdamage1"
        "libxrandr2"
        "libgbm1"
        "libxss1"
        "libnss3"
        "libgconf-2-4"
    )
    
    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_info "安装 $package..."
            sudo apt-get install -y "$package" >/dev/null 2>&1
        else
            print_info "$package 已安装"
        fi
    done
    
    print_success "系统依赖安装完成"
    log "系统依赖安装完成"
}

# 安装 Google Chrome
install_chrome() {
    print_step "安装 Google Chrome..."
    
    if command -v google-chrome >/dev/null 2>&1; then
        print_info "Google Chrome 已安装"
        return
    fi
    
    # 下载并安装 Chrome
    cd /tmp
    wget -q -O google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
    
    # 验证安装
    if command -v google-chrome >/dev/null 2>&1; then
        print_success "Google Chrome 安装成功"
        google-chrome --version
    else
        print_error "Google Chrome 安装失败"
        exit 1
    fi
    
    log "Google Chrome 安装完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    print_step "创建Python虚拟环境..."
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "虚拟环境已存在，是否重新创建？"
        read -p "(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "使用现有虚拟环境"
            return
        fi
    fi
    
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    # 升级pip
    pip install --upgrade pip >/dev/null 2>&1
    
    print_success "Python虚拟环境创建完成"
    log "Python虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    print_step "安装Python依赖包..."
    
    source "$VENV_DIR/bin/activate"
    
    # 创建requirements.txt如果不存在
    if [[ ! -f "$PROJECT_DIR/requirements.txt" ]]; then
        cat > "$PROJECT_DIR/requirements.txt" << EOF
DrissionPage>=4.0.0
python-dotenv>=1.0.0
selenium>=4.0.0
requests>=2.28.0
EOF
    fi
    
    # 安装依赖
    pip install -r "$PROJECT_DIR/requirements.txt"
    
    print_success "Python依赖安装完成"
    log "Python依赖安装完成"
}

# 配置环境文件
setup_environment() {
    print_step "配置环境文件..."
    
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        print_warning ".env 文件不存在，创建示例配置文件"
        
        cat > "$PROJECT_DIR/.env.example" << EOF
# 基础配置
BASE_URL=https://my.rfchost.com
LOGIN_URL=https://my.rfchost.com/clientarea.php
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229

# 登录信息
EMAIL=your_email@example.com
PASSWORD=your_password

# 性能配置
HEADLESS_MODE=True
DELAY_TIME=0.3
ELEMENT_TIMEOUT=2
PAGE_LOAD_TIMEOUT=10
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3
FAST_MODE=True
QUICK_PURCHASE=True

# 可选配置
PROMO_CODE=
TG_BOT_TOKEN=
TG_CHAT_ID=
EOF
        
        print_warning "请复制 .env.example 为 .env 并填写您的配置信息"
        print_info "配置文件位置: $PROJECT_DIR/.env.example"
    else
        print_success "环境配置文件已存在"
    fi
    
    log "环境配置完成"
}

# 创建启动脚本
create_startup_scripts() {
    print_step "创建启动脚本..."
    
    # 创建主启动脚本
    cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/bin/bash

# WHCMS Auto Grabber 启动脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查虚拟环境
if [[ ! -d "$VENV_DIR" ]]; then
    print_error "虚拟环境不存在，请先运行部署脚本"
    exit 1
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 检查配置文件
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    print_error "配置文件 .env 不存在"
    print_warning "请复制 .env.example 为 .env 并填写配置信息"
    exit 1
fi

# 启动应用
print_success "启动 WHCMS Auto Grabber..."
cd "$PROJECT_DIR"

# 检查是否有显示服务器
if [[ -z "$DISPLAY" ]]; then
    print_warning "未检测到显示服务器，使用虚拟显示"
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    sleep 2
fi

# 运行快速启动脚本
python quick_start.py

# 清理
if [[ -n "$XVFB_PID" ]]; then
    kill $XVFB_PID 2>/dev/null || true
fi
EOF
    
    chmod +x "$PROJECT_DIR/start.sh"
    
    # 创建后台运行脚本
    cat > "$PROJECT_DIR/start_daemon.sh" << 'EOF'
#!/bin/bash

# WHCMS Auto Grabber 后台运行脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PID_FILE="$PROJECT_DIR/grabber.pid"
LOG_FILE="$PROJECT_DIR/grabber_daemon.log"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

start_daemon() {
    if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        print_warning "服务已在运行中 (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_success "启动后台服务..."
    
    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"
    
    # 设置虚拟显示
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    sleep 2
    
    # 启动应用
    cd "$PROJECT_DIR"
    nohup python simple_fast_grabber.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    print_success "服务已启动 (PID: $(cat "$PID_FILE"))"
    print_success "日志文件: $LOG_FILE"
}

stop_daemon() {
    if [[ ! -f "$PID_FILE" ]]; then
        print_warning "服务未运行"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        print_success "停止服务 (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        
        # 停止虚拟显示
        pkill -f "Xvfb :99" 2>/dev/null || true
        
        print_success "服务已停止"
    else
        print_warning "服务进程不存在"
        rm -f "$PID_FILE"
    fi
}

status_daemon() {
    if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        print_success "服务正在运行 (PID: $(cat "$PID_FILE"))"
        return 0
    else
        print_warning "服务未运行"
        return 1
    fi
}

case "$1" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    status)
        status_daemon
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
EOF
    
    chmod +x "$PROJECT_DIR/start_daemon.sh"
    
    print_success "启动脚本创建完成"
    log "启动脚本创建完成"
}

# 创建systemd服务文件
create_systemd_service() {
    print_step "创建systemd服务文件..."

    local service_file="/etc/systemd/system/whcms-grabber.service"
    local current_user=$(whoami)

    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=WHCMS Auto Grabber Service
After=network.target

[Service]
Type=forking
User=$current_user
WorkingDirectory=$PROJECT_DIR
Environment=DISPLAY=:99
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1024x768x24
ExecStart=$PROJECT_DIR/start_daemon.sh start
ExecStop=$PROJECT_DIR/start_daemon.sh stop
ExecReload=$PROJECT_DIR/start_daemon.sh restart
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    print_success "systemd服务文件创建完成"
    print_info "服务名称: whcms-grabber"
    print_info "启动服务: sudo systemctl start whcms-grabber"
    print_info "开机自启: sudo systemctl enable whcms-grabber"

    log "systemd服务创建完成"
}

# 创建requirements.txt文件
create_requirements() {
    print_step "创建Python依赖文件..."

    cat > "$PROJECT_DIR/requirements.txt" << EOF
# 核心依赖
DrissionPage>=4.0.0
python-dotenv>=1.0.0
selenium>=4.15.0

# 网络请求
requests>=2.31.0
urllib3>=2.0.0

# 数据处理
typing-extensions>=4.8.0

# 日志和监控
colorlog>=6.7.0

# 可选依赖 (Telegram通知)
python-telegram-bot>=20.0
EOF

    print_success "requirements.txt 创建完成"
    log "requirements.txt 创建完成"
}

# 运行测试
run_tests() {
    print_step "运行系统测试..."

    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"

    # 测试Python环境
    print_info "测试Python环境..."
    python3 -c "import sys; print(f'Python版本: {sys.version}')"

    # 测试依赖包
    print_info "测试依赖包..."
    python3 -c "
try:
    import DrissionPage
    print('✅ DrissionPage 导入成功')
except ImportError as e:
    print(f'❌ DrissionPage 导入失败: {e}')

try:
    from dotenv import load_dotenv
    print('✅ python-dotenv 导入成功')
except ImportError as e:
    print(f'❌ python-dotenv 导入失败: {e}')

try:
    import selenium
    print('✅ selenium 导入成功')
except ImportError as e:
    print(f'❌ selenium 导入失败: {e}')
"

    # 测试Chrome
    print_info "测试Chrome浏览器..."
    if command -v google-chrome >/dev/null 2>&1; then
        google-chrome --version
        print_success "Chrome测试通过"
    else
        print_error "Chrome测试失败"
    fi

    # 测试虚拟显示
    print_info "测试虚拟显示..."
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    sleep 2

    if ps -p $XVFB_PID > /dev/null; then
        print_success "虚拟显示测试通过"
        kill $XVFB_PID
    else
        print_error "虚拟显示测试失败"
    fi

    print_success "系统测试完成"
    log "系统测试完成"
}

# 显示部署完成信息
show_completion_info() {
    print_success "🎉 部署完成！"
    echo
    print_info "项目目录: $PROJECT_DIR"
    print_info "虚拟环境: $VENV_DIR"
    print_info "日志文件: $LOG_FILE"
    echo
    print_step "使用方法："
    echo "  1. 配置环境变量:"
    echo "     cp .env.example .env"
    echo "     nano .env  # 编辑配置文件"
    echo
    echo "  2. 交互式启动:"
    echo "     ./start.sh"
    echo
    echo "  3. 后台运行:"
    echo "     ./start_daemon.sh start    # 启动"
    echo "     ./start_daemon.sh stop     # 停止"
    echo "     ./start_daemon.sh status   # 状态"
    echo "     ./start_daemon.sh restart  # 重启"
    echo
    echo "  4. 系统服务 (可选):"
    echo "     sudo systemctl start whcms-grabber    # 启动服务"
    echo "     sudo systemctl enable whcms-grabber   # 开机自启"
    echo "     sudo systemctl status whcms-grabber   # 查看状态"
    echo
    print_warning "⚠️  重要提醒："
    echo "  - 请先配置 .env 文件中的登录信息"
    echo "  - 建议先使用交互式启动测试配置"
    echo "  - 生产环境建议使用后台运行模式"
    echo
    print_success "祝您抢单成功！🚀"
}

# 主函数
main() {
    clear
    echo -e "${CYAN}"
    echo "=============================================="
    echo "    WHCMS Auto Grabber - 一键部署脚本"
    echo "    支持 Debian/Ubuntu 系统"
    echo "=============================================="
    echo -e "${NC}"

    # 初始化日志
    echo "部署开始: $(date)" > "$LOG_FILE"

    # 执行部署步骤
    check_root
    check_system
    update_system
    install_system_dependencies
    install_chrome
    create_virtual_environment
    create_requirements
    install_python_dependencies
    setup_environment
    create_startup_scripts
    create_systemd_service
    run_tests
    show_completion_info

    log "部署完成: $(date)"
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查日志: $LOG_FILE"; exit 1' ERR

# 运行主函数
main "$@"
