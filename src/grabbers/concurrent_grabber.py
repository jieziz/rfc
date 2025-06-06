"""
并发抢单器 - 多浏览器并行抢单
特性：
1. 多浏览器实例并行运行
2. 智能负载均衡
3. 实时状态监控
4. 自动故障恢复
"""

import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from DrissionPage import ChromiumPage, ChromiumOptions
from dotenv import load_dotenv
import os
import random
import queue
from typing import Dict, Any, List
from ..utils.TimePinner import Pinner
from sys import platform

def apply_headless_config(co, config: Dict[str, Any]):
    """应用无头模式配置"""
    headless_value = config.get('HEADLESS_MODE', False)

    # 处理不同类型的值
    if isinstance(headless_value, bool):
        headless_mode = headless_value
    elif isinstance(headless_value, str):
        headless_mode = headless_value.lower() in ['true', '1', 'yes', 'on']
    else:
        headless_mode = bool(headless_value)

    if headless_mode:
        # 启用无头模式
        co.headless()

        # 添加无头模式必要参数
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--disable-gpu')
        co.set_argument('--window-size=1920,1080')

        logging.info("已启用无头模式")
    else:
        logging.info("使用有头模式")

    # # 设置自定义User-Agent（无头和有头模式都适用）
    # custom_ua = config.get('CUSTOM_USER_AGENT', '')
    # if custom_ua:
    #     co.set_user_agent(custom_ua)
    #     logging.info(f"已设置自定义User-Agent: {custom_ua}")
    # else:
    #     # 根据系统平台自动选择User-Agent
    #     if platform == "linux" or platform == "linux2":
    #         platformIdentifier = "X11; Linux x86_64"
    #     elif platform == "darwin":
    #         platformIdentifier = "Macintosh; Intel Mac OS X 10_15_7"
    #     elif platform == "win32":
    #         platformIdentifier = "Windows NT 10.0; Win64; x64"
    #     else:
    #         platformIdentifier = "Windows NT 10.0; Win64; x64"  # 默认使用Windows

    #     default_ua = f"Mozilla/5.0 ({platformIdentifier}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    #     co.set_user_agent(default_ua)
    #     logging.info(f"已设置基于平台的User-Agent: {default_ua}")

    return co


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("concurrent_log.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ConcurrentConfig:
    """并发配置管理"""
    
    def __init__(self):
        load_dotenv(override=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        return {
            'BASE_URL': os.getenv("BASE_URL", "").rstrip('/'),
            'PRODUCT_URL': os.getenv("PRODUCT_URL"),
            'LOGIN_URL': os.getenv("LOGIN_URL"),
            'EMAIL': os.getenv("EMAIL"),
            'PASSWORD': os.getenv("PASSWORD"),
            'HEADLESS_MODE': os.getenv("HEADLESS_MODE", "True").lower() == "true",
            
            # 并发配置
            'CONCURRENT_BROWSERS': int(os.getenv("CONCURRENT_BROWSERS", "5")),
            'MAX_WORKERS': int(os.getenv("MAX_WORKERS", "10")),
            'WORKER_DELAY': float(os.getenv("WORKER_DELAY", "0.1")),
            'CHECK_INTERVAL': float(os.getenv("CHECK_INTERVAL", "0.3")),
            'RESTART_INTERVAL': int(os.getenv("RESTART_INTERVAL", "300")),  # 5分钟重启
            'PAYMENT_WAIT_TIME': int(os.getenv("PAYMENT_WAIT_TIME", "30")),  # 购买成功后等待用户付款的时间

        }

class BrowserWorker:
    """浏览器工作器"""
    
    def __init__(self, worker_id: int, config: Dict[str, Any], result_queue: queue.Queue):
        self.worker_id = worker_id
        self.config = config
        self.result_queue = result_queue
        self.browser = None
        self.page = None
        self.is_running = False
        self.success_count = 0
        self.check_count = 0
        
    def setup_browser(self):
        """设置浏览器"""
        try:
            co = ChromiumOptions().auto_port()

            # 高性能配置
            co.set_load_mode('none')

            # 基础性能参数
            performance_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-images',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--memory-pressure-off',
                '--hide-crash-restore-bubble',
                '--start-maximized'
            ]

            # 应用基础参数
            for arg in performance_args:
                co.set_argument(arg)

            # 应用无头模式配置
            co = apply_headless_config(co, self.config)

            # 设置浏览器首选项
            co.set_pref('credentials_enable_service', False)

            # 使用ChromiumPage而不是Chromium（DrissionPage官方推荐）
            self.page = ChromiumPage(co)
            self.browser = self.page  # 保持兼容性
            
            # 快速登录
            self._quick_login()
            
            logging.info(f"Worker-{self.worker_id}: 浏览器设置完成")
            return True
            
        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 浏览器设置失败: {e}")
            return False
    
    def _quick_login(self):
        """快速登录"""
        try:
            self.page.get(self.config['LOGIN_URL'])
            time.sleep(1)
            
            # 检查是否已登录
            if self.page.s_ele('text:Dashboard', timeout=1):
                return True
            
            # 输入登录信息
            email_input = self.page.s_ele('#inputEmail', timeout=2)
            if email_input:
                self.page('#inputEmail').input(self.config['EMAIL'])
            
            password_input = self.page.s_ele('#inputPassword', timeout=2)
            if password_input:
                self.page('#inputPassword').input(self.config['PASSWORD'])
            
            # 点击登录
            login_btn = self.page.s_ele('#login', timeout=2)
            if login_btn:
                self.page('#login').click()
                time.sleep(2)
            
            return True
            
        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 登录失败: {e}")
            return False
    
    def check_stock_and_purchase(self) -> bool:
        """检查库存并购买"""
        try:
            self.check_count += 1

            # 访问产品页面
            self.page.get(self.config['PRODUCT_URL'])
            time.sleep(0.2)

            # 快速检查缺货
            out_of_stock_indicators = [
                'text:Out of Stock',
                'text:缺货',
                '.out-of-stock'
            ]

            for indicator in out_of_stock_indicators:
                if self.page.s_ele(indicator, timeout=0.1):
                    return False

            # 检查购买按钮
            buy_button = self.page.s_ele('#btnCompleteProductConfig', timeout=0.5)
            if not buy_button:
                buy_button = self.page.s_ele('text:Add to Cart', timeout=0.5)

            if buy_button:
                # 有库存，尝试购买
                logging.info(f"Worker-{self.worker_id}: 检测到库存，开始抢购！")

                # 执行完整的购买流程
                if self._perform_safe_purchase():
                    self.success_count += 1

                    # 通知主线程
                    self.result_queue.put({
                        'worker_id': self.worker_id,
                        'action': 'success',
                        'timestamp': time.time()
                    })

                    logging.info(f"🎉 Worker-{self.worker_id}: 抢单成功！")

                    # 购买成功后，给用户足够时间完成付款
                    wait_time = self.config['PAYMENT_WAIT_TIME']
                    logging.info(f"Worker-{self.worker_id}: 购买成功，等待{wait_time}秒让用户完成付款...")
                    time.sleep(wait_time)  # 给用户配置的时间完成付款

                    return True

            return False

        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 抢购过程错误: {e}")
            return False

    def _perform_safe_purchase(self) -> bool:
        """安全的购买流程，避免在结算过程中被中断"""
        try:
            # 步骤1: 点击购买按钮
            buy_selectors = [
                '#btnCompleteProductConfig',
                '.btn-add-cart',
                'text:Add to Cart',
                'text:立即购买'
            ]

            clicked = False
            for selector in buy_selectors:
                try:
                    if self.page.s_ele(selector, timeout=0.3):
                        self.page(selector).click()
                        logging.info(f"Worker-{self.worker_id}: 点击购买按钮: {selector}")
                        clicked = True
                        break
                except:
                    continue

            if not clicked:
                logging.warning(f"Worker-{self.worker_id}: 未找到购买按钮")
                return False

            # 步骤2: 等待页面响应和系统验证
            logging.info(f"Worker-{self.worker_id}: 等待5秒进行系统验证（反机器人验证、库存检查等）...")
            time.sleep(5)  # 等待5秒确保系统验证通过（反机器人验证、库存检查等）
            logging.info(f"Worker-{self.worker_id}: 系统验证等待完成")

            # 步骤3: 处理条款（如果存在）
            tos_selectors = [
                '#tos-checkbox',
                '.tos-checkbox',
                'input[name="tos"]',
                'text:I agree'
            ]

            for selector in tos_selectors:
                try:
                    if self.page.s_ele(selector, timeout=0.5):
                        self.page(selector).click()
                        logging.info(f"Worker-{self.worker_id}: 点击条款: {selector}")
                        break
                except:
                    continue

            # 步骤4: 点击结算并等待进入付款页面
            checkout_selectors = [
                '#checkout',
                '.checkout-btn',
                'text:Checkout',
                'text:结算',
                'text:立即支付'
            ]

            for selector in checkout_selectors:
                try:
                    if self.page.s_ele(selector, timeout=1):
                        self.page(selector).click()
                        logging.info(f"Worker-{self.worker_id}: 点击结算: {selector}")

                        # 等待进入付款页面
                        if self._wait_for_payment_page():
                            logging.info(f"Worker-{self.worker_id}: 成功进入付款页面，请在浏览器中完成付款...")

                            # 不立即返回，让用户有时间看到付款页面
                            # 这里不做额外等待，让主循环处理等待逻辑
                            return True
                        else:
                            logging.warning(f"Worker-{self.worker_id}: 未能进入付款页面")
                            return False
                except:
                    continue

            logging.warning(f"Worker-{self.worker_id}: 未找到结算按钮")
            return False

        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 安全购买流程错误: {e}")
            return False

    def _wait_for_payment_page(self, max_wait_time: int = 15) -> bool:
        """等待进入付款页面 - 缩短等待时间，避免阻塞太久"""
        try:
            # 付款页面的标识符
            payment_indicators = [
                'text:Payment',
                'text:支付',
                'text:付款',
                '.payment-form',
                '#payment-form',
                'text:Credit Card',
                'text:信用卡',
                'text:PayPal',
                'text:Order Summary',
                'text:订单摘要',
                'text:Total',
                'text:总计',
                'text:Billing',
                'text:账单',
                'text:Continue to Payment',
                'text:继续付款'
            ]

            start_time = time.time()
            logging.info(f"Worker-{self.worker_id}: 开始等待付款页面...")

            while time.time() - start_time < max_wait_time:
                # 检查是否已进入付款页面
                for indicator in payment_indicators:
                    if self.page.s_ele(indicator, timeout=0.3):
                        logging.info(f"Worker-{self.worker_id}: 检测到付款页面标识: {indicator}")
                        return True

                # 检查URL是否包含付款相关关键词
                try:
                    current_url = self.page.url.lower()
                    payment_url_keywords = ['payment', 'checkout', 'order', 'cart', 'billing', 'pay']

                    for keyword in payment_url_keywords:
                        if keyword in current_url:
                            logging.info(f"Worker-{self.worker_id}: URL包含付款关键词: {keyword} - {current_url}")
                            return True
                except:
                    pass

                # 短暂等待后继续检查
                time.sleep(0.5)

            logging.warning(f"Worker-{self.worker_id}: 等待付款页面超时 ({max_wait_time}秒)")
            return False

        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 等待付款页面错误: {e}")
            return False
    
    def run(self):
        """运行工作器"""
        self.is_running = True

        if not self.setup_browser():
            self.is_running = False
            return

        logging.info(f"Worker-{self.worker_id}: 开始监控...")

        while self.is_running:
            try:
                # 检查库存并购买
                purchase_success = self.check_stock_and_purchase()

                # 如果购买成功且配置为单次购买，则停止
                if purchase_success and self.config.get('STOP_AFTER_SUCCESS', True):
                    logging.info(f"Worker-{self.worker_id}: 购买成功，根据配置停止运行")
                    self.is_running = False
                    break

                # 动态延迟
                delay = self.config['CHECK_INTERVAL'] + random.uniform(-0.1, 0.1)
                time.sleep(max(0.1, delay))

                # 每100次检查报告状态
                if self.check_count % 100 == 0:
                    self.result_queue.put({
                        'worker_id': self.worker_id,
                        'action': 'status',
                        'check_count': self.check_count,
                        'success_count': self.success_count
                    })

            except Exception as e:
                logging.error(f"Worker-{self.worker_id}: 运行错误: {e}")
                time.sleep(1)
    
    def stop(self):
        """停止工作器"""
        self.is_running = False
        if self.page:
            try:
                self.page.quit()
            except:
                pass

class ConcurrentGrabber:
    """并发抢单管理器"""
    
    def __init__(self):
        self.config_manager = ConcurrentConfig()
        self.config = self.config_manager.config
        self.workers: List[BrowserWorker] = []
        self.result_queue = queue.Queue()
        self.total_success = 0
        self.total_checks = 0
        self.is_running = False
    
    def create_workers(self):
        """创建工作器"""
        num_workers = self.config['CONCURRENT_BROWSERS']
        
        for i in range(num_workers):
            worker = BrowserWorker(i + 1, self.config, self.result_queue)
            self.workers.append(worker)
        
        logging.info(f"创建了 {num_workers} 个并发工作器")
    
    def start_workers(self):
        """启动所有工作器"""
        self.is_running = True
        
        # 使用线程池启动工作器
        with ThreadPoolExecutor(max_workers=self.config['MAX_WORKERS']) as executor:
            # 提交工作器任务
            futures = [executor.submit(worker.run) for worker in self.workers]
            
            # 启动结果监控线程
            monitor_thread = threading.Thread(target=self._monitor_results)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            try:
                # 等待所有工作器完成或中断
                for future in as_completed(futures):
                    if not self.is_running:
                        break
                    
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"工作器执行错误: {e}")
                        
            except KeyboardInterrupt:
                logging.info("收到中断信号，停止所有工作器...")
                self.stop_all_workers()
    
    def _monitor_results(self):
        """监控结果"""
        while self.is_running:
            try:
                # 非阻塞获取结果
                try:
                    result = self.result_queue.get(timeout=1)
                    
                    if result['action'] == 'success':
                        self.total_success += 1
                        logging.info(f"🎉 总成功次数: {self.total_success}")
                        
                        # 成功后可以选择暂停其他工作器
                        # self._pause_other_workers(result['worker_id'])
                        
                    elif result['action'] == 'status':
                        worker_id = result['worker_id']
                        check_count = result['check_count']
                        success_count = result['success_count']
                        logging.info(f"Worker-{worker_id}: 检查 {check_count} 次，成功 {success_count} 次")
                        
                except queue.Empty:
                    continue
                    
            except Exception as e:
                logging.error(f"结果监控错误: {e}")
    
    def stop_all_workers(self):
        """停止所有工作器"""
        self.is_running = False
        
        for worker in self.workers:
            worker.stop()
        
        logging.info("所有工作器已停止")
    
    def run(self):
        """运行并发抢单器"""
        logging.info("🚀 启动并发抢单器...")
        
        try:
            self.create_workers()
            self.start_workers()
            
        except Exception as e:
            logging.error(f"并发抢单器运行错误: {e}")
        finally:
            self.stop_all_workers()
            logging.info(f"并发抢单结束，总成功次数: {self.total_success}")

def main():
    """主函数"""
    grabber = ConcurrentGrabber()
    grabber.run()

if __name__ == "__main__":
    main()
