# Linux无头模式配置指南

## 概述

在Linux服务器环境中，通常没有图形界面（GUI），因此需要使用无头模式（headless mode）来运行浏览器。本指南详细说明如何在Linux环境中正确配置和使用RFC Auto Grabber。

## 环境检测

系统会自动检测以下环境特征来判断是否需要启用无头模式：

- **操作系统**: Linux (os.name == 'posix')
- **显示服务器**: 无DISPLAY环境变量
- **Wayland**: 无WAYLAND_DISPLAY环境变量

## 自动优化特性

### 1. 环境自动检测
```python
# 系统会自动检测Linux无头环境
if is_linux_headless_environment():
    # 自动应用无头模式优化
    apply_linux_optimizations(browser_options, 'performance')
```

### 2. 浏览器参数优化

#### 性能模式参数
```bash
--disable-software-rasterizer      # 禁用软件光栅化
--disable-background-networking    # 禁用后台网络
--disable-default-apps            # 禁用默认应用
--disable-sync                    # 禁用同步
--disable-translate               # 禁用翻译
--hide-scrollbars                 # 隐藏滚动条
--metrics-recording-only          # 仅记录指标
--mute-audio                      # 静音
--no-first-run                    # 跳过首次运行
--safebrowsing-disable-auto-update # 禁用安全浏览自动更新
```

#### 稳定模式参数
```bash
--disable-hang-monitor            # 禁用挂起监控
--disable-prompt-on-repost        # 禁用重新提交提示
--disable-component-extensions    # 禁用组件扩展
--disable-background-timer-throttling # 禁用后台定时器限制
```

## 配置说明

### 1. 环境变量配置

在 `.env` 文件中设置：
```env
# 强制启用无头模式（Linux服务器推荐）
HEADLESS_MODE=True

# 性能优化配置
DELAY_TIME=0.3
ELEMENT_TIMEOUT=2
PAGE_LOAD_TIMEOUT=10
STOCK_CHECK_INTERVAL=0.2
```

### 2. 部署脚本自动配置

部署脚本会自动检测Linux环境：
```bash
# 检测到Linux服务器环境时
if [[ "$OSTYPE" == "linux-gnu"* ]] && [[ -z "$DISPLAY" ]]; then
    headless_mode="True"
    echo "检测到Linux服务器环境，自动启用无头模式"
fi
```

## 系统依赖

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-venv \
    python3-dev \
    wget \
    curl \
    unzip \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3
```

### CentOS/RHEL
```bash
sudo yum install -y \
    python3-devel \
    wget \
    curl \
    unzip \
    xorg-x11-server-Xvfb
```

### 浏览器安装
```bash
# Ubuntu/Debian
sudo apt-get install -y chromium-browser

# CentOS/RHEL
sudo yum install -y chromium
```

## 使用方法

### 1. 快速启动
```bash
# 自动检测环境并启动
python quick_start.py
```

### 2. 直接运行特定模式
```bash
# 快速模式（推荐）
python -m src.grabbers.simple_fast_grabber

# 稳定模式
python -m src.grabbers.stable_grabber

# 并发模式
python -m src.grabbers.concurrent_grabber
```

### 3. 测试无头模式
```bash
# 运行测试脚本验证配置
python test_linux_headless.py
```

## 故障排除

### 1. 常见问题

#### 问题：浏览器启动失败
```
selenium.common.exceptions.WebDriverException: unknown error: Chrome failed to start
```

**解决方案：**
```bash
# 检查Chrome是否安装
which google-chrome || which chromium-browser || which chromium

# 检查依赖
ldd $(which chromium-browser) | grep "not found"

# 安装缺失依赖
sudo apt-get install -y libnss3 libgconf-2-4
```

#### 问题：权限错误
```
Permission denied: '/dev/shm'
```

**解决方案：**
```bash
# 添加无沙盒参数（已自动包含）
--no-sandbox
--disable-dev-shm-usage
```

#### 问题：内存不足
```
Out of memory
```

**解决方案：**
```bash
# 检查内存使用
free -h

# 减少并发浏览器数量
CONCURRENT_BROWSERS=1

# 使用稳定模式
python -m src.grabbers.stable_grabber
```

### 2. 调试方法

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 检查环境信息
```python
from src.utils.linux_optimizer import log_environment_info
log_environment_info()
```

#### 手动测试浏览器
```python
from DrissionPage import Chromium, ChromiumOptions
from src.utils.linux_optimizer import apply_linux_optimizations

co = ChromiumOptions().auto_port()
co = apply_linux_optimizations(co, 'performance')
browser = Chromium(co)
```

## 性能优化建议

### 1. 系统级优化
```bash
# 增加文件描述符限制
ulimit -n 4096

# 优化内存使用
echo 'vm.swappiness=10' >> /etc/sysctl.conf

# 禁用不必要的服务
systemctl disable bluetooth
systemctl disable cups
```

### 2. 应用级优化
```env
# 减少检查间隔
STOCK_CHECK_INTERVAL=0.1

# 降低超时时间
PAGE_LOAD_TIMEOUT=8
ELEMENT_TIMEOUT=2

# 启用快速模式
FAST_MODE=True
QUICK_PURCHASE=True
```

### 3. 网络优化
```bash
# 检查网络延迟
ping -c 5 my.rfchost.com

# 使用DNS优化
echo 'nameserver 8.8.8.8' > /etc/resolv.conf
```

## 监控和日志

### 1. 系统监控
```bash
# 监控CPU和内存使用
htop

# 监控网络连接
netstat -an | grep :80

# 监控磁盘IO
iotop
```

### 2. 应用日志
```bash
# 查看应用日志
tail -f simple_fast.log
tail -f stable_grabber.log
tail -f concurrent_log.log

# 查看测试日志
tail -f linux_headless_test.log
```

## 最佳实践

1. **使用快速模式**: 在Linux服务器上推荐使用快速模式，性能最佳
2. **监控资源**: 定期检查CPU、内存和网络使用情况
3. **定期重启**: 长时间运行后建议重启程序释放资源
4. **备份配置**: 保存有效的配置文件作为备份
5. **测试验证**: 部署后运行测试脚本验证功能正常

## 技术支持

如果遇到问题，请：

1. 运行测试脚本：`python test_linux_headless.py`
2. 检查日志文件中的错误信息
3. 确认系统依赖是否完整安装
4. 验证网络连接是否正常
