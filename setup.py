"""
RFC Auto Grabber 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("config/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rfc-auto-grabber",
    version="2.0.0",
    author="RFC Auto Grabber Team",
    author_email="support@example.com",
    description="高性能的RFC/WHCMS自动抢购脚本",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/rfc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rfc-grabber=quick_start:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.sh"],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-repo/rfc/issues",
        "Source": "https://github.com/your-repo/rfc",
        "Documentation": "https://github.com/your-repo/rfc/blob/main/docs/README.md",
    },
)
