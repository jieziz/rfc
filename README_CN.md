# 🚀 RFC 自动抢购脚本

一个专为RFC/WHCMS设计的高性能自动抢购工具，支持多种抢购策略和智能优化。

## ✨ 主要特色

- 🚀 **多种抢购模式** - 简化快速、极速、稳定、并发等多种模式
- ⚡ **极速响应** - 最快0.05秒检测库存变化
- 🔄 **智能并发** - 支持多浏览器同时抢购
- 🧠 **自动优化** - 根据网络环境自动调整参数
- 🛡️ **故障恢复** - 自动检测并恢复异常状态
- 📊 **实时监控** - 详细的运行状态和性能数据
- 🎯 **一键部署** - Windows和Linux全自动部署
- ⏱️ **精确计时** - 内置高精度时间测量工具

## 🚀 快速上手

### Windows 用户（推荐）

1. **安装Git Bash**
   - 下载：https://git-scm.com/download/win
   - 安装时选择默认选项

2. **运行部署脚本**
   ```bash
   # 下载并运行部署脚本
   curl -O https://raw.githubusercontent.com/your-repo/rfc/main/deploy_gitbash.sh
   chmod +x deploy_gitbash.sh
   ./deploy_gitbash.sh
   ```

3. **按提示配置**
   - 输入邮箱账号
   - 输入密码
   - 输入商品PID
   - 确认信息并开始部署

4. **选择模式开始抢购**

### Linux 用户

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/rfc.git
cd rfc

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件

# 4. 启动程序
python quick_start.py
```

## 📋 抢购模式选择

### 推荐模式

| 模式 | 特点 | 适用场景 | 推荐度 |
|------|------|----------|--------|
| **简化快速** | 最稳定的快速版本 | 日常使用，新手推荐 | ⭐⭐⭐⭐⭐ |
| **快速模式** | 速度与稳定性平衡 | 网络良好时使用 | ⭐⭐⭐⭐ |
| **稳定模式** | 超高稳定性 | 网络不稳定时使用 | ⭐⭐⭐⭐ |

### 高级模式

| 模式 | 特点 | 适用场景 | 推荐度 |
|------|------|----------|--------|
| **极速模式** | 最快检测速度 | 网络优秀，高配置机器 | ⭐⭐⭐ |
| **并发模式** | 多浏览器同时抢购 | 高性能需求 | ⭐⭐⭐⭐ |

## ⚙️ 配置说明

### 基础配置 (.env 文件)

```env
# 必填项目
EMAIL=你的邮箱@example.com
PASSWORD=你的密码
PRODUCT_URL=https://my.rfchost.com/cart.php?a=add&pid=229

# 可选配置
HEADLESS_MODE=True          # 无头模式（不显示浏览器窗口）
DELAY_TIME=0.3              # 操作延迟时间（秒）
STOCK_CHECK_INTERVAL=0.2    # 库存检查间隔（秒）
CONCURRENT_BROWSERS=3       # 并发浏览器数量
```

### 网络环境优化

```env
# 网络良好（延迟 < 20ms）
DELAY_TIME=0.1
STOCK_CHECK_INTERVAL=0.1
CONCURRENT_BROWSERS=5

# 网络一般（延迟 20-50ms）
DELAY_TIME=0.3
STOCK_CHECK_INTERVAL=0.2
CONCURRENT_BROWSERS=3

# 网络较差（延迟 > 50ms）
DELAY_TIME=0.5
STOCK_CHECK_INTERVAL=0.5
CONCURRENT_BROWSERS=1
```

## 🎯 使用方法

### 1. 交互式启动（推荐新手）
```bash
python quick_start.py
```
然后按照菜单选择合适的模式。

### 2. 直接启动特定模式
```bash
# 简化快速模式（最推荐）
python simple_fast_grabber.py

# 稳定模式
python stable_grabber.py

# 并发模式
python concurrent_grabber.py
```

### 3. 原版兼容模式
```bash
python auto.py
```

## 📊 性能监控

### 实时状态显示
- ✅ 检查次数统计
- ✅ 成功率监控  
- ✅ 平均响应时间
- ✅ 错误率统计

### 示例输出
```
📊 已检查 100 次，成功 0 次，速度 25.00 次/秒
📊 平均响应时间: 0.05秒
📊 成功率: 0.00%，错误率: 0.00%
```

## 🔧 常见问题

### 1. Chrome浏览器问题
```bash
# 重新安装Chrome（Linux）
sudo apt-get remove google-chrome-stable
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### 2. Python依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或者重建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux
# 或 source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
```

### 3. 配置文件问题
```bash
# 重新创建配置文件
cp .env.example .env
# 然后编辑 .env 文件填入正确信息
```

### 4. 权限问题（Linux）
```bash
# 添加执行权限
chmod +x *.sh
```

## 📁 文件说明

### 核心脚本
- `quick_start.py` - 快速启动菜单（推荐使用）
- `simple_fast_grabber.py` - 简化快速抢购（最稳定）
- `super_grabber.py` - 超级抢购器（多模式）
- `stable_grabber.py` - 稳定版抢购
- `concurrent_grabber.py` - 并发抢购
- `auto.py` - 原版脚本

### 工具模块
- `TimePinner.py` - 时间测量工具
- `browser_pool.py` - 浏览器池管理
- `performance_config.py` - 性能配置管理

### 部署脚本
- `deploy_gitbash.sh` - Windows自动部署
- `deploy.sh` - Linux自动部署
- `check_install.sh` - 安装检查

## 💡 使用建议

### 新手用户
1. ✅ 使用Windows Git Bash部署脚本
2. ✅ 选择"简化快速模式"
3. ✅ 先测试运行确保配置正确
4. ✅ 观察日志输出调整参数

### 进阶用户
1. ✅ 根据网络环境选择合适模式
2. ✅ 调整并发浏览器数量
3. ✅ 使用并发模式提高成功率
4. ✅ 监控系统资源使用情况

### 性能优化
1. ✅ 使用有线网络连接
2. ✅ 关闭不必要的后台程序
3. ✅ 确保充足的内存和CPU资源
4. ✅ 根据实际情况调整检查间隔

## 🆘 获取帮助

### 查看日志
```bash
# 查看运行日志
tail -f grabber.log

# 查看部署日志  
cat deploy.log
```

### 系统检查
```bash
# 检查安装状态
./check_install.sh

# 检查系统资源
free -h && df -h

# 检查进程状态
ps aux | grep python
```

## ⚠️ 重要提醒

1. **合法使用** - 请遵守网站使用条款和相关法律法规
2. **测试先行** - 建议先在测试环境验证配置
3. **网络稳定** - 确保网络连接稳定，避免频繁断线
4. **适度使用** - 避免过于频繁的请求，以免被网站限制

## 📞 技术支持

- 📧 邮箱支持: support@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/rfc/issues)
- 📚 详细文档: [查看完整文档](README.md)

---

**祝您抢单成功！** 🎯🚀
