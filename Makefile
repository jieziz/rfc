# RFC Auto Grabber Makefile

.PHONY: help install install-dev test clean deploy run lint format check-deps

# 默认目标
help:
	@echo "RFC Auto Grabber - 可用命令:"
	@echo ""
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  clean        - 清理临时文件"
	@echo "  deploy       - 运行部署脚本"
	@echo "  run          - 启动快速启动脚本"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  check-deps   - 检查依赖"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	pip install -r config/requirements.txt

# 安装开发依赖
install-dev: install
	@echo "🛠️ 安装开发依赖..."
	pip install pytest flake8 black mypy

# 运行测试
test:
	@echo "🧪 运行测试..."
	python -m pytest tests/ -v

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -f *.log

# 运行部署脚本
deploy:
	@echo "🚀 运行部署脚本..."
	chmod +x scripts/deploy.sh
	./scripts/deploy.sh

# 启动快速启动脚本
run:
	@echo "▶️ 启动RFC Auto Grabber..."
	python quick_start.py

# 代码检查
lint:
	@echo "🔍 代码检查..."
	flake8 src/ quick_start.py --max-line-length=88 --ignore=E203,W503

# 代码格式化
format:
	@echo "✨ 代码格式化..."
	black src/ quick_start.py --line-length=88

# 检查依赖
check-deps:
	@echo "📋 检查依赖..."
	./scripts/deploy.sh --check

# 构建包
build:
	@echo "📦 构建包..."
	python setup.py sdist bdist_wheel

# 安装本地包
install-local: build
	@echo "📥 安装本地包..."
	pip install -e .

# 创建虚拟环境
venv:
	@echo "🐍 创建虚拟环境..."
	python -m venv venv
	@echo "激活虚拟环境: source venv/bin/activate (Linux/macOS) 或 venv\\Scripts\\activate (Windows)"

# 检查代码质量
quality: lint test
	@echo "✅ 代码质量检查完成"

# 完整检查
check: clean install-dev quality
	@echo "🎯 完整检查完成"
