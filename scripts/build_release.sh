#!/bin/bash

# =============================================================================
# RFC Auto Grabber - 发布构建脚本
# 将源码编译为二进制文件，保护源码不被泄露
# =============================================================================

set -e

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
print_step() { echo -e "${BLUE}🔄 $1${NC}"; }

# 项目信息
PROJECT_NAME="RFC Auto Grabber"
VERSION="1.0.0"
BUILD_DIR="build"
DIST_DIR="dist"
RELEASE_DIR="release"

# 检查环境
check_environment() {
    print_step "检查构建环境..."

    # 检查Python
    if command -v python >/dev/null 2>&1; then
        PYTHON_CMD="python"
        print_success "Python 已安装: $(python --version)"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
        print_success "Python3 已安装: $(python3 --version)"
    else
        print_error "未找到Python，请先安装Python 3.8+"
        exit 1
    fi

    # 检查pip
    if command -v pip >/dev/null 2>&1; then
        PIP_CMD="pip"
    elif command -v pip3 >/dev/null 2>&1; then
        PIP_CMD="pip3"
    else
        print_error "未找到pip，请先安装pip"
        exit 1
    fi

    # 检查PyInstaller
    if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
        print_info "安装PyInstaller..."
        $PIP_CMD install pyinstaller
    fi

    # 检查其他必要依赖
    local required_packages=("selenium" "requests" "python-dotenv")
    for package in "${required_packages[@]}"; do
        if ! $PYTHON_CMD -c "import ${package//-/_}" 2>/dev/null; then
            print_info "安装 $package..."
            $PIP_CMD install "$package"
        fi
    done

    print_success "构建环境检查完成"
}

# 清理旧的构建文件
clean_build() {
    print_step "清理旧的构建文件..."
    
    rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
    mkdir -p "$RELEASE_DIR"
    
    print_success "构建目录清理完成"
}

# 构建主程序
build_main_program() {
    print_step "构建主程序..."

    # 检查主程序文件是否存在
    if [[ ! -f "quick_start.py" ]]; then
        print_error "主程序文件 quick_start.py 不存在"
        exit 1
    fi

    # 根据操作系统设置数据分隔符
    local data_separator=":"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        data_separator=";"
    fi

    # 构建快速启动器
    print_info "使用PyInstaller构建主程序..."
    $PYTHON_CMD -m PyInstaller --onefile \
        --name="rfc-grabber" \
        --distpath="$RELEASE_DIR" \
        --workpath="$BUILD_DIR" \
        --specpath="$BUILD_DIR" \
        --add-data="config${data_separator}config" \
        --hidden-import="selenium" \
        --hidden-import="requests" \
        --hidden-import="python-dotenv" \
        --hidden-import="selenium.webdriver" \
        --hidden-import="selenium.webdriver.chrome" \
        --hidden-import="selenium.webdriver.common" \
        --console \
        quick_start.py

    print_success "主程序构建完成"
}

# 构建各个抢购模块
build_grabbers() {
    print_step "构建抢购模块..."

    local grabbers=(
        "src/grabbers/simple_fast_grabber.py:fast-grabber"
        "src/grabbers/stable_grabber.py:stable-grabber"
        "src/grabbers/concurrent_grabber.py:concurrent-grabber"
    )

    # 根据操作系统设置数据分隔符
    local data_separator=":"
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        data_separator=";"
    fi

    for grabber_info in "${grabbers[@]}"; do
        IFS=':' read -r source_file output_name <<< "$grabber_info"

        if [[ -f "$source_file" ]]; then
            print_info "构建 $output_name..."

            $PYTHON_CMD -m PyInstaller --onefile \
                --name="$output_name" \
                --distpath="$RELEASE_DIR" \
                --workpath="$BUILD_DIR" \
                --specpath="$BUILD_DIR" \
                --add-data="config${data_separator}config" \
                --add-data="src${data_separator}src" \
                --hidden-import="selenium" \
                --hidden-import="requests" \
                --hidden-import="python-dotenv" \
                --hidden-import="selenium.webdriver" \
                --hidden-import="selenium.webdriver.chrome" \
                --hidden-import="selenium.webdriver.common" \
                --console \
                "$source_file"
        else
            print_warning "跳过不存在的文件: $source_file"
        fi
    done

    print_success "抢购模块构建完成"
}

# 创建配置模板
create_config_template() {
    print_step "创建配置模板..."
    
    cat > "$RELEASE_DIR/.env.template" << 'EOF'
# RFC Auto Grabber 配置文件
# 请复制此文件为 .env 并填写您的信息

# 基础配置
BASE_URL=https://my.rfchost.com
LOGIN_URL=https://my.rfchost.com/clientarea.php
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=YOUR_PID

# 登录信息 (必填)
EMAIL=your_email@example.com
PASSWORD=your_password

# 性能配置 (可选)
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
    
    print_success "配置模板创建完成"
}

# 创建启动脚本
create_startup_scripts() {
    print_step "创建启动脚本..."
    
    # Windows 启动脚本
    cat > "$RELEASE_DIR/start.bat" << 'EOF'
@echo off
echo RFC Auto Grabber - Windows Launcher
echo.

if not exist .env (
    echo 错误: 配置文件 .env 不存在
    echo 请复制 .env.template 为 .env 并填写您的信息
    pause
    exit /b 1
)

echo 启动 RFC Auto Grabber...
rfc-grabber.exe
pause
EOF
    
    # Linux/macOS 启动脚本
    cat > "$RELEASE_DIR/start.sh" << 'EOF'
#!/bin/bash

echo "RFC Auto Grabber - Linux/macOS Launcher"
echo

if [[ ! -f ".env" ]]; then
    echo "错误: 配置文件 .env 不存在"
    echo "请复制 .env.template 为 .env 并填写您的信息"
    exit 1
fi

echo "启动 RFC Auto Grabber..."
./rfc-grabber
EOF
    
    chmod +x "$RELEASE_DIR/start.sh"
    
    print_success "启动脚本创建完成"
}

# 创建说明文档
create_documentation() {
    print_step "创建说明文档..."
    
    cat > "$RELEASE_DIR/README.txt" << EOF
RFC Auto Grabber v${VERSION}
============================

这是一个编译后的二进制版本，源码已被保护。

快速开始:
1. 复制 .env.template 为 .env
2. 编辑 .env 文件，填写您的邮箱、密码和商品PID
3. 运行启动脚本:
   - Windows: 双击 start.bat
   - Linux/macOS: 运行 ./start.sh

文件说明:
- rfc-grabber: 主程序 (交互式界面)
- fast-grabber: 快速模式
- stable-grabber: 稳定模式  
- concurrent-grabber: 并发模式
- .env.template: 配置文件模板
- start.bat/start.sh: 启动脚本

注意事项:
- 请确保系统已安装Chrome或Chromium浏览器
- 首次运行可能需要下载浏览器驱动
- 建议在稳定的网络环境下使用

技术支持: https://github.com/jieziz/rfc
EOF
    
    print_success "说明文档创建完成"
}

# 打包发布文件
package_release() {
    print_step "打包发布文件..."
    
    local release_name="rfc-auto-grabber-v${VERSION}"
    
    # 创建发布包
    if command -v zip >/dev/null 2>&1; then
        cd "$RELEASE_DIR"
        zip -r "../${release_name}.zip" ./*
        cd ..
        print_success "发布包创建完成: ${release_name}.zip"
    else
        print_warning "未找到zip命令，跳过打包"
    fi
}

# 显示构建结果
show_build_result() {
    echo
    print_success "🎉 构建完成！"
    echo
    print_info "发布文件位置: $RELEASE_DIR/"
    print_info "文件列表:"
    ls -la "$RELEASE_DIR/"
    echo
    print_info "用户只需要:"
    print_info "1. 下载发布包"
    print_info "2. 配置 .env 文件"  
    print_info "3. 运行启动脚本"
    echo
    print_warning "⚠️  源码已被保护，用户无法查看Python代码"
}

# 主函数
main() {
    echo "🔨 开始构建 $PROJECT_NAME v$VERSION"
    echo
    
    check_environment
    clean_build
    build_main_program
    build_grabbers
    create_config_template
    create_startup_scripts
    create_documentation
    package_release
    show_build_result
}

# 运行主函数
main "$@"
