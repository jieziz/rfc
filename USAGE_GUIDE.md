# 📖 RFC Auto Grabber - 使用指南

## 🚀 快速开始

### 用户安装

**方式一：一键安装（推荐）**
```bash
bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/install.sh)
```

**方式二：二进制版本（源码保护）**
```bash
bash <(curl -Ls https://your-domain.com/install_binary.sh)
```

### 开发者部署

```bash
# 1. 克隆项目
git clone https://github.com/jieziz/rfc.git
cd rfc

# 2. 运行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🎯 使用方法

### 启动程序

```bash
# 交互式启动（推荐）
python quick_start.py

# 直接启动特定模式
python src/grabbers/simple_fast_grabber.py    # 快速模式
python src/grabbers/stable_grabber.py         # 稳定模式
python src/grabbers/concurrent_grabber.py     # 并发模式
```

### 配置文件

编辑 `.env` 文件：
```env
# 基础配置
EMAIL=your_email@example.com
PASSWORD=your_password
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229

# 性能配置
HEADLESS_MODE=True
DELAY_TIME=0.3
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3
```

## 🛡️ 源码保护（开发者）

### 构建二进制文件

**Windows：**
```batch
scripts\build_release.bat
```

**Linux/macOS：**
```bash
chmod +x scripts/build_release.sh
./scripts/build_release.sh
```

### 分发部署

1. 上传构建包到发布平台
2. 修改 `install_binary.sh` 中的下载地址
3. 提供一键安装命令

## 🔧 常用命令

```bash
# 清理临时文件
make clean

# 安装依赖
make install

# 运行程序
make run

# 检查状态
./scripts/deploy.sh --check
```

## 🔍 故障排除

### 常见问题

**安装失败：**
```bash
# 检查网络连接
curl -I https://raw.githubusercontent.com/jieziz/rfc/main/install.sh

# 手动安装
wget https://raw.githubusercontent.com/jieziz/rfc/main/install.sh
chmod +x install.sh
./install.sh
```

**浏览器问题：**
```bash
# Ubuntu/Debian
sudo apt-get install -y chromium-browser

# CentOS/RHEL
sudo yum install -y chromium

# macOS
brew install --cask chromium
```

## 📋 抢购模式

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| 快速模式 | 平衡速度和稳定性 | 日常使用（推荐） |
| 稳定模式 | 超高稳定性 | 网络不稳定时 |
| 并发模式 | 多浏览器并发 | 高性能机器 |

## ⚠️ 注意事项

1. 请遵守网站使用条款
2. 确保网络连接稳定
3. 建议使用Chrome或Chromium浏览器
4. 首次运行可能需要下载浏览器驱动

## 📞 技术支持

- 查看日志：`tail -f *.log`
- 检查进程：`ps aux | grep python`
- 系统资源：`free -h && df -h`

---

**祝您使用愉快！** 🎯
