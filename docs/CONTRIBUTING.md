# 🤝 贡献指南

感谢您对RFC Auto Grabber项目的关注！我们欢迎各种形式的贡献。

## 📋 贡献方式

### 🐛 报告问题
- 使用 [GitHub Issues](https://github.com/your-repo/rfc/issues) 报告bug
- 提供详细的问题描述和复现步骤
- 包含系统环境信息（操作系统、Python版本等）

### 💡 功能建议
- 在Issues中提出新功能建议
- 详细描述功能需求和使用场景
- 讨论实现方案的可行性

### 📝 改进文档
- 修正文档中的错误
- 补充缺失的说明
- 翻译文档到其他语言

### 💻 代码贡献
- 修复已知问题
- 实现新功能
- 优化性能
- 改进代码质量

## 🚀 开发流程

### 1. 准备开发环境

```bash
# 1. Fork项目到您的GitHub账户
# 2. 克隆您的fork
git clone https://github.com/your-username/rfc.git
cd rfc

# 3. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 source venv/Scripts/activate  # Windows Git Bash

# 4. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖（如果存在）

# 5. 添加上游仓库
git remote add upstream https://github.com/original-repo/rfc.git
```

### 2. 创建功能分支

```bash
# 1. 确保主分支是最新的
git checkout main
git pull upstream main

# 2. 创建新的功能分支
git checkout -b feature/your-feature-name
# 或 git checkout -b fix/issue-number
```

### 3. 开发和测试

```bash
# 1. 进行开发
# 编辑代码...

# 2. 运行测试
python -m pytest tests/  # 如果有测试

# 3. 检查代码风格
flake8 .  # 如果配置了代码检查

# 4. 测试功能
python quick_start.py  # 测试主要功能
```

### 4. 提交更改

```bash
# 1. 添加更改
git add .

# 2. 提交更改（使用清晰的提交信息）
git commit -m "feat: 添加新的抢购模式"
# 或 git commit -m "fix: 修复Chrome启动失败问题"
# 或 git commit -m "docs: 更新安装指南"
```

### 5. 推送和创建Pull Request

```bash
# 1. 推送到您的fork
git push origin feature/your-feature-name

# 2. 在GitHub上创建Pull Request
# 3. 填写PR描述，说明更改内容
```

## 📝 代码规范

### Python代码风格
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用4个空格缩进
- 行长度不超过88字符
- 使用有意义的变量和函数名

### 提交信息格式
使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<类型>(<范围>): <描述>

[可选的正文]

[可选的脚注]
```

**类型：**
- `feat`: 新功能
- `fix`: 问题修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(grabber): 添加并发抢购模式

- 支持多浏览器同时抢购
- 可配置并发数量
- 增强错误处理

Closes #123
```

### 代码注释
- 为复杂逻辑添加注释
- 使用中文注释（项目主要面向中文用户）
- 为函数和类添加文档字符串

```python
def check_stock(product_url: str) -> bool:
    """
    检查商品库存状态
    
    Args:
        product_url: 商品页面URL
        
    Returns:
        bool: True表示有库存，False表示无库存
        
    Raises:
        NetworkError: 网络连接失败时抛出
    """
    pass
```

## 🧪 测试指南

### 运行测试
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_grabber.py

# 运行并显示覆盖率
python -m pytest --cov=.
```

### 编写测试
- 为新功能编写单元测试
- 确保测试覆盖率不降低
- 使用有意义的测试名称

```python
def test_simple_fast_grabber_success():
    """测试简化快速抢购成功场景"""
    # 测试代码...
    pass
```

## 📚 文档贡献

### 文档类型
- **README.md** - 项目主要说明
- **README_CN.md** - 中文使用指南
- **INSTALL.md** - 安装指南
- **demo_usage.md** - 使用演示
- **CHANGELOG.md** - 更新日志

### 文档规范
- 使用Markdown格式
- 保持结构清晰
- 添加适当的emoji增强可读性
- 提供代码示例

## 🔍 代码审查

### 审查要点
- 功能是否正确实现
- 代码是否遵循项目规范
- 是否有充分的测试
- 文档是否完整
- 性能是否有影响

### 审查流程
1. 自动化检查（CI/CD）
2. 代码审查（人工）
3. 测试验证
4. 合并到主分支

## 🎯 贡献建议

### 适合新手的任务
- 修复文档中的错误
- 改进错误信息
- 添加代码注释
- 编写测试用例

### 进阶任务
- 实现新的抢购模式
- 优化性能
- 添加新功能
- 重构代码

### 高级任务
- 架构设计
- 安全性改进
- 跨平台兼容性
- 大型功能开发

## 📞 获取帮助

### 讨论渠道
- **GitHub Issues** - 问题报告和功能讨论
- **GitHub Discussions** - 一般讨论和问答
- **邮箱** - support@example.com

### 开发资源
- [Python官方文档](https://docs.python.org/)
- [Selenium文档](https://selenium-python.readthedocs.io/)
- [Git教程](https://git-scm.com/docs)

## 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里可以添加贡献者列表 -->

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT许可证](LICENSE) 下发布。

---

**再次感谢您的贡献！** 🙏
