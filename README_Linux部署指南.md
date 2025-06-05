# 🐧 Linux Debian 部署指南

## 📋 系统要求

### 支持的系统
- **Debian 10+** (推荐)
- **Ubuntu 18.04+** (推荐)
- **其他基于Debian的发行版**

### 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB以上 (推荐8GB)
- **存储**: 2GB可用空间
- **网络**: 稳定的互联网连接

## 🚀 一键部署

### 方法1: 完整部署 (推荐新手)

```bash
# 下载并运行完整部署脚本
chmod +x deploy.sh
./deploy.sh
```

**特性:**
- ✅ 完整的系统检查和依赖安装
- ✅ 自动创建systemd服务
- ✅ 详细的日志记录
- ✅ 完整的测试验证

### 方法2: 快速部署 (推荐有经验用户)

```bash
# 下载并运行快速部署脚本
chmod +x quick_deploy.sh
./quick_deploy.sh
```

**特性:**
- ⚡ 快速安装，5分钟内完成
- 🎯 专注核心功能
- 📦 最小化依赖

## ⚙️ 手动部署 (高级用户)

### 1. 安装系统依赖

```bash
# 更新系统
sudo apt-get update

# 安装基础依赖
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    wget curl unzip xvfb \
    fonts-liberation libasound2 \
    libatk-bridge2.0-0 libdrm2 \
    libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libxss1 libnss3
```

### 2. 安装Google Chrome

```bash
# 下载Chrome
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 安装Chrome
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y  # 修复依赖
```

### 3. 设置Python环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装Python依赖
pip install DrissionPage>=4.0.0 python-dotenv>=1.0.0 selenium>=4.15.0
```

### 4. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑配置 (填写您的登录信息)
nano .env
```

## 📝 配置文件说明

### 必填配置项

```env
# 登录信息 (必须填写)
EMAIL=your_email@example.com
PASSWORD=your_password

# 产品URL (根据需要修改)
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229
```

### 性能优化配置

```env
# 基础性能配置
HEADLESS_MODE=True          # 无头模式 (服务器推荐)
DELAY_TIME=0.3              # 操作延迟时间
STOCK_CHECK_INTERVAL=0.2    # 库存检查间隔
CONCURRENT_BROWSERS=3       # 并发浏览器数量

# 高级配置
ELEMENT_TIMEOUT=2           # 元素查找超时
PAGE_LOAD_TIMEOUT=10        # 页面加载超时
FAST_MODE=True              # 快速模式
QUICK_PURCHASE=True         # 快速购买
```

### 网络环境调优

```env
# 网络良好 (延迟 < 20ms)
DELAY_TIME=0.1
STOCK_CHECK_INTERVAL=0.1
CONCURRENT_BROWSERS=5

# 网络一般 (延迟 20-50ms)
DELAY_TIME=0.3
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3

# 网络较差 (延迟 > 50ms)
DELAY_TIME=0.5
STOCK_CHECK_INTERVAL=0.5
CONCURRENT_BROWSERS=1
```

## 🎮 运行方式

### 1. 交互式运行 (推荐测试)

```bash
# 使用快速启动脚本
./run.sh

# 或直接运行
source venv/bin/activate
python quick_start.py
```

### 2. 后台运行 (推荐生产)

```bash
# 启动后台服务
./daemon.sh start

# 查看服务状态
./daemon.sh status

# 停止服务
./daemon.sh stop

# 重启服务
./daemon.sh restart

# 查看日志
tail -f grabber.log
```

### 3. 系统服务 (开机自启)

```bash
# 启动系统服务
sudo systemctl start whcms-grabber

# 设置开机自启
sudo systemctl enable whcms-grabber

# 查看服务状态
sudo systemctl status whcms-grabber

# 查看服务日志
sudo journalctl -u whcms-grabber -f
```

## 🔧 故障排除

### 常见问题

#### 1. Chrome启动失败
```bash
# 检查Chrome安装
google-chrome --version

# 检查依赖
sudo apt-get install -f

# 重新安装Chrome
sudo apt-get remove google-chrome-stable
# 然后重新安装
```

#### 2. 虚拟显示问题
```bash
# 检查Xvfb
ps aux | grep Xvfb

# 手动启动虚拟显示
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
```

#### 3. Python依赖问题
```bash
# 重新创建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. 权限问题
```bash
# 确保脚本有执行权限
chmod +x *.sh

# 检查文件所有者
ls -la
```

### 日志查看

```bash
# 部署日志
cat deploy.log

# 运行日志
tail -f grabber.log

# 系统服务日志
sudo journalctl -u whcms-grabber -f
```

## 📊 性能监控

### 系统资源监控

```bash
# 查看CPU和内存使用
htop

# 查看进程
ps aux | grep python

# 查看网络连接
netstat -tulpn | grep python
```

### 应用性能监控

```bash
# 查看抢单统计
grep "成功" grabber.log | tail -10

# 查看错误信息
grep "错误\|失败" grabber.log | tail -10

# 实时监控日志
tail -f grabber.log | grep -E "成功|失败|错误"
```

## 🔒 安全建议

### 1. 用户权限
- ❌ 不要使用root用户运行
- ✅ 创建专用用户账户
- ✅ 设置适当的文件权限

### 2. 网络安全
- ✅ 使用HTTPS连接
- ✅ 定期更新系统和依赖
- ✅ 配置防火墙规则

### 3. 数据保护
- ✅ 加密存储敏感信息
- ✅ 定期备份配置文件
- ✅ 使用强密码

## 🚀 性能优化

### 1. 系统级优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化网络参数
echo "net.core.rmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. 应用级优化
- 🎯 根据网络环境调整检查间隔
- 🎯 合理设置并发浏览器数量
- 🎯 使用无头模式减少资源消耗
- 🎯 定期重启服务清理内存

## 📞 技术支持

### 获取帮助
1. 查看日志文件定位问题
2. 检查配置文件是否正确
3. 验证网络连接状态
4. 确认系统资源充足

### 常用命令
```bash
# 快速诊断
./daemon.sh status
tail -20 grabber.log
ps aux | grep python
free -h
df -h
```

---

## 🎉 部署完成

恭喜！您已成功在Linux系统上部署WHCMS Auto Grabber。

**下一步:**
1. ✅ 配置 `.env` 文件
2. ✅ 测试运行 `./run.sh`
3. ✅ 启动后台服务 `./daemon.sh start`
4. ✅ 监控运行状态

**祝您抢单成功！** 🚀
