#!/bin/bash

# =============================================================================
# WHCMS Auto Grabber - 安装检查脚本
# 验证系统环境和依赖是否正确安装
# =============================================================================

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_step() { echo -e "${PURPLE}🔍 $1${NC}"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISSUES_FOUND=0

echo -e "${BLUE}"
echo "=============================================="
echo "    WHCMS Auto Grabber - 安装检查"
echo "=============================================="
echo -e "${NC}"

# 检查操作系统
print_step "检查操作系统..."
if [[ -f /etc/debian_version ]]; then
    OS_VERSION=$(cat /etc/debian_version)
    print_success "Debian/Ubuntu 系统 (版本: $OS_VERSION)"
else
    print_error "不支持的操作系统"
    ((ISSUES_FOUND++))
fi

# 检查Python
print_step "检查Python环境..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION"
else
    print_error "Python3 未安装"
    ((ISSUES_FOUND++))
fi

# 检查pip
if command -v pip3 >/dev/null 2>&1; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_success "pip $PIP_VERSION"
else
    print_error "pip3 未安装"
    ((ISSUES_FOUND++))
fi

# 检查虚拟环境
print_step "检查Python虚拟环境..."
if [[ -d "$PROJECT_DIR/venv" ]]; then
    print_success "虚拟环境已创建"
    
    # 检查虚拟环境中的包
    if [[ -f "$PROJECT_DIR/venv/bin/activate" ]]; then
        source "$PROJECT_DIR/venv/bin/activate"
        
        # 检查关键包
        packages=("DrissionPage" "dotenv" "selenium")
        for package in "${packages[@]}"; do
            if python -c "import $package" 2>/dev/null; then
                print_success "$package 已安装"
            else
                print_error "$package 未安装"
                ((ISSUES_FOUND++))
            fi
        done
        
        deactivate
    else
        print_error "虚拟环境损坏"
        ((ISSUES_FOUND++))
    fi
else
    print_error "虚拟环境未创建"
    ((ISSUES_FOUND++))
fi

# 检查Google Chrome
print_step "检查Google Chrome..."
if command -v google-chrome >/dev/null 2>&1; then
    CHROME_VERSION=$(google-chrome --version)
    print_success "$CHROME_VERSION"
else
    print_error "Google Chrome 未安装"
    ((ISSUES_FOUND++))
fi

# 检查系统依赖
print_step "检查系统依赖..."
dependencies=("xvfb" "wget" "curl" "unzip")
for dep in "${dependencies[@]}"; do
    if command -v "$dep" >/dev/null 2>&1; then
        print_success "$dep 已安装"
    else
        print_error "$dep 未安装"
        ((ISSUES_FOUND++))
    fi
done

# 检查配置文件
print_step "检查配置文件..."
if [[ -f "$PROJECT_DIR/.env" ]]; then
    print_success ".env 配置文件存在"
    
    # 检查关键配置项
    source "$PROJECT_DIR/.env" 2>/dev/null || true
    
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
    
elif [[ -f "$PROJECT_DIR/.env.example" ]]; then
    print_warning ".env 文件不存在，但有示例文件"
    print_info "请运行: cp .env.example .env"
else
    print_error "配置文件不存在"
    ((ISSUES_FOUND++))
fi

# 检查启动脚本
print_step "检查启动脚本..."
scripts=("run.sh" "daemon.sh")
for script in "${scripts[@]}"; do
    if [[ -f "$PROJECT_DIR/$script" ]]; then
        if [[ -x "$PROJECT_DIR/$script" ]]; then
            print_success "$script 存在且可执行"
        else
            print_warning "$script 存在但不可执行"
            print_info "运行: chmod +x $script"
        fi
    else
        print_error "$script 不存在"
        ((ISSUES_FOUND++))
    fi
done

# 检查网络连接
print_step "检查网络连接..."
if ping -c 1 google.com >/dev/null 2>&1; then
    print_success "网络连接正常"
else
    print_warning "网络连接可能有问题"
fi

# 测试虚拟显示
print_step "测试虚拟显示..."
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2

if ps -p $XVFB_PID >/dev/null 2>&1; then
    print_success "虚拟显示测试通过"
    kill $XVFB_PID 2>/dev/null || true
else
    print_error "虚拟显示测试失败"
    ((ISSUES_FOUND++))
fi

# 检查端口占用
print_step "检查端口占用..."
if netstat -tuln 2>/dev/null | grep -q ":99 "; then
    print_warning "端口 99 被占用"
else
    print_success "端口 99 可用"
fi

# 检查磁盘空间
print_step "检查磁盘空间..."
AVAILABLE_SPACE=$(df "$PROJECT_DIR" | awk 'NR==2 {print $4}')
if [[ $AVAILABLE_SPACE -gt 1048576 ]]; then  # 1GB
    print_success "磁盘空间充足 ($(($AVAILABLE_SPACE/1024/1024))GB 可用)"
else
    print_warning "磁盘空间不足 ($(($AVAILABLE_SPACE/1024))MB 可用)"
fi

# 检查内存
print_step "检查系统内存..."
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

# 总结
echo
echo "=============================================="
if [[ $ISSUES_FOUND -eq 0 ]]; then
    print_success "🎉 所有检查通过！系统已准备就绪"
    echo
    print_info "下一步操作："
    echo "  1. 配置 .env 文件 (如果还未配置)"
    echo "  2. 运行测试: ./run.sh"
    echo "  3. 启动服务: ./daemon.sh start"
else
    print_error "发现 $ISSUES_FOUND 个问题需要解决"
    echo
    print_info "建议操作："
    echo "  1. 重新运行部署脚本: ./deploy.sh 或 ./quick_deploy.sh"
    echo "  2. 手动安装缺失的依赖"
    echo "  3. 检查配置文件"
fi
echo "=============================================="
