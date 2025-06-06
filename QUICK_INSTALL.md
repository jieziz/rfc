# 🚀 RFC Auto Grabber - 一键安装指南

## 🌟 超级简单的一键安装

**只需要一条命令，无需任何准备工作：**

```bash
bash <(curl -Ls https://raw.githubusercontent.com/jieziz/rfc/main/install.sh)
```

就是这么简单！🎉

## 📋 安装过程说明

运行上面的命令后，脚本会自动：

1. **检测系统环境** - 自动识别 Windows/Linux/macOS
2. **创建安装目录** - 在用户目录下创建 `rfc-auto-grabber` 文件夹
3. **下载项目代码** - 从GitHub拉取最新代码
4. **安装依赖** - 自动安装Python依赖和系统依赖
5. **配置环境** - 创建虚拟环境和配置文件
6. **交互式配置** - 引导您输入邮箱、密码、商品PID等信息
7. **启动程序** - 可选择立即启动抢购程序

## 🎯 使用方法

安装完成后，您可以通过以下方式启动：

### 方式1: 使用启动脚本 (推荐)
```bash
~/rfc-auto-grabber/start_grabber.sh
```

### 方式2: 手动启动
```bash
cd ~/rfc-auto-grabber/rfc_repo
source ~/rfc-auto-grabber/venv/bin/activate
python quick_start.py
```

## 🔧 系统要求

- **操作系统**: Windows 10+ (Git Bash) / Linux / macOS
- **软件**: Git, curl (通常系统自带)
- **网络**: 稳定的互联网连接

## ❓ 常见问题

### Q: 安装失败怎么办？
A: 检查网络连接，确保能访问GitHub。也可以手动下载脚本：
```bash
wget https://raw.githubusercontent.com/jieziz/rfc/main/install.sh
chmod +x install.sh
./install.sh
```

### Q: Windows用户如何使用？
A: 在Git Bash中运行命令，不要在PowerShell或CMD中运行。

### Q: 安装在哪里？
A: 默认安装在 `~/rfc-auto-grabber/` 目录下。

### Q: 如何卸载？
A: 直接删除安装目录即可：
```bash
rm -rf ~/rfc-auto-grabber
```

## 🎉 就是这么简单！

一条命令，几分钟时间，您就可以开始使用专业级的RFC抢购工具了！

---

**祝您抢单成功！** 🚀
