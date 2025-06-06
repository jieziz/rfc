"""
超级抢单器 - 终极优化版本
集成所有优化技术：
1. 浏览器池管理
2. 并发处理
3. 智能库存检测
4. 极速购买流程
5. 实时性能监控
"""

import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
import random
import queue
from dotenv import load_dotenv
import os

from browser_pool import BrowserPool
from performance_config import PerformanceConfig
from TimePinner import Pinner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("super_grabber.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SuperStockChecker:
    """超级库存检查器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stock_cache = {}
        self.cache_timeout = 1  # 缓存1秒
        
        # 优化的选择器
        self.selectors = {
            'out_of_stock': [
                'text:Out of Stock',
                'text:缺货',
                'text:售罄',
                'text:Sold Out',
                '.out-of-stock',
                '#out-of-stock'
            ],
            'in_stock': [
                '#btnCompleteProductConfig',
                '.btn-add-cart',
                'text:Add to Cart',
                'text:立即购买',
                'text:加入购物车',
                '[data-action="add-to-cart"]'
            ]
        }
    
    def ultra_fast_check(self, page) -> bool:
        """超快速库存检查"""
        try:
            # 检查缓存
            cache_key = self.config['PRODUCT_URL']
            current_time = time.time()
            
            if cache_key in self.stock_cache:
                cache_data = self.stock_cache[cache_key]
                if current_time - cache_data['timestamp'] < self.cache_timeout:
                    return cache_data['has_stock']
            
            # 极速检查
            has_stock = True
            
            # 快速检查缺货标识（超短超时）
            for selector in self.selectors['out_of_stock']:
                if page.s_ele(selector, timeout=0.05):
                    has_stock = False
                    break
            
            # 如果没有缺货标识，检查购买按钮
            if has_stock:
                button_found = False
                for selector in self.selectors['in_stock']:
                    if page.s_ele(selector, timeout=0.05):
                        button_found = True
                        break
                has_stock = button_found
            
            # 更新缓存
            self.stock_cache[cache_key] = {
                'has_stock': has_stock,
                'timestamp': current_time
            }
            
            return has_stock
            
        except Exception as e:
            logging.debug(f"超快速库存检查错误: {e}")
            return False

class SuperPurchaser:
    """超级购买器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def lightning_buy(self, page) -> bool:
        """闪电购买"""
        try:
            pinner = Pinner()
            pinner.pin('闪电购买开始')
            
            # 预定义所有选择器
            selectors = {
                'add_cart': [
                    '#btnCompleteProductConfig',
                    '.btn-add-cart',
                    'text:Add to Cart'
                ],
                'tos': [
                    '#tos-checkbox',
                    '.tos-checkbox',
                    'input[name="tos"]'
                ],
                'checkout': [
                    '#checkout',
                    '.checkout-btn',
                    'text:Checkout'
                ]
            }
            
            # 步骤1: 添加到购物车
            for selector in selectors['add_cart']:
                try:
                    if page.s_ele(selector, timeout=0.3):
                        page(selector).click()
                        pinner.pin('点击购物车')
                        break
                except:
                    continue
            else:
                return False
            
            # 最小等待
            time.sleep(0.1)
            
            # 步骤2: 处理条款（可选）
            for selector in selectors['tos']:
                try:
                    if page.s_ele(selector, timeout=0.1):
                        page(selector).click()
                        break
                except:
                    continue
            
            # 步骤3: 结算
            for selector in selectors['checkout']:
                try:
                    if page.s_ele(selector, timeout=0.5):
                        page(selector).click()
                        pinner.pin('点击结算')
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"闪电购买错误: {e}")
            return False

class SuperGrabber:
    """超级抢单器主类"""
    
    def __init__(self, mode: str = 'fast'):
        # 加载配置
        self.config_manager = PerformanceConfig(mode)
        self.config = self.config_manager.get_config()
        
        # 创建浏览器池
        pool_size = self.config.get('BROWSER_POOL_SIZE', 3)
        self.browser_pool = BrowserPool(self.config, pool_size)
        
        # 创建组件
        self.stock_checker = SuperStockChecker(self.config)
        self.purchaser = SuperPurchaser(self.config)
        
        # 统计信息
        self.stats = {
            'total_checks': 0,
            'total_success': 0,
            'start_time': time.time(),
            'last_success_time': None
        }
        
        # 控制变量
        self.is_running = False
        self.result_queue = queue.Queue()
        
        # 打印配置信息
        self.config_manager.print_config()
    
    def worker_task(self, worker_id: int):
        """工作器任务"""
        logging.info(f"Worker-{worker_id}: 启动")
        login_check_counter = 0

        while self.is_running:
            try:
                # 从浏览器池获取实例
                with self.browser_pool.get_browser(timeout=2.0) as page:
                    if page is None:
                        time.sleep(0.5)
                        continue

                    # 每50次检查一次登录状态
                    login_check_counter += 1
                    if login_check_counter % 50 == 0:
                        if not self.ensure_login(page):
                            logging.warning(f"Worker-{worker_id}: 登录检查失败")
                            continue

                    # 访问产品页面
                    page.get(self.config['PRODUCT_URL'])
                    
                    # 极短等待
                    time.sleep(self.config['STOCK_CHECK_INTERVAL'])
                    
                    # 更新统计
                    self.stats['total_checks'] += 1
                    
                    # 超快速库存检查
                    if self.stock_checker.ultra_fast_check(page):
                        logging.info(f"🎯 Worker-{worker_id}: 检测到库存！")
                        
                        # 闪电购买
                        if self.purchaser.lightning_buy(page):
                            self.stats['total_success'] += 1
                            self.stats['last_success_time'] = time.time()
                            
                            # 通知成功
                            self.result_queue.put({
                                'worker_id': worker_id,
                                'action': 'success',
                                'timestamp': time.time()
                            })
                            
                            logging.info(f"🎉 Worker-{worker_id}: 抢单成功！总成功: {self.stats['total_success']}")
                            
                            # 成功后短暂休息
                            time.sleep(random.uniform(0.5, 1.0))
                        else:
                            logging.warning(f"Worker-{worker_id}: 购买失败")
                    
                    # 动态延迟
                    delay = self.config['DELAY_TIME'] + random.uniform(-0.05, 0.05)
                    time.sleep(max(0.05, delay))
                    
            except Exception as e:
                logging.error(f"Worker-{worker_id}: 任务错误: {e}")
                time.sleep(0.5)
        
        logging.info(f"Worker-{worker_id}: 停止")
    
    def monitor_results(self):
        """结果监控器"""
        while self.is_running:
            try:
                result = self.result_queue.get(timeout=1)
                
                if result['action'] == 'success':
                    # 可以在这里添加成功后的处理逻辑
                    # 比如发送通知、暂停其他工作器等
                    pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"结果监控错误: {e}")
    
    def stats_reporter(self):
        """统计报告器"""
        while self.is_running:
            try:
                time.sleep(30)  # 每30秒报告一次
                
                runtime = time.time() - self.stats['start_time']
                checks_per_second = self.stats['total_checks'] / runtime if runtime > 0 else 0
                
                # 获取浏览器池统计
                pool_stats = self.browser_pool.get_stats()
                
                logging.info(f"📊 统计报告:")
                logging.info(f"   运行时间: {runtime:.1f}秒")
                logging.info(f"   总检查: {self.stats['total_checks']} 次")
                logging.info(f"   检查速度: {checks_per_second:.2f} 次/秒")
                logging.info(f"   总成功: {self.stats['total_success']} 次")
                logging.info(f"   浏览器池: {pool_stats['available_count']}/{pool_stats['pool_size']} 可用")
                
            except Exception as e:
                logging.error(f"统计报告错误: {e}")
    
    def ensure_login(self, page) -> bool:
        """确保已登录"""
        try:
            # 检查是否已登录
            dashboard_indicators = ['text:Dashboard', 'text:My Dashboard', '.dashboard']
            for indicator in dashboard_indicators:
                if page.s_ele(indicator, timeout=1):
                    return True

            # 需要登录
            logging.info("需要登录，开始登录流程...")
            page.get(self.config['LOGIN_URL'])
            time.sleep(1)

            # 输入登录信息
            email_selectors = ['#inputEmail', 'input[name="email"]', 'input[type="email"]']
            password_selectors = ['#inputPassword', 'input[name="password"]', 'input[type="password"]']
            login_selectors = ['#login', 'button[type="submit"]', 'text:Login']

            # 输入邮箱
            for selector in email_selectors:
                try:
                    if page.s_ele(selector, timeout=1):
                        page(selector).input(self.config['EMAIL'])
                        break
                except:
                    continue

            # 输入密码
            for selector in password_selectors:
                try:
                    if page.s_ele(selector, timeout=1):
                        page(selector).input(self.config['PASSWORD'])
                        break
                except:
                    continue

            # 点击登录
            for selector in login_selectors:
                try:
                    if page.s_ele(selector, timeout=1):
                        page(selector).click()
                        break
                except:
                    continue

            # 等待登录完成
            time.sleep(2)

            # 验证登录
            for indicator in dashboard_indicators:
                if page.s_ele(indicator, timeout=3):
                    logging.info("登录成功")
                    return True

            logging.warning("登录状态不明确，继续执行")
            return True

        except Exception as e:
            logging.error(f"登录失败: {e}")
            return False

    def run(self):
        """运行超级抢单器"""
        logging.info("🚀 启动超级抢单器...")

        self.is_running = True

        try:
            # 预先登录一个浏览器实例进行测试
            logging.info("预先测试登录...")
            with self.browser_pool.get_browser(timeout=5.0) as test_page:
                if test_page:
                    if not self.ensure_login(test_page):
                        logging.error("登录测试失败，请检查登录信息")
                        return
                    logging.info("登录测试成功")
                else:
                    logging.error("无法获取浏览器实例")
                    return

            # 启动工作器
            max_workers = self.config.get('MAX_WORKERS', 5)
            concurrent_browsers = self.config.get('CONCURRENT_BROWSERS', 3)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交工作器任务
                futures = []
                for i in range(concurrent_browsers):
                    future = executor.submit(self.worker_task, i + 1)
                    futures.append(future)
                
                # 启动监控线程
                monitor_thread = threading.Thread(target=self.monitor_results, daemon=True)
                monitor_thread.start()
                
                # 启动统计线程
                stats_thread = threading.Thread(target=self.stats_reporter, daemon=True)
                stats_thread.start()
                
                logging.info(f"已启动 {concurrent_browsers} 个工作器")
                
                # 等待中断或完成
                try:
                    for future in as_completed(futures):
                        if not self.is_running:
                            break
                        future.result()
                except KeyboardInterrupt:
                    logging.info("收到中断信号...")
                    self.is_running = False
                    
        except Exception as e:
            logging.error(f"运行错误: {e}")
        finally:
            self.is_running = False
            self.browser_pool.destroy_all()
            
            # 最终统计
            runtime = time.time() - self.stats['start_time']
            logging.info(f"🏁 超级抢单器结束")
            logging.info(f"   总运行时间: {runtime:.1f}秒")
            logging.info(f"   总检查次数: {self.stats['total_checks']}")
            logging.info(f"   总成功次数: {self.stats['total_success']}")
            if runtime > 0:
                logging.info(f"   平均检查速度: {self.stats['total_checks']/runtime:.2f} 次/秒")

def main():
    """主函数"""
    import sys
    
    # 支持命令行参数选择模式
    mode = 'fast'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    
    logging.info(f"使用模式: {mode}")
    
    grabber = SuperGrabber(mode)
    grabber.run()

if __name__ == "__main__":
    main()
