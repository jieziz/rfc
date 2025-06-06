#!/bin/bash

# =============================================================================
# RFC Auto Grabber - 一键部署脚本
# 支持 Windows Git Bash、Linux、macOS 多平台自动部署
# 支持远程一条命令安装: bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/scripts/deploy.sh)
# 从GitHub自动拉取代码并交互式配置启动
# 集成安装检查功能
# =============================================================================

set -e  # 遇到错误立即退出

# 脚本模式
SCRIPT_MODE="deploy"  # deploy, check, help

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

# 动态设置项目目录
if [[ -n "${BASH_SOURCE[0]}" && "${BASH_SOURCE[0]}" != "/dev/stdin" ]]; then
    # 本地执行
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    # 远程执行
    PROJECT_DIR="$(pwd)/rfc-auto-grabber"
    mkdir -p "$PROJECT_DIR"
fi

REPO_DIR="$PROJECT_DIR/rfc_repo"
PYTHON_VERSION="3.8"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/deploy.log"

# 检测是否为远程执行
REMOTE_INSTALL=false
if [[ "${BASH_SOURCE[0]}" == "/dev/stdin" ]] || [[ -z "${BASH_SOURCE[0]}" ]]; then
    REMOTE_INSTALL=true
fi

# 全局变量
OS=""
ISSUES_FOUND=0

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

# 检查系统类型和必要工具
check_system() {
    print_step "检查系统环境..."

    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/debian_version ]]; then
            OS="debian"
            print_success "检测到 Debian/Ubuntu 系统"
        elif [[ -f /etc/redhat-release ]]; then
            OS="redhat"
            print_success "检测到 RedHat/CentOS 系统"
        else
            OS="linux"
            print_success "检测到 Linux 系统"
        fi
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

    # 检查架构
    ARCH=$(uname -m)
    print_info "系统架构: $ARCH"

    # 检查必要工具
    check_dependencies

    log "系统检查完成: $OS, $ARCH"
}

# 检查必要的依赖工具
check_dependencies() {
    print_step "检查必要工具..."

    local missing_tools=()

    # 检查 git
    if ! command -v git >/dev/null 2>&1; then
        missing_tools+=("git")
    else
        print_success "Git 已安装: $(git --version)"
    fi

    # 检查 python (兼容Windows和Linux)
    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        print_success "Python 已安装: $(python --version)"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        print_success "Python3 已安装: $(python3 --version)"
    else
        missing_tools+=("python")
    fi

    # 检查 pip (兼容Windows和Linux)
    if command -v pip >/dev/null 2>&1; then
        PIP_CMD="pip"
        print_success "Pip 已安装: $(pip --version)"
    elif command -v pip3 >/dev/null 2>&1; then
        PIP_CMD="pip3"
        print_success "Pip3 已安装: $(pip3 --version)"
    else
        missing_tools+=("pip")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_error "缺少必要工具: ${missing_tools[*]}"
        print_info "请安装缺少的工具后重新运行脚本"

        if [[ "$OS" == "debian" ]]; then
            print_info "Ubuntu/Debian 安装命令:"
            print_info "sudo apt update && sudo apt install -y git python3 python3-pip"
        elif [[ "$OS" == "redhat" ]]; then
            print_info "CentOS/RHEL 安装命令:"
            print_info "sudo yum install -y git python3 python3-pip"
        elif [[ "$OS" == "macos" ]]; then
            print_info "macOS 安装命令:"
            print_info "brew install git python3"
        fi

        exit 1
    fi

    print_success "所有必要工具已安装"
}

# 克隆或更新GitHub仓库
clone_or_update_repo() {
    print_step "获取最新代码..."

    if [[ -d "$REPO_DIR" ]]; then
        print_info "仓库目录已存在，更新代码..."
        cd "$REPO_DIR"

        # 检查是否是git仓库
        if [[ -d ".git" ]]; then
            print_info "拉取最新代码..."
            git fetch origin
            git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null
            print_success "代码更新完成"
        else
            print_warning "目录存在但不是git仓库，重新克隆..."
            cd "$PROJECT_DIR"
            rm -rf "$REPO_DIR"
            git clone "$GITHUB_REPO" "$REPO_DIR"
            print_success "代码克隆完成"
        fi
    else
        print_info "克隆仓库..."
        git clone "$GITHUB_REPO" "$REPO_DIR"
        print_success "代码克隆完成"
    fi

    # 检查克隆是否成功
    if [[ ! -d "$REPO_DIR" ]]; then
        print_error "代码获取失败"
        exit 1
    fi

    cd "$REPO_DIR"
    print_info "当前代码版本: $(git rev-parse --short HEAD)"

    log "代码获取完成"
}

# 收集用户输入
collect_user_input() {
    print_step "收集用户配置信息..."

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

    # 输入密码（显示输入）
    while true; do
        read -p "请输入您的密码: " USER_PASSWORD
        if [[ -n "$USER_PASSWORD" ]]; then
            break
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

    # 确认信息
    echo
    print_info "请确认您的配置信息："
    echo "邮箱: $USER_EMAIL"
    echo "密码: $USER_PASSWORD"
    echo "商品PID: $PRODUCT_PID"
    echo

    read -p "确认信息正确？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "重新输入配置信息..."
        collect_user_input
        return
    fi

    print_success "用户配置收集完成"
    log "用户配置收集完成"
}

# 生成配置文件
generate_config_file() {
    print_step "生成配置文件..."

    local env_file="$REPO_DIR/.env"

    # 构建产品URL
    local base_url="https://my.rfchost.com"
    local login_url="$base_url/clientarea.php"
    local product_url="$base_url/cart.php?a=add&pid=$PRODUCT_PID"

    # 检测是否为Linux服务器环境（无显示服务器）
    local headless_mode="True"
    if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ -z "$DISPLAY" ]]; then
        headless_mode="True"
        print_info "检测到Linux服务器环境，自动启用无头模式"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] && [[ -n "$DISPLAY" ]]; then
        print_info "检测到Linux桌面环境，可选择是否使用无头模式"
        read -p "是否使用无头模式？(推荐) (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            headless_mode="False"
        fi
    fi

    # 生成.env文件
    cat > "$env_file" << EOF
# 基础配置
BASE_URL=$base_url
LOGIN_URL=$login_url
PRODUCT_URL=$product_url

# 登录信息
EMAIL=$USER_EMAIL
PASSWORD=$USER_PASSWORD

# 性能配置 - 优化设置
HEADLESS_MODE=$headless_mode
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

    print_success "配置文件生成完成: $env_file"
    print_info "无头模式设置: $headless_mode"
    log "配置文件生成完成，无头模式: $headless_mode"
}

# 安装系统依赖（根据操作系统）
install_system_dependencies() {
    print_step "安装系统依赖..."

    if [[ "$OS" == "debian" ]]; then
        install_debian_dependencies
    elif [[ "$OS" == "redhat" ]]; then
        install_redhat_dependencies
    elif [[ "$OS" == "macos" ]]; then
        install_macos_dependencies
    elif [[ "$OS" == "windows" ]]; then
        print_info "Windows环境，跳过系统依赖安装"
    else
        print_warning "未知系统，跳过系统依赖安装"
    fi
}

# Debian/Ubuntu 依赖安装
install_debian_dependencies() {
    print_info "安装 Debian/Ubuntu 系统依赖..."

    # 更新包列表
    sudo apt-get update -qq

    local packages=(
        "python3-venv"
        "python3-dev"
        "wget"
        "curl"
        "unzip"
    )

    # 如果是桌面环境，安装浏览器相关依赖
    if [[ -n "$DISPLAY" ]] || command -v Xvfb >/dev/null 2>&1; then
        packages+=(
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
        )
    fi

    for package in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            print_info "安装 $package..."
            sudo apt-get install -y "$package" >/dev/null 2>&1
        else
            print_info "$package 已安装"
        fi
    done

    print_success "Debian/Ubuntu 依赖安装完成"
}

# RedHat/CentOS 依赖安装
install_redhat_dependencies() {
    print_info "安装 RedHat/CentOS 系统依赖..."

    local packages=(
        "python3-devel"
        "wget"
        "curl"
        "unzip"
    )

    for package in "${packages[@]}"; do
        if ! rpm -q "$package" >/dev/null 2>&1; then
            print_info "安装 $package..."
            sudo yum install -y "$package" >/dev/null 2>&1
        else
            print_info "$package 已安装"
        fi
    done

    print_success "RedHat/CentOS 依赖安装完成"
}

# macOS 依赖安装
install_macos_dependencies() {
    print_info "macOS 环境，检查 Homebrew..."

    if ! command -v brew >/dev/null 2>&1; then
        print_warning "未安装 Homebrew，建议安装以便管理依赖"
        print_info "安装命令: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    else
        print_success "Homebrew 已安装"
    fi
}

# 安装浏览器（可选）
install_browser() {
    print_step "检查浏览器安装..."

    # 检查是否已安装Chrome或Chromium
    if command -v google-chrome >/dev/null 2>&1; then
        print_success "Google Chrome 已安装: $(google-chrome --version)"
        return
    elif command -v chromium-browser >/dev/null 2>&1; then
        print_success "Chromium 已安装: $(chromium-browser --version)"
        return
    elif command -v chromium >/dev/null 2>&1; then
        print_success "Chromium 已安装: $(chromium --version)"
        return
    fi

    # 根据系统安装浏览器
    if [[ "$OS" == "debian" ]]; then
        print_info "尝试安装 Chromium 浏览器..."
        if sudo apt-get install -y chromium-browser >/dev/null 2>&1; then
            print_success "Chromium 安装成功"
        else
            print_warning "Chromium 安装失败，脚本将使用无头模式"
        fi
    elif [[ "$OS" == "redhat" ]]; then
        print_info "尝试安装 Chromium 浏览器..."
        if sudo yum install -y chromium >/dev/null 2>&1; then
            print_success "Chromium 安装成功"
        else
            print_warning "Chromium 安装失败，脚本将使用无头模式"
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew >/dev/null 2>&1; then
            print_info "尝试安装 Chromium 浏览器..."
            if brew install --cask chromium >/dev/null 2>&1; then
                print_success "Chromium 安装成功"
            else
                print_warning "Chromium 安装失败，请手动安装 Chrome 或 Chromium"
            fi
        else
            print_warning "请手动安装 Chrome 或 Chromium 浏览器"
        fi
    else
        print_warning "请确保系统已安装 Chrome 或 Chromium 浏览器"
    fi

    log "浏览器检查完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    print_step "创建Python虚拟环境..."

    cd "$REPO_DIR"

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

    # 创建虚拟环境
    python3 -m venv "$VENV_DIR"

    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    # 升级pip
    pip install --upgrade pip >/dev/null 2>&1

    print_success "Python虚拟环境创建完成"
    log "Python虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    print_step "安装Python依赖包..."

    cd "$REPO_DIR"

    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    # 检查是否有requirements.txt
    if [[ -f "requirements.txt" ]]; then
        print_info "使用项目的 requirements.txt"
        pip install -r requirements.txt
    else
        print_info "创建基础 requirements.txt"
        cat > "requirements.txt" << EOF
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
        pip install -r requirements.txt
    fi

    print_success "Python依赖安装完成"
    log "Python依赖安装完成"
}

# 运行测试
run_tests() {
    print_step "运行系统测试..."

    cd "$REPO_DIR"

    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

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

    # 测试配置文件
    if [[ -f ".env" ]]; then
        print_success "配置文件存在"
        python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
required_configs = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
missing_configs = [config for config in required_configs if not os.getenv(config)]
if missing_configs:
    print(f'❌ 缺少必要配置: {missing_configs}')
else:
    print('✅ 配置文件验证通过')
"
    else
        print_error "配置文件不存在"
    fi

    print_success "系统测试完成"
    log "系统测试完成"
}

# 启动应用程序
start_application() {
    print_step "启动抢购应用程序..."

    cd "$REPO_DIR"

    # 激活虚拟环境
    if [[ "$OS" == "windows" ]]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    # 检查配置文件
    if [[ ! -f ".env" ]]; then
        print_error "配置文件不存在，无法启动应用"
        exit 1
    fi

    print_success "配置完成，准备启动抢购程序..."
    echo
    print_info "启动选项："
    echo "1. 快速启动（推荐）- 使用 quick_start.py"
    echo "2. 快速模式 - 使用 simple_fast_grabber.py"
    echo "3. 稳定模式 - 使用 stable_grabber.py"
    echo "4. 退出"
    echo

    read -p "请选择启动方式 (1-4): " -n 1 -r
    echo

    case $REPLY in
        1)
            print_info "启动快速启动程序..."
            if [[ -f "quick_start.py" ]]; then
                python quick_start.py
            else
                print_error "quick_start.py 不存在，使用备用方案"
                python auto.py
            fi
            ;;
        2)
            print_info "启动快速模式..."
            if [[ -f "src/grabbers/simple_fast_grabber.py" ]]; then
                python -m src.grabbers.simple_fast_grabber
            else
                print_error "simple_fast_grabber.py 不存在"
                return 1
            fi
            ;;
        3)
            print_info "启动稳定模式..."
            if [[ -f "src/grabbers/stable_grabber.py" ]]; then
                python -m src.grabbers.stable_grabber
            else
                print_error "stable_grabber.py 不存在"
                return 1
            fi
            ;;
        4)
            print_info "退出程序"
            return
            ;;
        *)
            print_warning "无效选择，使用默认启动方式"
            python quick_start.py
            ;;
    esac

    print_success "应用程序执行完成"
    log "应用程序启动完成"
}

# 创建启动脚本
create_startup_scripts() {
    print_step "创建启动脚本..."

    # 创建主启动脚本
    local start_script="$PROJECT_DIR/start_grabber.sh"

    cat > "$start_script" << EOF
#!/bin/bash

# RFC Auto Grabber 启动脚本

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="\$SCRIPT_DIR/rfc_repo"
VENV_DIR="\$SCRIPT_DIR/venv"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "\${GREEN}✅ \$1\${NC}"; }
print_error() { echo -e "\${RED}❌ \$1\${NC}"; }
print_warning() { echo -e "\${YELLOW}⚠️  \$1\${NC}"; }

# 检查目录
if [[ ! -d "\$REPO_DIR" ]]; then
    print_error "代码目录不存在，请先运行部署脚本"
    exit 1
fi

if [[ ! -d "\$VENV_DIR" ]]; then
    print_error "虚拟环境不存在，请先运行部署脚本"
    exit 1
fi

cd "\$REPO_DIR"

# 激活虚拟环境
if [[ "\$OSTYPE" == "msys" ]] || [[ "\$OSTYPE" == "cygwin" ]]; then
    source "\$VENV_DIR/Scripts/activate"
else
    source "\$VENV_DIR/bin/activate"
fi

# 检查配置文件
if [[ ! -f ".env" ]]; then
    print_error "配置文件 .env 不存在"
    print_warning "请先运行部署脚本进行配置"
    exit 1
fi

# 启动应用
print_success "启动 RFC Auto Grabber..."

# 检查是否有显示服务器（Linux环境）
if [[ "\$OSTYPE" == "linux-gnu"* ]] && [[ -z "\$DISPLAY" ]]; then
    print_warning "未检测到显示服务器，使用虚拟显示"
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    XVFB_PID=\$!
    sleep 2
fi

# 检查Python命令
if command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    print_error "未找到Python命令"
    exit 1
fi

# 运行快速启动脚本
if [[ -f "quick_start.py" ]]; then
    \$PYTHON_CMD quick_start.py
else
    print_error "quick_start.py 不存在"
    exit 1
fi

# 清理
if [[ -n "\$XVFB_PID" ]]; then
    kill \$XVFB_PID 2>/dev/null || true
fi
EOF

    chmod +x "$start_script"

    print_success "启动脚本创建完成: $start_script"
    log "启动脚本创建完成"
}

# 显示完成信息
show_completion_info() {
    print_success "🎉 部署完成！"
    echo
    print_info "项目信息："
    print_info "  - 代码目录: $REPO_DIR"
    print_info "  - 虚拟环境: $VENV_DIR"
    print_info "  - 配置文件: $REPO_DIR/.env"
    print_info "  - 启动脚本: $PROJECT_DIR/start_grabber.sh"
    print_info "  - 日志文件: $LOG_FILE"
    echo
    print_step "使用方法："
    echo "  1. 直接启动（推荐）:"
    echo "     cd $REPO_DIR"
    echo "     source $VENV_DIR/bin/activate  # Windows: source $VENV_DIR/Scripts/activate"
    echo "     python quick_start.py"
    echo
    echo "  2. 使用启动脚本:"
    echo "     $PROJECT_DIR/start_grabber.sh"
    echo
    echo "  3. 手动启动特定模式:"
    echo "     cd $REPO_DIR && source $VENV_DIR/bin/activate"
    echo "     python -m src.grabbers.simple_fast_grabber  # 快速模式"
    echo "     python -m src.grabbers.stable_grabber       # 稳定模式"
    echo
    print_info "配置信息："
    echo "  - 邮箱: $USER_EMAIL"
    echo "  - 商品PID: $PRODUCT_PID"
    echo "  - 产品URL: https://my.rfchost.com/cart.php?a=add&pid=$PRODUCT_PID"
    echo
    print_warning "⚠️  重要提醒："
    echo "  - 配置已自动生成，如需修改请编辑 $REPO_DIR/.env"
    echo "  - 建议先测试运行确保配置正确"
    echo "  - 抢购时请确保网络稳定"
    echo
    print_success "祝您抢单成功！🚀"
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--check)
                SCRIPT_MODE="check"
                shift
                ;;
            -d|--deploy)
                SCRIPT_MODE="deploy"
                shift
                ;;
            -h|--help)
                SCRIPT_MODE="help"
                shift
                ;;
            *)
                print_warning "未知参数: $1"
                SCRIPT_MODE="help"
                shift
                ;;
        esac
    done
}

# 显示远程安装信息
show_remote_install_info() {
    if [[ "$REMOTE_INSTALL" == "true" ]]; then
        echo -e "${CYAN}"
        echo "=============================================="
        echo "    RFC Auto Grabber - 一键远程安装"
        echo "=============================================="
        echo -e "${NC}"
        echo
        print_info "🌐 远程安装模式已启用"
        print_info "📁 安装目录: $PROJECT_DIR"
        print_info "📦 将从GitHub自动拉取最新代码"
        echo
        print_step "开始远程安装流程..."
        echo
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "    RFC Auto Grabber - 智能部署和检查脚本"
    echo "=============================================="
    echo -e "${NC}"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -d, --deploy    执行完整部署流程 (默认)"
    echo "  -c, --check     仅执行安装检查"
    echo "  -h, --help      显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0              # 执行完整部署"
    echo "  $0 --check      # 仅检查安装状态"
    echo "  $0 --deploy     # 执行完整部署"
    echo
    echo "远程一键安装:"
    echo "  bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/scripts/deploy.sh)"
    echo
}

# 安装检查功能（从 check_install.sh 移植）
run_installation_check() {
    local issues_found=0

    echo -e "${BLUE}"
    echo "=============================================="
    echo "    RFC Auto Grabber - 安装检查"
    echo "=============================================="
    echo -e "${NC}"

    # 检查操作系统
    print_step "检查操作系统..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -f /etc/debian_version ]]; then
            OS_VERSION=$(cat /etc/debian_version)
            print_success "Debian/Ubuntu 系统 (版本: $OS_VERSION)"
        elif [[ -f /etc/redhat-release ]]; then
            OS_VERSION=$(cat /etc/redhat-release)
            print_success "RedHat/CentOS 系统 (版本: $OS_VERSION)"
        else
            print_success "Linux 系统"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        print_success "Windows 系统 (Git Bash/Cygwin)"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "macOS 系统"
    else
        print_error "不支持的操作系统: $OSTYPE"
        ((issues_found++))
    fi

    # 检查Python
    print_step "检查Python环境..."
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        print_success "$PYTHON_VERSION"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version)
        print_success "$PYTHON_VERSION"
    else
        print_error "Python 未安装"
        ((issues_found++))
    fi

    # 检查pip
    if command -v pip3 >/dev/null 2>&1; then
        PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
        print_success "pip $PIP_VERSION"
    elif command -v pip >/dev/null 2>&1; then
        PIP_VERSION=$(pip --version | cut -d' ' -f2)
        print_success "pip $PIP_VERSION"
    else
        print_error "pip 未安装"
        ((issues_found++))
    fi

    # 检查虚拟环境
    print_step "检查Python虚拟环境..."
    if [[ -d "$VENV_DIR" ]]; then
        print_success "虚拟环境已创建"

        # 检查虚拟环境中的包
        local activate_script
        if [[ "$OS" == "windows" ]]; then
            activate_script="$VENV_DIR/Scripts/activate"
        else
            activate_script="$VENV_DIR/bin/activate"
        fi

        if [[ -f "$activate_script" ]]; then
            source "$activate_script"

            # 检查关键包
            packages=("DrissionPage" "dotenv" "selenium")
            for package in "${packages[@]}"; do
                if python -c "import $package" 2>/dev/null; then
                    print_success "$package 已安装"
                else
                    print_error "$package 未安装"
                    ((issues_found++))
                fi
            done

            deactivate 2>/dev/null || true
        else
            print_error "虚拟环境损坏"
            ((issues_found++))
        fi
    else
        print_error "虚拟环境未创建"
        ((issues_found++))
    fi

    # 检查Google Chrome
    print_step "检查浏览器..."
    if command -v google-chrome >/dev/null 2>&1; then
        CHROME_VERSION=$(google-chrome --version)
        print_success "$CHROME_VERSION"
    elif command -v chromium-browser >/dev/null 2>&1; then
        CHROME_VERSION=$(chromium-browser --version)
        print_success "$CHROME_VERSION"
    elif command -v chromium >/dev/null 2>&1; then
        CHROME_VERSION=$(chromium --version)
        print_success "$CHROME_VERSION"
    else
        print_error "Chrome/Chromium 未安装"
        ((issues_found++))
    fi

    # 检查系统依赖
    print_step "检查系统依赖..."
    if [[ "$OS" != "windows" ]]; then
        dependencies=("wget" "curl" "unzip")
        for dep in "${dependencies[@]}"; do
            if command -v "$dep" >/dev/null 2>&1; then
                print_success "$dep 已安装"
            else
                print_error "$dep 未安装"
                ((issues_found++))
            fi
        done

        # 检查xvfb（Linux特有）
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command -v xvfb >/dev/null 2>&1; then
                print_success "xvfb 已安装"
            else
                print_error "xvfb 未安装"
                ((issues_found++))
            fi
        fi
    else
        print_info "Windows环境，跳过系统依赖检查"
    fi

    # 检查配置文件
    print_step "检查配置文件..."
    local env_file="$REPO_DIR/.env"
    if [[ -f "$env_file" ]]; then
        print_success ".env 配置文件存在"

        # 检查关键配置项
        source "$env_file" 2>/dev/null || true

        if [[ -n "$EMAIL" && "$EMAIL" != "your_email@example.com" ]]; then
            print_success "EMAIL 已配置"
        else
            print_warning "EMAIL 未配置或使用默认值"
        fi

        if [[ -n "$PASSWORD" && "$PASSWORD" != "your_password" ]]; then
            print_success "PASSWORD 已配置"
        else
            print_warning "PASSWORD 未配置或使用默认值"
        fi

        if [[ -n "$PRODUCT_URL" ]]; then
            print_success "PRODUCT_URL 已配置"
        else
            print_warning "PRODUCT_URL 未配置"
        fi

    elif [[ -f "$REPO_DIR/.env.example" ]]; then
        print_warning ".env 文件不存在，但有示例文件"
        print_info "请运行: cp .env.example .env"
    else
        print_error "配置文件不存在"
        ((issues_found++))
    fi

    # 检查网络连接
    print_step "检查网络连接..."
    if ping -c 1 google.com >/dev/null 2>&1; then
        print_success "网络连接正常"
    else
        print_warning "网络连接可能有问题"
    fi

    # 检查磁盘空间
    print_step "检查磁盘空间..."
    if command -v df >/dev/null 2>&1; then
        AVAILABLE_SPACE=$(df "$PROJECT_DIR" 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
        if [[ $AVAILABLE_SPACE -gt 1048576 ]]; then  # 1GB
            print_success "磁盘空间充足 ($(($AVAILABLE_SPACE/1024/1024))GB 可用)"
        else
            print_warning "磁盘空间不足 ($(($AVAILABLE_SPACE/1024))MB 可用)"
        fi
    else
        print_info "无法检查磁盘空间"
    fi

    # 检查内存
    print_step "检查系统内存..."
    if command -v free >/dev/null 2>&1; then
        TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
        AVAILABLE_MEM=$(free -m | awk 'NR==2{print $7}')

        if [[ $TOTAL_MEM -gt 4096 ]]; then
            print_success "系统内存充足 (${TOTAL_MEM}MB 总计)"
        else
            print_warning "系统内存较少 (${TOTAL_MEM}MB 总计)"
        fi

        if [[ $AVAILABLE_MEM -gt 2048 ]]; then
            print_success "可用内存充足 (${AVAILABLE_MEM}MB 可用)"
        else
            print_warning "可用内存不足 (${AVAILABLE_MEM}MB 可用)"
        fi
    else
        print_info "无法检查内存信息"
    fi

    # 总结
    echo
    echo "=============================================="
    if [[ $issues_found -eq 0 ]]; then
        print_success "🎉 所有检查通过！系统已准备就绪"
        echo
        print_info "下一步操作："
        echo "  1. 配置 .env 文件 (如果还未配置)"
        echo "  2. 运行测试: cd $REPO_DIR && python quick_start.py"
        echo "  3. 启动服务: $PROJECT_DIR/start_grabber.sh"
    else
        print_error "发现 $issues_found 个问题需要解决"
        echo
        print_info "建议操作："
        echo "  1. 重新运行部署脚本: $0 --deploy"
        echo "  2. 手动安装缺失的依赖"
        echo "  3. 检查配置文件"
    fi
    echo "=============================================="

    return $issues_found
}

# 主函数
main() {
    # 解析命令行参数
    parse_arguments "$@"

    case $SCRIPT_MODE in
        "help")
            show_help
            exit 0
            ;;
        "check")
            clear
            run_installation_check
            exit $?
            ;;
        "deploy")
            clear

            # 显示远程安装信息（如果适用）
            show_remote_install_info

            if [[ "$REMOTE_INSTALL" != "true" ]]; then
                echo -e "${CYAN}"
                echo "=============================================="
                echo "    RFC Auto Grabber - 智能部署脚本"
                echo "    支持从GitHub自动拉取并配置启动"
                echo "=============================================="
                echo -e "${NC}"
            fi

            # 初始化日志
            echo "部署开始: $(date)" > "$LOG_FILE"

            # 执行部署步骤
            check_root
            check_system
            clone_or_update_repo
            collect_user_input
            generate_config_file
            install_system_dependencies
            install_browser
            create_virtual_environment
            install_python_dependencies
            run_tests
            create_startup_scripts
            show_completion_info

            echo
            print_step "是否立即启动抢购程序？"
            read -p "(y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                start_application
            else
                print_info "您可以稍后使用以下命令启动："
                print_info "$PROJECT_DIR/start_grabber.sh"
            fi

            log "部署完成: $(date)"
            ;;
        *)
            print_error "未知模式: $SCRIPT_MODE"
            show_help
            exit 1
            ;;
    esac
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查日志: $LOG_FILE"; exit 1' ERR

# 运行主函数
main "$@"
