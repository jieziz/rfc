"""
快速启动脚本
提供简单的命令行界面来选择不同的抢单模式
"""

import os
import sys
import time
import subprocess
try:
    from performance_config import PerformanceConfig, create_optimized_env_file
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有文件都在正确的目录中")
    sys.exit(1)

def print_banner():
    """打印横幅"""
    banner = """
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
    """
    print(banner)

def show_modes():
    """显示可用模式"""
    print("\n📋 可用的抢单模式:")
    print("=" * 60)
    
    modes = {
        '1': ('simple_fast', '简化快速模式', '最稳定的快速版本 (强烈推荐)'),
        '2': ('fast', '快速模式', '平衡速度和稳定性'),
        '3': ('ultra_fast', '极速模式', '最快速度，适合网络良好环境'),
        '4': ('balanced', '平衡模式', '速度和稳定性平衡'),
        '5': ('stable_new', '新稳定模式', '专门的稳定版，确保登录 (推荐网络不稳定时使用)'),
        '6': ('stable', '稳定模式', '超级抢单器稳定版'),
        '7': ('concurrent', '并发模式', '多浏览器并发抢单'),
        '8': ('debug', '调试模式', '用于调试和测试'),
        '9': ('original', '原版模式', '使用原始脚本')
    }
    
    for key, (mode, name, desc) in modes.items():
        print(f"{key}. {name} ({mode})")
        print(f"   {desc}")
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
        
        if mode:
            cmd = [sys.executable, script_name, mode]
        else:
            cmd = [sys.executable, script_name]
        
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
💡 性能优化建议:

1. 网络优化:
   - 使用有线网络连接
   - 确保网络延迟低于50ms
   - 关闭其他占用带宽的应用

2. 系统优化:
   - 关闭不必要的后台程序
   - 确保有足够的内存 (建议8GB+)
   - 使用SSD硬盘

3. 配置优化:
   - 极速模式: 网络良好时使用
   - 快速模式: 日常使用推荐
   - 稳定模式: 网络不稳定时使用

4. 并发设置:
   - 并发浏览器数量: 3-5个 (根据CPU性能调整)
   - 检查间隔: 0.1-0.3秒
   - 延迟时间: 0.1-0.5秒

5. 监控建议:
   - 观察日志输出
   - 监控成功率
   - 调整参数优化性能
    """
    print(tips)

def main():
    """主函数"""
    print_banner()
    
    # 检查配置
    if not check_config():
        print("\n请先配置 .env 文件后再运行。")
        return
    
    while True:
        modes = show_modes()
        
        try:
            choice = input("请选择模式 (1-9) 或输入 'h' 查看帮助, 'q' 退出: ").strip().lower()
            
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
                run_script('simple_fast_grabber.py')
            elif choice == '2':  # fast
                optimize_config('fast')
                run_script('super_grabber.py', 'fast')
            elif choice == '3':  # ultra_fast
                optimize_config('ultra_fast')
                run_script('super_grabber.py', 'ultra_fast')
            elif choice == '4':  # balanced
                optimize_config('balanced')
                run_script('super_grabber.py', 'balanced')
            elif choice == '5':  # stable_new
                optimize_config('stable')
                run_script('stable_grabber.py')
            elif choice == '6':  # stable
                optimize_config('stable')
                run_script('super_grabber.py', 'stable')
            elif choice == '7':  # concurrent
                optimize_config('fast')
                run_script('concurrent_grabber.py')
            elif choice == '8':  # debug
                optimize_config('debug')
                run_script('super_grabber.py', 'debug')
            elif choice == '9':  # original
                run_script('auto.py')
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
