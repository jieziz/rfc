# 🚀 WHCMS Auto Grabber - Linux 安装指南

## 📦 快速安装 (推荐)

### 一键部署
```bash
# 给脚本执行权限
chmod +x quick_deploy.sh

# 运行快速部署
./quick_deploy.sh
```

### 配置和启动
```bash
# 1. 配置登录信息
cp .env.example .env
nano .env  # 编辑配置文件

# 2. 检查安装
./check_install.sh

# 3. 启动程序
./run.sh          # 交互式运行
./daemon.sh start # 后台运行
```

## 📋 详细步骤

### 1. 系统要求
- **操作系统**: Debian 10+ / Ubuntu 18.04+
- **内存**: 4GB+ (推荐8GB)
- **存储**: 2GB+ 可用空间
- **网络**: 稳定的互联网连接

### 2. 部署选项

#### 选项A: 完整部署 (新手推荐)
```bash
chmod +x deploy.sh
./deploy.sh
```
- ✅ 完整的系统检查
- ✅ 自动创建systemd服务
- ✅ 详细的错误处理

#### 选项B: 快速部署 (经验用户)
```bash
chmod +x quick_deploy.sh
./quick_deploy.sh
```
- ⚡ 5分钟快速安装
- 🎯 专注核心功能

### 3. 配置文件

编辑 `.env` 文件，填写必要信息：

```env
# 必填项
EMAIL=your_email@example.com
PASSWORD=your_password
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229

# 性能配置 (可选)
HEADLESS_MODE=True
DELAY_TIME=0.3
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3
```

### 4. 运行程序

#### 交互式运行 (测试推荐)
```bash
./run.sh
```

#### 后台运行 (生产推荐)
```bash
./daemon.sh start    # 启动
./daemon.sh status   # 状态
./daemon.sh stop     # 停止
./daemon.sh restart  # 重启
```

#### 系统服务 (开机自启)
```bash
sudo systemctl start whcms-grabber
sudo systemctl enable whcms-grabber
```

## 🔧 故障排除

### 检查安装状态
```bash
./check_install.sh
```

### 常见问题

#### 1. Chrome启动失败
```bash
# 重新安装Chrome
sudo apt-get remove google-chrome-stable
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

#### 2. Python依赖问题
```bash
# 重建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. 权限问题
```bash
# 添加执行权限
chmod +x *.sh
```

#### 4. 虚拟显示问题
```bash
# 检查Xvfb
ps aux | grep Xvfb
sudo apt-get install xvfb
```

### 查看日志
```bash
# 运行日志
tail -f grabber.log

# 部署日志
cat deploy.log

# 系统服务日志
sudo journalctl -u whcms-grabber -f
```

## 📊 性能优化

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

### 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 重启生效
sudo reboot
```

## 📁 文件结构

```
whcms-auto/rfc/
├── deploy.sh              # 完整部署脚本
├── quick_deploy.sh         # 快速部署脚本
├── check_install.sh        # 安装检查脚本
├── run.sh                  # 交互式启动脚本
├── daemon.sh               # 后台服务脚本
├── .env.example            # 配置文件示例
├── requirements.txt        # Python依赖
├── README_Linux部署指南.md  # 详细部署指南
└── INSTALL.md             # 本文件
```

## 🎯 使用建议

### 首次使用
1. ✅ 运行快速部署脚本
2. ✅ 配置 `.env` 文件
3. ✅ 运行安装检查
4. ✅ 交互式测试运行
5. ✅ 确认无误后启动后台服务

### 生产环境
1. ✅ 使用后台运行模式
2. ✅ 设置系统服务自启
3. ✅ 定期检查日志
4. ✅ 监控系统资源

### 安全建议
1. ✅ 不要使用root用户运行
2. ✅ 定期更新系统和依赖
3. ✅ 使用强密码
4. ✅ 配置防火墙

## 📞 获取帮助

### 自助诊断
```bash
# 1. 检查安装状态
./check_install.sh

# 2. 查看运行日志
tail -20 grabber.log

# 3. 检查系统资源
free -h && df -h

# 4. 检查进程状态
ps aux | grep python
```

### 常用命令
```bash
# 服务管理
./daemon.sh status
./daemon.sh restart

# 日志监控
tail -f grabber.log | grep -E "成功|失败|错误"

# 系统监控
htop
netstat -tulpn | grep python
```

---

## 🎉 安装完成

恭喜！您已成功安装WHCMS Auto Grabber。

**下一步:**
1. 📝 配置 `.env` 文件
2. 🧪 运行 `./run.sh` 测试
3. 🚀 启动 `./daemon.sh start` 后台服务
4. 📊 监控 `tail -f grabber.log` 运行状态

**祝您抢单成功！** 🎯
