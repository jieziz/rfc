"""
快速启动脚本
提供简单的命令行界面来选择不同的抢单模式
"""

import os
import sys
import time
import subprocess
try:
    from src.core.performance_config import PerformanceConfig, create_optimized_env_file
    from src.utils.linux_optimizer import log_environment_info, is_linux_headless_environment
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有文件都在正确的目录中")
    sys.exit(1)

def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 RFC Auto Grabber v2.0                 ║
║                   简化版快速启动器                           ║
╠══════════════════════════════════════════════════════════════╣
║  特性:                                                       ║
║  ✅ 三种核心模式，简单易选                                   ║
║  ✅ 智能性能配置                                             ║
║  ✅ 自动故障恢复                                             ║
║  ✅ 实时监控                                                 ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_modes():
    """显示可用模式"""
    print("\n📋 可用的抢单模式:")
    print("=" * 60)

    modes = {
        '1': ('simple_fast', '快速模式', '最稳定的快速版本 (强烈推荐)'),
        '2': ('stable', '稳定模式', '超高稳定性，确保登录 (网络不稳定时使用)'),
        '3': ('concurrent', '并发模式', '多浏览器并发抢单 (高性能机器)')
    }

    for key, (mode, name, desc) in modes.items():
        print(f"{key}. {name}")
        print(f"   {desc}")
        print()

    print("💡 推荐使用: 大多数情况下建议使用 快速模式")
    print()

    return modes

def check_config():
    """检查配置"""
    env_file = '.env'
    if not os.path.exists(env_file):
        print("❌ 未找到 .env 配置文件！")
        print("请确保 .env 文件存在并包含必要的配置项。")
        return False
    
    # 检查必要的配置项
    required_configs = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        missing_configs = []
        for config in required_configs:
            if not os.getenv(config):
                missing_configs.append(config)
        
        if missing_configs:
            print(f"❌ 缺少必要的配置项: {', '.join(missing_configs)}")
            return False
        
        print("✅ 配置检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def optimize_config(mode: str):
    """优化配置"""
    try:
        print(f"🔧 正在优化配置为 {mode} 模式...")
        
        config_manager = PerformanceConfig(mode)
        config_manager.print_config()
        
        # 创建优化的配置文件
        create_optimized_env_file(mode)
        
        print("✅ 配置优化完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置优化失败: {e}")
        return False

def run_script(script_name: str, mode: str = None):
    """运行脚本"""
    try:
        print(f"🚀 启动脚本: {script_name}")

        # 将文件路径转换为模块路径
        if script_name.endswith('.py'):
            module_name = script_name[:-3].replace('/', '.').replace('\\', '.')
        else:
            module_name = script_name.replace('/', '.').replace('\\', '.')

        if mode:
            cmd = [sys.executable, '-m', module_name, mode]
        else:
            cmd = [sys.executable, '-m', module_name]

        print(f"执行命令: {' '.join(cmd)}")
        print("=" * 60)

        # 运行脚本
        process = subprocess.run(cmd, cwd=os.getcwd())

        if process.returncode == 0:
            print("✅ 脚本执行完成")
        else:
            print(f"❌ 脚本执行失败，退出码: {process.returncode}")

    except KeyboardInterrupt:
        print("\n⏹️ 用户中断执行")
    except Exception as e:
        print(f"❌ 执行错误: {e}")

def show_performance_tips():
    """显示性能优化建议"""
    tips = """
💡 模式选择建议:

1. 快速模式 (推荐):
   - 适合大多数用户
   - 平衡速度和稳定性
   - 网络要求: 一般

2. 稳定模式:
   - 网络不稳定时使用
   - 优先保证成功率
   - 速度较慢但更可靠

3. 并发模式:
   - 需要高性能机器 (8GB+ 内存)
   - 多浏览器同时抢购
   - 网络要求: 良好

💡 系统优化建议:
   - 关闭不必要的后台程序
   - 使用有线网络连接
   - 确保网络延迟低于50ms
   - 观察日志输出调整参数
    """
    print(tips)

def main():
    """主函数"""
    print_banner()

    # 检测并记录环境信息
    print("🔍 检测系统环境...")
    log_environment_info()

    # Linux无头环境提示
    if is_linux_headless_environment():
        print("🐧 检测到Linux服务器环境（无显示），已自动启用无头模式优化")

    # 检查配置
    if not check_config():
        print("\n请先配置 .env 文件后再运行。")
        return
    
    while True:
        modes = show_modes()
        
        try:
            choice = input("请选择模式 (1-3) 或输入 'h' 查看帮助, 'q' 退出: ").strip().lower()

            if choice == 'q':
                print("👋 再见！")
                break
            elif choice == 'h':
                show_performance_tips()
                continue
            elif choice not in modes:
                print("❌ 无效选择，请重新输入")
                continue
            
            mode_name, mode_desc = modes[choice][1], modes[choice][2]
            
            print(f"\n🎯 选择了: {mode_name}")
            print(f"描述: {mode_desc}")
            
            # 确认选择
            confirm = input("\n确认启动? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
            
            # 根据选择运行相应脚本
            if choice == '1':  # simple_fast
                optimize_config('fast')
                run_script('src/grabbers/simple_fast_grabber.py')
            elif choice == '2':  # stable
                optimize_config('stable')
                run_script('src/grabbers/stable_grabber.py')
            elif choice == '3':  # concurrent
                optimize_config('fast')
                run_script('src/grabbers/concurrent_grabber.py')
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
