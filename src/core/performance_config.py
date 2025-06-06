"""
性能配置管理器
提供不同场景下的优化配置
"""

import os
import time
from typing import Dict, Any
from dotenv import load_dotenv

class PerformanceConfig:
    """性能配置管理器"""
    
    # 预设配置模式 (简化版)
    PRESETS = {
        'fast': {
            'name': '简化快速模式',
            'description': '最稳定的快速版本 (强烈推荐)',
            'config': {
                'DELAY_TIME': 0.3,
                'ELEMENT_TIMEOUT': 2,
                'PAGE_LOAD_TIMEOUT': 8,
                'PAGE_LOAD_WAIT': 0.5,
                'ELEMENT_WAIT': 0.1,
                'STOCK_CHECK_INTERVAL': 0.2,
                'CONCURRENT_BROWSERS': 3,
                'HEADLESS_MODE': True,
                'FAST_MODE': True,
                'QUICK_PURCHASE': True,
                'BROWSER_POOL_SIZE': 3,
                'MAX_WORKERS': 5,
            }
        },

        'stable': {
            'name': '稳定模式',
            'description': '超高稳定性，确保登录 (网络不稳定时使用)',
            'config': {
                'DELAY_TIME': 1,
                'ELEMENT_TIMEOUT': 5,
                'PAGE_LOAD_TIMEOUT': 15,
                'PAGE_LOAD_WAIT': 2,
                'ELEMENT_WAIT': 0.5,
                'STOCK_CHECK_INTERVAL': 0.5,
                'CONCURRENT_BROWSERS': 1,
                'HEADLESS_MODE': False,
                'FAST_MODE': False,
                'QUICK_PURCHASE': False,
                'BROWSER_POOL_SIZE': 1,
                'MAX_WORKERS': 2,
            }
        },

        'concurrent': {
            'name': '并发模式',
            'description': '多浏览器并发抢单 (高性能机器)',
            'config': {
                'DELAY_TIME': 0.2,
                'ELEMENT_TIMEOUT': 2,
                'PAGE_LOAD_TIMEOUT': 8,
                'PAGE_LOAD_WAIT': 0.3,
                'ELEMENT_WAIT': 0.1,
                'STOCK_CHECK_INTERVAL': 0.15,
                'CONCURRENT_BROWSERS': 5,
                'HEADLESS_MODE': True,
                'FAST_MODE': True,
                'QUICK_PURCHASE': True,
                'BROWSER_POOL_SIZE': 5,
                'MAX_WORKERS': 8,
            }
        }
    }
    
    def __init__(self, mode: str = 'fast'):
        """
        初始化性能配置

        Args:
            mode: 配置模式 ('fast', 'stable', 'concurrent')
        """
        load_dotenv(override=True)
        self.mode = mode
        self.config = self._build_config()
    
    def _build_config(self) -> Dict[str, Any]:
        """构建配置"""
        # 基础配置
        base_config = {
            'BASE_URL': os.getenv("BASE_URL", "").rstrip('/'),
            'PRODUCT_URL': os.getenv("PRODUCT_URL"),
            'LOGIN_URL': os.getenv("LOGIN_URL"),
            'EMAIL': os.getenv("EMAIL"),
            'PASSWORD': os.getenv("PASSWORD"),
            'PROMO_CODE': os.getenv("PROMO_CODE", ""),
        }
        
        # 获取预设配置
        if self.mode in self.PRESETS:
            preset_config = self.PRESETS[self.mode]['config']
        else:
            preset_config = self.PRESETS['fast']['config']  # 默认使用快速模式
        
        # 合并配置，环境变量优先
        final_config = {}
        final_config.update(base_config)
        
        for key, default_value in preset_config.items():
            env_value = os.getenv(key)
            if env_value is not None:
                # 类型转换
                try:
                    if isinstance(default_value, bool):
                        final_config[key] = env_value.lower() == 'true'
                    elif isinstance(default_value, int):
                        final_config[key] = int(float(env_value))  # 先转float再转int，处理小数
                    elif isinstance(default_value, float):
                        final_config[key] = float(env_value)
                    else:
                        final_config[key] = env_value
                except (ValueError, TypeError):
                    # 如果转换失败，使用默认值
                    final_config[key] = default_value
            else:
                final_config[key] = default_value
        
        return final_config
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    def get_mode_info(self) -> Dict[str, str]:
        """获取当前模式信息"""
        if self.mode in self.PRESETS:
            return {
                'mode': self.mode,
                'name': self.PRESETS[self.mode]['name'],
                'description': self.PRESETS[self.mode]['description']
            }
        return {
            'mode': self.mode,
            'name': '自定义模式',
            'description': '使用环境变量配置'
        }
    
    def print_config(self):
        """打印当前配置"""
        mode_info = self.get_mode_info()
        print(f"\n=== 性能配置 ===")
        print(f"模式: {mode_info['name']} ({mode_info['mode']})")
        print(f"描述: {mode_info['description']}")
        print(f"\n配置详情:")
        
        for key, value in self.config.items():
            if key not in ['EMAIL', 'PASSWORD']:  # 隐藏敏感信息
                print(f"  {key}: {value}")
        print("=" * 20)
    
    @classmethod
    def list_presets(cls):
        """列出所有预设模式"""
        print("\n=== 可用的性能模式 ===")
        for mode, info in cls.PRESETS.items():
            print(f"{mode}: {info['name']}")
            print(f"  描述: {info['description']}")
            print()

def create_optimized_env_file(mode: str = 'fast'):
    """创建优化的 .env 文件"""
    config_manager = PerformanceConfig(mode)
    config = config_manager.get_config()
    
    # 读取现有的 .env 文件
    env_file_path = '.env'
    existing_config = {}
    
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_config[key.strip()] = value.strip()
    
    # 更新配置
    for key, value in config.items():
        if key not in ['BASE_URL', 'PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD', 'PROMO_CODE']:
            existing_config[key] = str(value)
    
    # 写入新的 .env 文件
    backup_file = f'.env.backup.{int(time.time())}'
    if os.path.exists(env_file_path):
        os.rename(env_file_path, backup_file)
        print(f"原配置文件已备份为: {backup_file}")
    
    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.write(f"# 优化配置文件 - {mode} 模式\n")
        f.write(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 基础配置
        f.write("# 基础配置\n")
        basic_keys = ['BASE_URL', 'PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD', 'PROMO_CODE']
        for key in basic_keys:
            if key in existing_config:
                f.write(f"{key}={existing_config[key]}\n")
        
        f.write("\n# 性能优化配置\n")
        performance_keys = [k for k in existing_config.keys() if k not in basic_keys]
        for key in sorted(performance_keys):
            f.write(f"{key}={existing_config[key]}\n")
    
    print(f"已生成优化配置文件: {env_file_path}")
    config_manager.print_config()

if __name__ == "__main__":
    import time
    
    # 列出所有模式
    PerformanceConfig.list_presets()
    
    # 创建快速模式配置
    create_optimized_env_file('fast')
