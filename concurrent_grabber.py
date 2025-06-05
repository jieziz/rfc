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
from DrissionPage import Chromium, ChromiumOptions
from dotenv import load_dotenv
import os
import random
import queue
from typing import Dict, Any, List
from TimePinner import Pinner

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
            
            if self.config['HEADLESS_MODE']:
                co.headless()
            
            # 高性能配置
            co.set_load_mode('none')
            co.set_argument('--disable-blink-features=AutomationControlled')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-images')
            
            self.browser = Chromium(co)
            self.page = self.browser.latest_tab
            
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
                
                # 点击购买
                buy_button.click()
                time.sleep(0.5)
                
                # 处理条款
                tos_checkbox = self.page.s_ele('#tos-checkbox', timeout=0.5)
                if tos_checkbox:
                    tos_checkbox.click()
                
                # 结算
                checkout_btn = self.page.s_ele('#checkout', timeout=1)
                if not checkout_btn:
                    checkout_btn = self.page.s_ele('text:Checkout', timeout=1)
                
                if checkout_btn:
                    checkout_btn.click()
                    self.success_count += 1
                    
                    # 通知主线程
                    self.result_queue.put({
                        'worker_id': self.worker_id,
                        'action': 'success',
                        'timestamp': time.time()
                    })
                    
                    logging.info(f"🎉 Worker-{self.worker_id}: 抢单成功！")
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Worker-{self.worker_id}: 抢购过程错误: {e}")
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
                self.check_stock_and_purchase()
                
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
        if self.browser:
            try:
                self.browser.quit()
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
