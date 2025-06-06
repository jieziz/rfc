"""
核心模块 - 浏览器池管理和性能配置
"""

from .browser_pool import BrowserPool
from .performance_config import PerformanceConfig, create_optimized_env_file

__all__ = ['BrowserPool', 'PerformanceConfig', 'create_optimized_env_file']
