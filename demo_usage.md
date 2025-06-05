# RFC Auto Grabber 部署脚本演示

## 🎯 演示场景

假设您是一个Windows用户，想要使用RFC抢购脚本，以下是完整的使用流程：

## 📋 准备工作

### 1. 安装必要工具

**Git for Windows**（包含Git Bash）：
- 访问：https://git-scm.com/download/win
- 下载并安装，安装时选择默认选项即可

**Python 3.8+**：
- 访问：https://www.python.org/downloads/
- 下载最新版本
- 安装时**务必勾选**"Add Python to PATH"

### 2. 验证安装

打开Git Bash，运行以下命令验证：

```bash
git --version
python --version
pip --version
```

如果都能正常显示版本号，说明安装成功。

## 🚀 使用部署脚本

### 步骤1：下载部署脚本

创建一个新文件夹，比如 `rfc_grabber`，然后将部署脚本放入其中。

### 步骤2：运行部署脚本

在Git Bash中进入脚本目录：

```bash
cd /c/Users/YourName/rfc_grabber  # 替换为您的实际路径
```

给脚本添加执行权限：

```bash
chmod +x deploy_gitbash.sh
```

运行部署脚本：

```bash
./deploy_gitbash.sh
```

### 步骤3：按提示输入信息

脚本会依次提示您输入：

1. **邮箱账号**：
   ```
   请输入您的邮箱账号: user@example.com
   ```

2. **密码**（隐藏输入）：
   ```
   请输入您的密码: [输入时不会显示]
   请再次确认密码: [再次输入确认]
   ```

3. **商品PID**：
   ```
   请输入要抢购的商品PID: 229
   ```

4. **确认信息**：
   ```
   请确认您的配置信息：
   邮箱: user@example.com
   密码: ********
   商品PID: 229

   确认信息正确？(y/n): y
   ```

## 📊 部署过程演示

部署过程中您会看到类似以下的输出：

```bash
==============================================
    RFC Auto Grabber - Git Bash 部署脚本
    支持从GitHub自动拉取并配置启动
==============================================

🔄 [2024-01-15 10:30:00] 检查必要工具...
✅ [2024-01-15 10:30:01] Git 已安装: git version 2.42.0.windows.2
✅ [2024-01-15 10:30:01] Python 已安装: Python 3.11.5
✅ [2024-01-15 10:30:01] Pip 已安装: pip 23.2.1
✅ [2024-01-15 10:30:01] 所有必要工具已安装

🔄 [2024-01-15 10:30:01] 获取最新代码...
ℹ️  [2024-01-15 10:30:01] 克隆仓库...
Cloning into 'rfc_repo'...
✅ [2024-01-15 10:30:05] 代码克隆完成
ℹ️  [2024-01-15 10:30:05] 当前代码版本: a1b2c3d

🔄 [2024-01-15 10:30:05] 收集用户配置信息...
ℹ️  [2024-01-15 10:30:05] 请输入以下信息来配置抢购脚本：

请输入您的邮箱账号: user@example.com
请输入您的密码: 
请再次确认密码: 
请输入要抢购的商品PID: 229

ℹ️  [2024-01-15 10:30:30] 请确认您的配置信息：
邮箱: user@example.com
密码: ********
商品PID: 229

确认信息正确？(y/n): y
✅ [2024-01-15 10:30:32] 用户配置收集完成

🔄 [2024-01-15 10:30:32] 生成配置文件...
✅ [2024-01-15 10:30:32] 配置文件生成完成: /c/Users/YourName/rfc_grabber/rfc_repo/.env

🔄 [2024-01-15 10:30:32] 创建Python虚拟环境...
✅ [2024-01-15 10:30:35] Python虚拟环境创建完成

🔄 [2024-01-15 10:30:35] 安装Python依赖包...
ℹ️  [2024-01-15 10:30:35] 使用项目的 requirements.txt
Collecting DrissionPage>=4.0.0
...
✅ [2024-01-15 10:31:20] Python依赖安装完成

🔄 [2024-01-15 10:31:20] 运行系统测试...
ℹ️  [2024-01-15 10:31:20] 测试Python环境...
Python版本: 3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)]
ℹ️  [2024-01-15 10:31:20] 测试依赖包...
✅ DrissionPage 导入成功
✅ python-dotenv 导入成功
✅ selenium 导入成功
✅ [2024-01-15 10:31:21] 配置文件存在
✅ 配置文件验证通过
✅ [2024-01-15 10:31:21] 系统测试完成

🔄 [2024-01-15 10:31:21] 创建启动脚本...
✅ [2024-01-15 10:31:21] 启动脚本创建完成
ℹ️  [2024-01-15 10:31:21] Windows启动脚本: /c/Users/YourName/rfc_grabber/start_grabber.bat
ℹ️  [2024-01-15 10:31:21] Git Bash启动脚本: /c/Users/YourName/rfc_grabber/start_grabber.sh

✅ [2024-01-15 10:31:21] 🎉 部署完成！

项目信息：
  - 代码目录: /c/Users/YourName/rfc_grabber/rfc_repo
  - 虚拟环境: /c/Users/YourName/rfc_grabber/venv
  - 配置文件: /c/Users/YourName/rfc_grabber/rfc_repo/.env
  - 日志文件: /c/Users/YourName/rfc_grabber/deploy.log

使用方法：
  1. Git Bash 启动（推荐）:
     /c/Users/YourName/rfc_grabber/start_grabber.sh

  2. Windows CMD 启动:
     /c/Users/YourName/rfc_grabber/start_grabber.bat

  3. 手动启动:
     cd /c/Users/YourName/rfc_grabber/rfc_repo
     source /c/Users/YourName/rfc_grabber/venv/Scripts/activate
     python quick_start.py

配置信息：
  - 邮箱: user@example.com
  - 商品PID: 229
  - 产品URL: https://my.rfchost.com/cart.php?a=add&pid=229

⚠️  重要提醒：
  - 配置已自动生成，如需修改请编辑 /c/Users/YourName/rfc_grabber/rfc_repo/.env
  - 建议先测试运行确保配置正确
  - 抢购时请确保网络稳定
  - Windows环境建议安装Chrome浏览器

✅ [2024-01-15 10:31:21] 祝您抢单成功！🚀

🔄 [2024-01-15 10:31:21] 是否立即启动抢购程序？
(y/n): y
```

## 🎮 启动抢购程序

如果选择立即启动，会看到：

```bash
🔄 [2024-01-15 10:31:25] 启动抢购应用程序...
✅ [2024-01-15 10:31:25] 配置完成，准备启动抢购程序...

ℹ️  [2024-01-15 10:31:25] 启动选项：
1. 快速启动（推荐）- 使用 quick_start.py
2. 简化快速模式 - 使用 simple_fast_grabber.py
3. 原版模式 - 使用 auto.py
4. 退出

请选择启动方式 (1-4): 1

ℹ️  [2024-01-15 10:31:27] 启动快速启动程序...

╔══════════════════════════════════════════════════════════════╗
║                    🚀 超级抢单器 v2.0                        ║
║                   Speed Optimized Grabber                   ║
╠══════════════════════════════════════════════════════════════╣
║  特性:                                                       ║
║  ✅ 极速库存检测 (0.05秒响应)                                ║
║  ✅ 并发多浏览器抢单                                         ║
║  ✅ 智能浏览器池管理                                         ║
║  ✅ 自动故障恢复                                             ║
║  ✅ 实时性能监控                                             ║
╚══════════════════════════════════════════════════════════════╝

📋 可用的抢单模式:
============================================================
1. 简化快速模式 (simple_fast)
   最稳定的快速版本 (强烈推荐)

2. 快速模式 (fast)
   平衡速度和稳定性

...

请选择模式 (1-9) 或输入 'h' 查看帮助, 'q' 退出: 1

🎯 选择了: 简化快速模式
描述: 最稳定的快速版本 (强烈推荐)

确认启动? (y/n): y

🚀 启动简化版快速抢单器...
产品URL: https://my.rfchost.com/cart.php?a=add&pid=229
检查间隔: 0.2秒
延迟时间: 0.3秒
执行快速登录...
✅ 登录成功
开始极速监控...
📊 已检查 50 次，成功 0 次，速度 25.00 次/秒
📊 已检查 100 次，成功 0 次，速度 25.00 次/秒
...
```

## 📁 生成的文件结构

部署完成后，您的目录结构如下：

```
rfc_grabber/
├── rfc_repo/                 # 从GitHub克隆的代码
│   ├── .env                  # 自动生成的配置文件
│   ├── quick_start.py        # 快速启动脚本
│   ├── auto.py              # 原版抢购脚本
│   ├── simple_fast_grabber.py # 简化快速抢购脚本
│   └── ...                  # 其他项目文件
├── venv/                    # Python虚拟环境
│   ├── Scripts/             # Windows环境
│   └── ...
├── start_grabber.sh         # 启动脚本
├── deploy.log               # 部署日志
├── deploy_gitbash.sh        # 部署脚本
└── README_部署脚本使用指南.md # 使用指南
```

## 🔄 后续使用

部署完成后，您可以：

1. **使用启动脚本**：
   ```bash
   ./start_grabber.sh
   ```

2. **手动启动**：
   ```bash
   cd rfc_repo
   source ../venv/Scripts/activate  # Windows Git Bash
   # source ../venv/bin/activate    # Linux/macOS
   python quick_start.py
   ```

3. **修改配置**：
   编辑 `rfc_repo/.env` 文件

4. **更新代码**：
   重新运行部署脚本即可自动更新

## 🎉 总结

通过这个部署脚本，您可以：
- ✅ 自动获取最新代码
- ✅ 交互式配置账号信息
- ✅ 自动安装所有依赖
- ✅ 一键启动抢购程序
- ✅ 支持多种启动方式

整个过程大约需要2-5分钟，完全自动化，无需手动配置！
