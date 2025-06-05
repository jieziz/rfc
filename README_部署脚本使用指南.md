# RFC Auto Grabber 部署脚本使用指南

## 📋 脚本概述

本项目提供了两个部署脚本，用于自动从GitHub拉取RFC抢购脚本并进行交互式配置：

1. **`deploy_gitbash.sh`** - Git Bash 专用脚本（推荐Windows用户）
2. **`deploy.sh`** - Linux/macOS 脚本

## 🚀 快速开始

### Windows 用户（推荐使用Git Bash）

1. **安装必要工具**：
   - [Git for Windows](https://git-scm.com/download/win)（包含Git Bash）
   - [Python 3.8+](https://www.python.org/downloads/)

2. **运行部署脚本**：
   ```bash
   # 在Git Bash中运行
   chmod +x deploy_gitbash.sh
   ./deploy_gitbash.sh
   ```

3. **按提示输入信息**：
   - 邮箱账号
   - 密码（隐藏输入）
   - 商品PID

### Linux/macOS 用户

1. **运行部署脚本**：
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📁 脚本功能详解

### 🔧 自动化功能

1. **环境检查**：
   - 检查Git、Python、Pip是否已安装
   - 验证工具版本兼容性

2. **代码管理**：
   - 自动从GitHub克隆最新代码
   - 如果已存在则更新到最新版本

3. **交互式配置**：
   - 安全收集用户邮箱和密码
   - 验证邮箱格式
   - 密码确认机制
   - 商品PID输入验证

4. **环境配置**：
   - 自动创建Python虚拟环境
   - 安装所有必要依赖包
   - 生成优化的.env配置文件

5. **系统测试**：
   - 验证Python环境
   - 测试依赖包导入
   - 配置文件验证

6. **启动脚本**：
   - 创建便捷的启动脚本
   - 支持多种启动方式

### 🛡️ 安全特性

- **密码隐藏输入**：输入密码时不会在屏幕上显示
- **密码确认**：需要二次输入确认密码正确性
- **输入验证**：邮箱格式和PID数字格式验证
- **错误处理**：完善的错误处理和用户提示

## 📊 生成的文件结构

部署完成后会生成以下文件结构：

```
项目目录/
├── rfc_repo/                 # 从GitHub克隆的代码
│   ├── .env                  # 自动生成的配置文件
│   ├── quick_start.py        # 快速启动脚本
│   ├── auto.py              # 原版抢购脚本
│   └── ...                  # 其他项目文件
├── venv/                    # Python虚拟环境
├── start_grabber.sh         # Git Bash启动脚本
├── start_grabber.bat        # Windows启动脚本
├── deploy.log               # 部署日志
└── deploy_gitbash.sh        # 部署脚本
```

## 🎯 使用方法

### 部署完成后启动程序

1. **使用启动脚本（推荐）**：
   ```bash
   # Git Bash / Linux / macOS
   ./start_grabber.sh
   ```

2. **手动启动**：
   ```bash
   cd rfc_repo
   source ../venv/Scripts/activate  # Windows Git Bash
   # source ../venv/bin/activate    # Linux/macOS
   python quick_start.py
   ```

### 配置文件说明

自动生成的`.env`文件包含：

```env
# 基础配置
BASE_URL=https://my.rfchost.com
LOGIN_URL=https://my.rfchost.com/clientarea.php
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=YOUR_PID

# 登录信息
EMAIL=your_email@example.com
PASSWORD=your_password

# 性能配置 - 已优化
HEADLESS_MODE=True
DELAY_TIME=0.3
ELEMENT_TIMEOUT=2
PAGE_LOAD_TIMEOUT=10
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3
FAST_MODE=True
QUICK_PURCHASE=True
```

## 🔧 故障排除

### 常见问题

1. **Git未安装**：
   - Windows: 下载安装 [Git for Windows](https://git-scm.com/download/win)
   - Linux: `sudo apt install git` 或 `sudo yum install git`
   - macOS: `brew install git`

2. **Python未安装**：
   - 下载安装 [Python 3.8+](https://www.python.org/downloads/)
   - 确保安装时勾选"Add to PATH"

3. **权限问题**：
   ```bash
   # 给脚本执行权限
   chmod +x deploy_gitbash.sh
   ```

4. **网络问题**：
   - 确保能访问GitHub
   - 检查防火墙设置
   - 考虑使用代理

5. **虚拟环境问题**：
   ```bash
   # 手动删除虚拟环境重新创建
   rm -rf venv
   ./deploy_gitbash.sh
   ```

### 日志查看

```bash
# 查看部署日志
cat deploy.log

# 查看运行日志
tail -f rfc_repo/log.log
```

## 📈 性能优化建议

1. **网络优化**：
   - 使用有线网络连接
   - 确保网络延迟低于50ms
   - 关闭其他占用带宽的应用

2. **系统优化**：
   - 关闭不必要的后台程序
   - 确保有足够的内存（建议8GB+）
   - 使用SSD硬盘

3. **浏览器优化**：
   - 安装Chrome浏览器（推荐）
   - 确保浏览器版本较新

## 🎉 成功标志

部署成功后会看到：

```
🎉 部署完成！

项目信息：
  - 代码目录: /path/to/rfc_repo
  - 虚拟环境: /path/to/venv
  - 配置文件: /path/to/rfc_repo/.env

配置信息：
  - 邮箱: your_email@example.com
  - 商品PID: 123
  - 产品URL: https://my.rfchost.com/cart.php?a=add&pid=123

祝您抢单成功！🚀
```

## 📞 技术支持

如果遇到问题：

1. 查看部署日志：`deploy.log`
2. 检查配置文件：`rfc_repo/.env`
3. 验证Python环境：`python --version`
4. 测试网络连接：`ping github.com`

---

**注意**：本脚本仅用于学习和研究目的，请遵守相关网站的使用条款和法律法规。
