"""
Linux环境优化工具
专门针对Linux服务器环境的浏览器配置优化
确保在无显示环境中稳定运行
"""

import os
import logging
from typing import List, Dict, Any


def is_linux_headless_environment() -> bool:
    """
    检测是否为Linux无头环境
    
    Returns:
        bool: 如果是Linux无头环境返回True
    """
    return (
        os.name == 'posix' and 
        not os.environ.get('DISPLAY') and 
        not os.environ.get('WAYLAND_DISPLAY')
    )


def get_linux_headless_args(mode: str = 'performance') -> List[str]:
    """
    获取Linux无头环境的浏览器启动参数
    
    Args:
        mode: 优化模式 ('performance', 'stability', 'minimal')
        
    Returns:
        List[str]: 浏览器启动参数列表
    """
    if not is_linux_headless_environment():
        return []
    
    # 基础无头参数
    base_args = [
        '--disable-software-rasterizer',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-sync',
        '--disable-translate',
        '--hide-scrollbars',
        '--mute-audio',
        '--no-first-run',
        '--disable-client-side-phishing-detection'
    ]
    
    if mode == 'performance':
        # 性能优先模式
        performance_args = [
            '--metrics-recording-only',
            '--safebrowsing-disable-auto-update',
            '--disable-component-update',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-features=TranslateUI,BlinkGenPropertyTrees',
            '--aggressive-cache-discard',
            '--memory-pressure-off'
        ]
        base_args.extend(performance_args)
        
    elif mode == 'stability':
        # 稳定性优先模式
        stability_args = [
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-component-extensions',
            '--disable-background-timer-throttling'
        ]
        base_args.extend(stability_args)
        
    elif mode == 'minimal':
        # 最小化模式，只包含基础参数
        pass
    
    return base_args


def get_linux_environment_info() -> Dict[str, Any]:
    """
    获取Linux环境信息

    Returns:
        Dict[str, Any]: 环境信息字典
    """
    info = {
        'is_linux': os.name == 'posix',
        'is_headless': is_linux_headless_environment(),
        'display': os.environ.get('DISPLAY'),
        'wayland_display': os.environ.get('WAYLAND_DISPLAY'),
        'xdg_session_type': os.environ.get('XDG_SESSION_TYPE'),
        'desktop_session': os.environ.get('DESKTOP_SESSION'),
        'has_xvfb': False,
        'memory_info': {},
        'browser_processes': []
    }

    # 检查Xvfb是否可用
    try:
        import subprocess
        result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True)
        info['has_xvfb'] = result.returncode == 0
    except Exception:
        pass
    
    # 获取内存信息
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    info['memory_info']['total'] = int(line.split()[1]) * 1024  # 转换为字节
                elif line.startswith('MemAvailable:'):
                    info['memory_info']['available'] = int(line.split()[1]) * 1024
    except Exception:
        pass



    return info





def log_environment_info():
    """记录环境信息到日志"""
    info = get_linux_environment_info()

    if info['is_linux']:
        logging.info("Linux环境检测结果:")
        logging.info(f"  - 无头环境: {info['is_headless']}")
        logging.info(f"  - DISPLAY: {info['display'] or 'None'}")
        logging.info(f"  - Wayland: {info['wayland_display'] or 'None'}")
        logging.info(f"  - 会话类型: {info['xdg_session_type'] or 'Unknown'}")
        logging.info(f"  - Xvfb可用: {info['has_xvfb']}")

        if info['memory_info']:
            total_mb = info['memory_info'].get('total', 0) // (1024 * 1024)
            available_mb = info['memory_info'].get('available', 0) // (1024 * 1024)
            logging.info(f"  - 内存: {total_mb}MB 总计, {available_mb}MB 可用")




def apply_linux_optimizations(chromium_options, mode: str = 'performance'):
    """
    为ChromiumOptions应用Linux优化
    根据DrissionPage官方文档的无头模式最佳实践

    Args:
        chromium_options: DrissionPage的ChromiumOptions对象
        mode: 优化模式 ('performance', 'stability', 'minimal')
    """
    if not is_linux_headless_environment():
        return chromium_options

    # 核心无头模式配置（根据DrissionPage官方文档）
    # 1. 关闭沙箱模式，解决 $DISPLAY 报错
    chromium_options.set_argument('--no-sandbox')

    # 2. 开启无头模式，解决浏览器无法连接报错
    chromium_options.headless()

    # 3. 添加其他必要的无头模式参数
    chromium_options.set_argument('--disable-dev-shm-usage')  # 解决共享内存问题
    chromium_options.set_argument('--disable-gpu')           # 禁用GPU加速

    # 获取额外的优化参数
    args = get_linux_headless_args(mode)

    # 应用额外参数
    for arg in args:
        # 避免重复添加已设置的参数
        if arg not in ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']:
            chromium_options.set_argument(arg)

    # 设置虚拟显示大小（如果需要）
    if not os.environ.get('DISPLAY'):
        chromium_options.set_argument('--window-size=1920,1080')
        chromium_options.set_argument('--virtual-time-budget=5000')

    logging.info(f"已应用Linux无头环境优化 (模式: {mode}) - 使用DrissionPage最佳实践")
    return chromium_options


def setup_virtual_display():
    """
    设置虚拟显示（如果需要且可用）
    
    Returns:
        int: Xvfb进程ID，如果未启动则返回None
    """
    if not is_linux_headless_environment():
        return None
    
    info = get_linux_environment_info()
    if not info['has_xvfb']:
        logging.warning("Xvfb不可用，无法设置虚拟显示")
        return None
    
    try:
        import subprocess
        import time
        
        # 启动Xvfb
        display_num = ':99'
        cmd = ['Xvfb', display_num, '-screen', '0', '1920x1080x24', '-nolisten', 'tcp']
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待启动
        time.sleep(2)
        
        # 设置DISPLAY环境变量
        os.environ['DISPLAY'] = display_num
        
        logging.info(f"虚拟显示已启动: {display_num} (PID: {process.pid})")
        return process.pid
        
    except Exception as e:
        logging.error(f"启动虚拟显示失败: {e}")
        return None


def cleanup_virtual_display(pid: int):
    """
    清理虚拟显示

    Args:
        pid: Xvfb进程ID
    """
    if pid is None:
        return

    try:
        import signal
        os.kill(pid, signal.SIGTERM)
        logging.info(f"虚拟显示已清理 (PID: {pid})")
    except Exception as e:
        logging.warning(f"清理虚拟显示失败: {e}")





# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 检测环境
    log_environment_info()
    
    # 获取优化参数
    if is_linux_headless_environment():
        args = get_linux_headless_args('performance')
        print(f"Linux无头环境优化参数: {args}")
    else:
        print("非Linux无头环境，无需特殊优化")
