#!/bin/bash

# =============================================================================
# WHCMS Auto Grabber - 快速部署脚本 (简化版)
# 适用于有经验的用户快速部署
# =============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 WHCMS Auto Grabber - 快速部署${NC}"
echo "================================================"

# 1. 更新系统
print_info "更新系统包..."
sudo apt-get update -qq

# 2. 安装基础依赖
print_info "安装系统依赖..."
sudo apt-get install -y python3 python3-pip python3-venv wget curl unzip xvfb \
    fonts-liberation libasound2 libatk-bridge2.0-0 libdrm2 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libxss1 libnss3 >/dev/null 2>&1

# 3. 安装Chrome
if ! command -v google-chrome >/dev/null 2>&1; then
    print_info "安装Google Chrome..."
    cd /tmp
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y >/dev/null 2>&1
    cd "$PROJECT_DIR"
fi

# 4. 创建虚拟环境
print_info "创建Python虚拟环境..."
if [[ -d "venv" ]]; then
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip >/dev/null 2>&1

# 5. 创建requirements.txt
cat > requirements.txt << EOF
DrissionPage>=4.0.0
python-dotenv>=1.0.0
selenium>=4.15.0
requests>=2.31.0
EOF

# 6. 安装Python依赖
print_info "安装Python依赖..."
pip install -r requirements.txt >/dev/null 2>&1

# 7. 创建环境配置示例
if [[ ! -f ".env" ]]; then
    cat > .env.example << EOF
# 基础配置
BASE_URL=https://my.rfchost.com
LOGIN_URL=https://my.rfchost.com/clientarea.php
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229

# 登录信息 (必填)
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
fi

# 8. 创建启动脚本
cat > run.sh << 'EOF'
#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -f ".env" ]]; then
    echo "❌ 请先配置 .env 文件"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

source venv/bin/activate

# 设置虚拟显示 (无头模式)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2

echo "🚀 启动 WHCMS Auto Grabber..."
python quick_start.py

# 清理
kill $XVFB_PID 2>/dev/null || true
EOF

chmod +x run.sh

# 9. 创建后台运行脚本
cat > daemon.sh << 'EOF'
#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/grabber.pid"
LOG_FILE="$PROJECT_DIR/grabber.log"

start() {
    if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "⚠️  服务已在运行"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 &
    sleep 2
    
    nohup python simple_fast_grabber.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ 服务已启动 (PID: $(cat "$PID_FILE"))"
}

stop() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            pkill -f "Xvfb :99" 2>/dev/null || true
            echo "✅ 服务已停止"
        else
            echo "⚠️  服务进程不存在"
            rm -f "$PID_FILE"
        fi
    else
        echo "⚠️  服务未运行"
    fi
}

status() {
    if [[ -f "$PID_FILE" ]] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✅ 服务正在运行 (PID: $(cat "$PID_FILE"))"
    else
        echo "⚠️  服务未运行"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status) status ;;
    *) echo "用法: $0 {start|stop|restart|status}" ;;
esac
EOF

chmod +x daemon.sh

# 10. 测试安装
print_info "测试安装..."
source venv/bin/activate

python3 -c "
try:
    import DrissionPage
    print('✅ DrissionPage')
except: print('❌ DrissionPage')

try:
    from dotenv import load_dotenv
    print('✅ python-dotenv')
except: print('❌ python-dotenv')
"

if command -v google-chrome >/dev/null 2>&1; then
    print_success "Chrome: $(google-chrome --version | cut -d' ' -f3)"
else
    print_error "Chrome 安装失败"
fi

echo
print_success "🎉 快速部署完成！"
echo
echo "📋 下一步操作："
echo "  1. 配置登录信息:"
echo "     cp .env.example .env"
echo "     nano .env"
echo
echo "  2. 运行程序:"
echo "     ./run.sh          # 交互式运行"
echo "     ./daemon.sh start # 后台运行"
echo
echo "  3. 管理后台服务:"
echo "     ./daemon.sh status   # 查看状态"
echo "     ./daemon.sh stop     # 停止服务"
echo "     ./daemon.sh restart  # 重启服务"
echo
print_warning "⚠️  请先编辑 .env 文件填写您的登录信息！"
