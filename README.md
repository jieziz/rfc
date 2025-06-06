# 🚀 RFC Auto Grabber

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](README.md)
[![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)](README.md)
[![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)](README.md)

一个高性能的RFC/WHCMS自动抢购脚本，支持多种抢购模式和智能优化策略。

> 🎯 **专业级抢购工具** - 为RFC/WHCMS平台量身定制，支持极速抢购和智能优化
>
> 🔥 **一键部署** - 统一部署脚本，支持跨平台自动化安装
>
> 🛡️ **源码保护** - 支持二进制编译，完全保护核心算法

## ✨ 特性

- 🚀 **多种抢购模式** - 从稳定到极速，满足不同网络环境需求
- ⚡ **极速响应** - 最快0.05秒库存检测响应时间
- 🔄 **并发抢购** - 支持多浏览器并发抢单
- 🧠 **智能优化** - 自动性能配置和浏览器池管理
- 🛡️ **故障恢复** - 自动故障检测和恢复机制
- 📊 **实时监控** - 详细的性能监控和日志记录
- 🎯 **统一部署** - 单一脚本支持跨平台自动部署
- ⏱️ **时间测量** - 内置高精度时间测量工具
- 📦 **模块化设计** - 清晰的分层架构，易于维护和扩展

## 🚀 快速开始

### 🌟 方式一：一键安装 (用户推荐)

**一条命令完成所有安装，无需克隆项目：**

```bash
# 一键安装命令 (推荐)
bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/install.sh)
```

> 🎯 **超级简单**:
> - 🚀 **零配置** - 一条命令搞定一切
> - 🌐 **远程安装** - 无需手动下载项目
> - 🔄 **自动检测** - 智能识别系统环境
> - 📦 **完整部署** - 自动安装所有依赖

### 🛡️ 方式二：二进制版本 (源码保护)

**适合需要保护源码的场景：**

```bash
# 二进制版本一键安装
bash <(curl -Ls https://your-domain.com/install_binary.sh)
```

> 🔒 **源码保护特性**:
> - 🛡️ **完全保护** - 用户无法查看Python源码
> - 🚀 **无需环境** - 用户无需安装Python和依赖
> - 📦 **开箱即用** - 下载即可使用
> - 🌐 **跨平台** - 支持Windows/Linux/macOS

### 🔧 方式三：开发者部署

如果您是开发者或需要自定义：

```bash
# 1. 克隆项目
git clone https://github.com/jieziz/rfc.git
cd rfc

# 2. 运行统一部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 3. 按提示输入配置信息
# 4. 选择启动模式开始抢购
```

> 💡 **支持平台**:
> - ✅ **Windows** (Git Bash/Cygwin)
> - ✅ **Linux** (Ubuntu/Debian/CentOS/RHEL)
> - ✅ **macOS** (Homebrew支持)

## 📋 抢购模式

| 模式 | 描述 | 适用场景 | 推荐指数 |
|------|------|----------|----------|
| **简化快速模式** | 最稳定的快速版本 (强烈推荐) | 日常使用 | ⭐⭐⭐⭐⭐ |
| **稳定模式** | 超高稳定性，确保登录 | 网络不稳定 | ⭐⭐⭐⭐ |
| **并发模式** | 多浏览器并发抢单 | 高性能机器 | ⭐⭐⭐ |

> 💡 **推荐使用**: 大多数情况下建议使用 **简化快速模式**，它经过优化，兼顾了速度和稳定性

## 🛠️ 安装要求

### 系统要求
- **Windows**: Windows 10+ (支持Git Bash)
- **Linux**: Ubuntu 18.04+ / Debian 10+ / CentOS 7+
- **macOS**: macOS 10.14+
- **内存**: 4GB+ (推荐8GB)
- **存储**: 2GB+ 可用空间

### 软件依赖
- Python 3.8+ (支持3.8-3.12)
- Chrome浏览器 (自动安装ChromeDriver)
- Git (用于克隆项目)

### 多平台支持详情
部署脚本会根据操作系统自动安装依赖：

**Windows (Git Bash/Cygwin)**:
- 跳过系统依赖安装，使用现有环境
- 自动检测Python和pip命令

**Linux (Ubuntu/Debian)**:
- 自动安装: `python3-venv`, `python3-dev`, `wget`, `curl`, `unzip`
- 浏览器支持: `xvfb`, `chromium-browser`
- 图形界面依赖: `fonts-liberation`, `libnss3`等

**Linux (CentOS/RHEL)**:
- 自动安装: `python3-devel`, `wget`, `curl`, `unzip`
- 浏览器支持: `chromium`

**macOS**:
- 检测并提示安装Homebrew
- 支持通过brew安装chromium

## 📁 项目结构

```
rfc/
├── 📄 核心文件
│   ├── quick_start.py              # 主启动器 (推荐入口)
│   ├── install.sh                  # 一键安装脚本
│   ├── install_binary.sh           # 二进制版本安装脚本
│   └── README.md                   # 项目说明 (本文件)
│
├── 🐍 源代码
│   └── src/                        # 源代码目录
│       ├── core/                   # 核心模块 (浏览器池、性能配置)
│       ├── grabbers/               # 抢购脚本 (快速、稳定、并发模式)
│       └── utils/                  # 工具模块 (时间测量等)
│
├── 🔨 构建脚本
│   └── scripts/
│       ├── build_release.sh        # Linux/macOS构建脚本
│       ├── build_release.bat       # Windows构建脚本
│       └── deploy.sh               # 统一部署脚本
│
├── ⚙️ 配置
│   ├── config/requirements.txt     # Python依赖
│   ├── Makefile                    # 构建命令
│   └── .gitignore                  # Git忽略规则
│
└── 📚 文档
    ├── docs/                       # 详细文档
    └── LICENSE                     # MIT许可证
```

## 🛡️ 源码保护 (开发者专用)

### 🔨 二进制编译构建

如果您需要保护源码不被泄露，可以将项目编译为二进制文件：

#### Windows 环境构建
```batch
# 进入项目目录
cd C:\Users\vedeng\Desktop\rfc

# 运行Windows构建脚本
scripts\build_release.bat
```

#### Linux/macOS 环境构建
```bash
# 给脚本执行权限
chmod +x scripts/build_release.sh

# 运行构建脚本
./scripts/build_release.sh
```

#### 构建产物
构建完成后，`release/` 目录将包含：
- `rfc-grabber.exe` - 主程序
- `fast-grabber.exe` - 快速模式
- `stable-grabber.exe` - 稳定模式
- `concurrent-grabber.exe` - 并发模式
- `.env.template` - 配置模板
- `start.bat/start.sh` - 启动脚本

#### 分发部署
1. 上传构建包到GitHub Releases或您的服务器
2. 修改 `install_binary.sh` 中的下载地址
3. 提供一键安装命令给用户

> 🔒 **保护效果**:
> - ✅ 源码完全不可见
> - ✅ 无法反编译查看Python代码
> - ✅ 用户无需Python环境
> - ✅ 保持一键安装体验

## 🎯 使用示例

### 1. 快速启动 (推荐)
```bash
python quick_start.py
```
> 💡 交互式界面，提供3个核心模式选择

### 2. 直接启动特定模式
```bash
# 快速模式 (推荐)
python src/grabbers/simple_fast_grabber.py

# 稳定模式
python src/grabbers/stable_grabber.py

# 并发模式
python src/grabbers/concurrent_grabber.py
```

## 🔍 故障排除

### 常见问题

1. **一键安装失败**
   ```bash
   # 检查网络连接
   curl -I https://raw.githubusercontent.com/jieziz/rfc/main/install.sh

   # 手动下载并执行
   wget https://raw.githubusercontent.com/jieziz/rfc/main/install.sh
   chmod +x install.sh
   ./install.sh
   ```

2. **Chrome启动失败**
   ```bash
   # Ubuntu/Debian安装Chromium
   sudo apt-get update
   sudo apt-get install -y chromium-browser

   # CentOS/RHEL安装Chromium
   sudo yum install -y chromium

   # macOS使用Homebrew
   brew install --cask chromium
   ```

### 🐧 Linux无头模式检查

在Linux服务器环境中，由于没有图形界面，需要特殊方法确认浏览器是否正常运行：

#### 系统级检查
```bash
# 检查浏览器进程
ps aux | grep -i chrome | grep headless

# 查看应用日志
tail -f simple_fast.log
tail -f stable_grabber.log
tail -f concurrent_log.log

# 搜索关键信息
grep -i "浏览器" *.log
grep -i "登录" *.log
```

> 💡 **检查要点**:
> - ✅ 能检测到Chrome/Chromium进程
> - ✅ 进程包含`--headless`和`--no-sandbox`参数
> - ✅ CPU和内存使用正常
> - ✅ 日志中显示"浏览器设置完成"、"登录成功"等信息
> - ✅ 无严重错误信息

详细的Linux无头模式配置和故障排除，请参考：[Linux无头模式指南](docs/LINUX_HEADLESS_GUIDE.md)

## 🆕 最新改进

### v2.0.0 主要更新
- ✅ **一键安装** - 新增远程一条命令安装功能
- ✅ **简化模式选择** - 从9个模式精简为3个核心模式
- ✅ **统一启动器** - 单一入口点，交互式模式选择
- ✅ **统一部署脚本** - 整合多平台部署功能，简化安装流程
- ✅ **模块化架构** - 重构代码结构，提高可维护性
- ✅ **包管理器支持** - 支持pip安装和命令行启动
- ✅ **增强错误处理** - 改进故障检测和恢复机制
- ✅ **性能优化** - 优化浏览器池管理和资源使用

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本工具仅供学习和研究使用，请遵守相关网站的使用条款和法律法规。使用者需要自行承担使用风险。

---

**祝您抢单成功！** 🎯
