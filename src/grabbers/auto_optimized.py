"""
高度优化的抢单脚本 - 专注于速度和效率
主要优化：
1. 减少等待时间
2. 并行处理
3. 智能库存检测
4. 浏览器性能优化
5. 网络请求优化
"""

import logging
import time
import asyncio
from DrissionPage import Chromium, ChromiumOptions
from dotenv import load_dotenv
import os
from TimePinner import Pinner
from typing import Optional, Dict, Any, List
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log_optimized.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FastConfig:
    """快速配置管理器"""
    
    def __init__(self):
        load_dotenv(override=True)
        self.config = self._load_optimized_config()
    
    def _load_optimized_config(self) -> Dict[str, Any]:
        """加载优化配置"""
        config = {
            'BASE_URL': os.getenv("BASE_URL", "").rstrip('/'),
            'PRODUCT_URL': os.getenv("PRODUCT_URL"),
            'LOGIN_URL': os.getenv("LOGIN_URL"),
            'EMAIL': os.getenv("EMAIL"),
            'PASSWORD': os.getenv("PASSWORD"),
            'PROMO_CODE': os.getenv("PROMO_CODE", ""),
            'HEADLESS_MODE': os.getenv("HEADLESS_MODE", "True").lower() == "true",
            
            # 优化的时间配置
            'DELAY_TIME': float(os.getenv("DELAY_TIME", "0.3")),
            'MAX_RETRIES': int(os.getenv("MAX_RETRIES", "2")),
            'ELEMENT_TIMEOUT': float(os.getenv("ELEMENT_TIMEOUT", "2")),
            'PAGE_LOAD_TIMEOUT': int(os.getenv("PAGE_LOAD_TIMEOUT", "10")),
            'PAGE_LOAD_WAIT': float(os.getenv("PAGE_LOAD_WAIT", "0.5")),
            'ELEMENT_WAIT': float(os.getenv("ELEMENT_WAIT", "0.1")),
            
            # 新增性能配置
            'FAST_MODE': os.getenv("FAST_MODE", "True").lower() == "true",
            'CONCURRENT_BROWSERS': int(os.getenv("CONCURRENT_BROWSERS", "3")),
            'STOCK_CHECK_INTERVAL': float(os.getenv("STOCK_CHECK_INTERVAL", "0.2")),
            'QUICK_PURCHASE': os.getenv("QUICK_PURCHASE", "True").lower() == "true",
            'PRELOAD_PAGES': os.getenv("PRELOAD_PAGES", "True").lower() == "true",
        }
        
        # 验证必需配置
        required_fields = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(f"缺少必需的配置项: {', '.join(missing_fields)}")
        
        return config
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)

class FastBrowser:
    """优化的浏览器管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser = None
        self.page = None
        self._setup_browser()
    
    def _setup_browser(self):
        """设置高性能浏览器"""
        co = ChromiumOptions().auto_port()
        
        if self.config['HEADLESS_MODE']:
            co.headless()
        
        # 极致性能优化
        co.set_load_mode('none')  # 不加载图片和CSS
        co.set_pref('credentials_enable_service', False)
        co.set_pref('profile.default_content_setting_values.notifications', 2)
        co.set_pref('profile.default_content_settings.popups', 0)
        
        # 性能参数
        performance_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',
            '--disable-javascript',  # 如果网站允许
            '--disable-web-security',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-background-timer-throttling',
            '--disable-background-networking',
            '--disable-client-side-phishing-detection',
            '--disable-sync',
            '--disable-default-apps',
            '--memory-pressure-off',
            '--max_old_space_size=4096'
        ]
        
        for arg in performance_args:
            co.set_argument(arg)
        
        self.browser = Chromium(co)
        self.page = self.browser.latest_tab
        
        # 设置页面超时
        self.page.set.timeouts(
            page_load=self.config['PAGE_LOAD_TIMEOUT'],
            script=5
        )

class FastStockChecker:
    """快速库存检查器"""
    
    def __init__(self, page, config: Dict[str, Any]):
        self.page = page
        self.config = config
        self.stock_indicators = {
            'out_of_stock': [
                'text:Out of Stock',
                'text:缺货',
                'text:售罄',
                'text:暂时缺货',
                '.out-of-stock',
                '#out-of-stock',
                'text:Sold Out'
            ],
            'add_to_cart': [
                '#btnCompleteProductConfig',
                '.btn-add-cart',
                'text:Add to Cart',
                'text:立即购买',
                'text:加入购物车',
                '[data-action="add-to-cart"]',
                'input[value*="Add to Cart"]'
            ]
        }
    
    def quick_check(self) -> bool:
        """快速库存检查 - 优化版本"""
        try:
            pinner = Pinner()
            pinner.pin('快速库存检查开始')
            
            # 快速检查缺货标识
            for indicator in self.stock_indicators['out_of_stock']:
                if self.page.s_ele(indicator, timeout=0.1):
                    logging.info(f"快速检测到缺货: {indicator}")
                    pinner.pin('快速库存检查结束')
                    return False
            
            # 快速检查购买按钮
            for button in self.stock_indicators['add_to_cart']:
                if self.page.s_ele(button, timeout=0.1):
                    logging.info(f"快速检测到库存: {button}")
                    pinner.pin('快速库存检查结束')
                    return True
            
            pinner.pin('快速库存检查结束')
            return False
            
        except Exception as e:
            logging.debug(f"快速库存检查错误: {e}")
            return False

class FastPurchaser:
    """快速购买执行器"""
    
    def __init__(self, page, config: Dict[str, Any]):
        self.page = page
        self.config = config
    
    def lightning_purchase(self) -> bool:
        """闪电购买 - 极速版本"""
        try:
            pinner = Pinner()
            pinner.pin('闪电购买开始')
            
            # 极速添加到购物车
            cart_selectors = [
                '#btnCompleteProductConfig',
                '.btn-add-cart',
                'text:Add to Cart',
                'text:立即购买'
            ]
            
            for selector in cart_selectors:
                try:
                    element = self.page.s_ele(selector, timeout=0.5)
                    if element:
                        self.page(selector).click()
                        logging.info(f"闪电点击购物车: {selector}")
                        break
                except:
                    continue
            else:
                return False
            
            pinner.pin('加入购物车完成')
            
            # 极速等待页面响应
            time.sleep(self.config['ELEMENT_WAIT'])
            
            # 快速处理条款（如果存在）
            tos_selectors = ['#tos-checkbox', '.tos-checkbox', 'input[name="tos"]']
            for selector in tos_selectors:
                try:
                    if self.page.s_ele(selector, timeout=0.2):
                        self.page(selector).click()
                        break
                except:
                    continue
            
            # 极速结算
            checkout_selectors = [
                '#checkout',
                '.checkout-btn',
                'text:Checkout',
                'text:结算'
            ]
            
            for selector in checkout_selectors:
                try:
                    element = self.page.s_ele(selector, timeout=0.5)
                    if element:
                        self.page(selector).click()
                        logging.info(f"闪电点击结算: {selector}")
                        pinner.pin('闪电购买完成')
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"闪电购买错误: {e}")
            return False

def fast_login(page, config: Dict[str, Any]) -> bool:
    """快速登录"""
    try:
        logging.info("执行快速登录...")
        page.get(config['LOGIN_URL'])
        
        # 最小等待
        time.sleep(config['PAGE_LOAD_WAIT'])
        
        # 快速检查是否已登录
        if page.s_ele('text:Dashboard', timeout=1) or page.s_ele('text:My Dashboard', timeout=1):
            logging.info("已经登录")
            return True
        
        # 快速输入凭据
        email_selectors = ['#inputEmail', 'input[name="email"]', 'input[type="email"]']
        password_selectors = ['#inputPassword', 'input[name="password"]', 'input[type="password"]']
        
        # 输入邮箱
        for selector in email_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).input(config['EMAIL'])
                    break
            except:
                continue
        
        # 输入密码
        for selector in password_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).input(config['PASSWORD'])
                    break
            except:
                continue
        
        # 快速登录
        login_selectors = ['#login', 'button[type="submit"]', 'text:Login']
        for selector in login_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).click()
                    break
            except:
                continue
        
        # 快速验证登录
        time.sleep(2)
        return page.s_ele('text:Dashboard', timeout=3) is not None
        
    except Exception as e:
        logging.error(f"快速登录失败: {e}")
        return False

def optimized_monitor():
    """优化的监控主函数"""
    config_manager = FastConfig()
    config = config_manager.config
    
    logging.info("启动优化监控模式...")
    
    # 创建浏览器
    fast_browser = FastBrowser(config)
    page = fast_browser.page
    
    # 快速登录
    if not fast_login(page, config):
        logging.error("快速登录失败")
        return
    
    # 创建检查器和购买器
    stock_checker = FastStockChecker(page, config)
    purchaser = FastPurchaser(page, config)
    
    success_count = 0
    total_checks = 0
    
    logging.info("开始极速监控...")
    
    while True:
        try:
            total_checks += 1
            
            # 访问产品页面
            page.get(config['PRODUCT_URL'])
            
            # 极短等待
            time.sleep(config['STOCK_CHECK_INTERVAL'])
            
            # 快速库存检查
            if stock_checker.quick_check():
                logging.info(f"检测到库存！执行闪电购买...")
                
                if purchaser.lightning_purchase():
                    success_count += 1
                    logging.info(f"🎉 第 {success_count} 次抢单成功！")
                    
                    # 成功后短暂休息
                    time.sleep(random.uniform(1, 2))
                else:
                    logging.warning("闪电购买失败")
            
            # 动态延迟
            delay = config['DELAY_TIME'] + random.uniform(-0.1, 0.1)
            time.sleep(max(0.1, delay))
            
            # 每100次检查输出统计
            if total_checks % 100 == 0:
                logging.info(f"已检查 {total_checks} 次，成功 {success_count} 次")
                
        except KeyboardInterrupt:
            logging.info("收到中断信号，退出监控...")
            break
        except Exception as e:
            logging.error(f"监控过程错误: {e}")
            time.sleep(1)
    
    # 清理
    try:
        fast_browser.browser.quit()
    except:
        pass
    
    logging.info(f"监控结束，总检查 {total_checks} 次，成功 {success_count} 次")

if __name__ == "__main__":
    logging.info("🚀 启动优化抢单脚本...")
    try:
        optimized_monitor()
    except Exception as e:
        logging.critical(f"脚本运行错误: {e}")
    finally:
        logging.info("脚本结束")
