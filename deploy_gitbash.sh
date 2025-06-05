#!/bin/bash

# =============================================================================
# RFC Auto Grabber - Git Bash 部署脚本
# 专为Windows Git Bash环境设计，支持从GitHub自动拉取代码并交互式配置启动
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
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$PROJECT_DIR/rfc_repo"
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

# 检查必要工具
check_dependencies() {
    print_step "检查必要工具..."
    
    local missing_tools=()
    
    # 检查 git
    if ! command -v git >/dev/null 2>&1; then
        missing_tools+=("git")
    else
        print_success "Git 已安装: $(git --version)"
    fi
    
    # 检查 python
    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        print_success "Python 已安装: $(python --version)"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        print_success "Python3 已安装: $(python3 --version)"
    else
        missing_tools+=("python")
    fi
    
    # 检查 pip
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
        print_info "Windows 安装建议:"
        print_info "  - Git: https://git-scm.com/download/win"
        print_info "  - Python: https://www.python.org/downloads/"
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
    
    # 输入密码（隐藏显示）
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
    
    # 确认信息
    echo
    print_info "请确认您的配置信息："
    echo "邮箱: $USER_EMAIL"
    echo "密码: $(echo "$USER_PASSWORD" | sed 's/./*/g')"
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
    
    print_success "配置文件生成完成: $env_file"
    log "配置文件生成完成"
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
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # 激活虚拟环境（Git Bash环境）
    source "$VENV_DIR/Scripts/activate"
    
    # 升级pip
    $PIP_CMD install --upgrade pip >/dev/null 2>&1
    
    print_success "Python虚拟环境创建完成"
    log "Python虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    print_step "安装Python依赖包..."
    
    cd "$REPO_DIR"
    
    # 激活虚拟环境（Git Bash环境）
    source "$VENV_DIR/Scripts/activate"
    
    # 检查是否有requirements.txt
    if [[ -f "requirements.txt" ]]; then
        print_info "使用项目的 requirements.txt"
        $PIP_CMD install -r requirements.txt
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
        $PIP_CMD install -r requirements.txt
    fi
    
    print_success "Python依赖安装完成"
    log "Python依赖安装完成"
}

# 运行测试
run_tests() {
    print_step "运行系统测试..."

    cd "$REPO_DIR"

    # 激活虚拟环境
    source "$VENV_DIR/Scripts/activate"

    # 测试Python环境
    print_info "测试Python环境..."
    $PYTHON_CMD -c "import sys; print(f'Python版本: {sys.version}')"

    # 测试依赖包
    print_info "测试依赖包..."
    $PYTHON_CMD -c "
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
        $PYTHON_CMD -c "
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

# 创建启动脚本
create_startup_scripts() {
    print_step "创建启动脚本..."

    # 创建启动脚本
    local start_script_bash="$PROJECT_DIR/start_grabber.sh"

    cat > "$start_script_bash" << 'EOF'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/rfc_repo"
VENV_DIR="$SCRIPT_DIR/venv"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查目录
if [[ ! -d "$REPO_DIR" ]]; then
    print_error "代码目录不存在，请先运行部署脚本"
    exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
    print_error "虚拟环境不存在，请先运行部署脚本"
    exit 1
fi

cd "$REPO_DIR"

# 激活虚拟环境（Git Bash环境）
source "$VENV_DIR/Scripts/activate"

# 检查配置文件
if [[ ! -f ".env" ]]; then
    print_error "配置文件 .env 不存在"
    print_warning "请先运行部署脚本进行配置"
    exit 1
fi

# 启动应用
print_success "启动 RFC Auto Grabber..."

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
    $PYTHON_CMD quick_start.py
else
    $PYTHON_CMD auto.py
fi
EOF

    chmod +x "$start_script_bash"

    print_success "启动脚本创建完成: $start_script_bash"
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
    print_info "  - 日志文件: $LOG_FILE"
    echo
    print_step "使用方法："
    echo "  1. 使用启动脚本（推荐）:"
    echo "     $PROJECT_DIR/start_grabber.sh"
    echo
    echo "  2. 手动启动:"
    echo "     cd $REPO_DIR"
    echo "     source $VENV_DIR/Scripts/activate"
    echo "     python quick_start.py"
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
    echo "  - Windows环境建议安装Chrome浏览器"
    echo
    print_success "祝您抢单成功！🚀"
}

# 启动应用程序
start_application() {
    print_step "启动抢购应用程序..."

    cd "$REPO_DIR"

    # 激活虚拟环境
    source "$VENV_DIR/Scripts/activate"

    # 检查配置文件
    if [[ ! -f ".env" ]]; then
        print_error "配置文件不存在，无法启动应用"
        exit 1
    fi

    print_success "配置完成，准备启动抢购程序..."
    echo
    print_info "启动选项："
    echo "1. 快速启动（推荐）- 使用 quick_start.py"
    echo "2. 简化快速模式 - 使用 simple_fast_grabber.py"
    echo "3. 原版模式 - 使用 auto.py"
    echo "4. 退出"
    echo

    read -p "请选择启动方式 (1-4): " -n 1 -r
    echo

    case $REPLY in
        1)
            print_info "启动快速启动程序..."
            if [[ -f "quick_start.py" ]]; then
                $PYTHON_CMD quick_start.py
            else
                print_error "quick_start.py 不存在，使用备用方案"
                $PYTHON_CMD auto.py
            fi
            ;;
        2)
            print_info "启动简化快速模式..."
            if [[ -f "simple_fast_grabber.py" ]]; then
                $PYTHON_CMD simple_fast_grabber.py
            else
                print_error "simple_fast_grabber.py 不存在，使用备用方案"
                $PYTHON_CMD auto.py
            fi
            ;;
        3)
            print_info "启动原版模式..."
            $PYTHON_CMD auto.py
            ;;
        4)
            print_info "退出程序"
            return
            ;;
        *)
            print_warning "无效选择，使用默认启动方式"
            $PYTHON_CMD auto.py
            ;;
    esac

    print_success "应用程序执行完成"
    log "应用程序启动完成"
}

# 主函数
main() {
    clear
    echo -e "${CYAN}"
    echo "=============================================="
    echo "    RFC Auto Grabber - Git Bash 部署脚本"
    echo "    支持从GitHub自动拉取并配置启动"
    echo "=============================================="
    echo -e "${NC}"

    # 初始化日志
    echo "部署开始: $(date)" > "$LOG_FILE"

    # 执行部署步骤
    check_dependencies
    clone_or_update_repo
    collect_user_input
    generate_config_file
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
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查日志: $LOG_FILE"; exit 1' ERR

# 运行主函数
main "$@"
