"""
简化版快速抢单器
避免复杂的浏览器池，直接优化原有逻辑
专注于速度提升，稳定可靠
"""

import logging
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from dotenv import load_dotenv
import os
from ..utils.TimePinner import Pinner
from ..utils.linux_optimizer import apply_linux_optimizations
from typing import Dict, Any
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_fast.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_fast_config() -> Dict[str, Any]:
    """加载快速配置"""
    load_dotenv(override=True)
    
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
        'ELEMENT_TIMEOUT': float(os.getenv("ELEMENT_TIMEOUT", "2")),
        'PAGE_LOAD_TIMEOUT': int(os.getenv("PAGE_LOAD_TIMEOUT", "10")),
        'STOCK_CHECK_INTERVAL': float(os.getenv("STOCK_CHECK_INTERVAL", "0.2")),
    }
    
    # 验证必需配置
    required_fields = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"缺少必需的配置项: {', '.join(missing_fields)}")
    
    return config

def create_fast_browser(config: Dict[str, Any]):
    """创建优化的浏览器"""
    co = ChromiumOptions().auto_port()
    
    if config['HEADLESS_MODE']:
        co.headless()
    
    # 性能优化设置
    co.set_load_mode('none')  # 不加载图片和CSS
    
    # 性能参数
    performance_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-plugins',
        '--disable-images',
        '--disable-web-security',
        '--disable-features=TranslateUI',
        '--memory-pressure-off',
        '--max_old_space_size=2048'
    ]

    for arg in performance_args:
        co.set_argument(arg)

    # 应用Linux环境优化
    co = apply_linux_optimizations(co, 'performance')
    
    # 使用ChromiumPage而不是Chromium（DrissionPage官方推荐）
    page = ChromiumPage(co)

    # 设置超时
    page.set.timeouts(page_load=config['PAGE_LOAD_TIMEOUT'])

    return page, page  # 返回两次page保持兼容性

def fast_login(page, config: Dict[str, Any]) -> bool:
    """快速登录"""
    try:
        logging.info("执行快速登录...")
        page.get(config['LOGIN_URL'])
        
        # 最小等待
        time.sleep(0.5)
        
        # 快速检查是否已登录
        dashboard_indicators = ['text:Dashboard', 'text:My Dashboard', '.dashboard']
        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=1):
                logging.info("已经登录")
                return True
        
        # 快速输入凭据
        email_selectors = ['#inputEmail', 'input[name="email"]', 'input[type="email"]']
        password_selectors = ['#inputPassword', 'input[name="password"]', 'input[type="password"]']
        login_selectors = ['#login', 'button[type="submit"]', 'text:Login']
        
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
        
        # 点击登录
        for selector in login_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).click()
                    break
            except:
                continue
        
        # 快速验证登录
        time.sleep(2)
        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=3):
                logging.info("登录成功")
                return True
        
        logging.warning("登录状态不明确，继续执行")
        return True
        
    except Exception as e:
        logging.error(f"快速登录失败: {e}")
        return False

def ultra_fast_stock_check(page) -> bool:
    """超快速库存检查"""
    try:
        # 极速检查缺货标识
        out_of_stock_indicators = [
            'text:Out of Stock',
            'text:缺货',
            'text:售罄',
            'text:Sold Out',
            '.out-of-stock',
            '#out-of-stock'
        ]
        
        # 超短超时检查缺货
        for indicator in out_of_stock_indicators:
            if page.s_ele(indicator, timeout=0.05):
                return False
        
        # 检查购买按钮
        buy_button_selectors = [
            '#btnCompleteProductConfig',
            '.btn-add-cart',
            'text:Add to Cart',
            'text:立即购买',
            'text:加入购物车'
        ]
        
        # 超短超时检查购买按钮
        for selector in buy_button_selectors:
            if page.s_ele(selector, timeout=0.05):
                return True
        
        return False
        
    except Exception as e:
        logging.debug(f"库存检查错误: {e}")
        return False

def lightning_purchase(page, config: Dict[str, Any]) -> bool:
    """闪电购买"""
    try:
        pinner = Pinner()
        pinner.pin('闪电购买开始')
        
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
                if page.s_ele(selector, timeout=0.3):
                    page(selector).click()
                    logging.info(f"点击购买按钮: {selector}")
                    clicked = True
                    break
            except:
                continue
        
        if not clicked:
            logging.warning("未找到购买按钮")
            return False
        
        pinner.pin('点击购买按钮')
        
        # 最小等待
        time.sleep(0.1)
        
        # 步骤2: 处理条款（如果存在）
        tos_selectors = [
            '#tos-checkbox',
            '.tos-checkbox',
            'input[name="tos"]',
            'text:I agree'
        ]
        
        for selector in tos_selectors:
            try:
                if page.s_ele(selector, timeout=0.1):
                    page(selector).click()
                    logging.info(f"点击条款: {selector}")
                    break
            except:
                continue
        
        # 步骤3: 点击结算
        checkout_selectors = [
            '#checkout',
            '.checkout-btn',
            'text:Checkout',
            'text:结算',
            'text:立即支付'
        ]
        
        for selector in checkout_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).click()
                    logging.info(f"点击结算: {selector}")
                    pinner.pin('闪电购买完成')
                    return True
            except:
                continue
        
        logging.warning("未找到结算按钮")
        return False
        
    except Exception as e:
        logging.error(f"闪电购买错误: {e}")
        return False

def simple_fast_monitor():
    """简化版快速监控"""
    config = load_fast_config()
    
    logging.info("🚀 启动简化版快速抢单器...")
    logging.info(f"产品URL: {config['PRODUCT_URL']}")
    logging.info(f"检查间隔: {config['STOCK_CHECK_INTERVAL']}秒")
    logging.info(f"延迟时间: {config['DELAY_TIME']}秒")
    
    # 创建浏览器
    _, page = create_fast_browser(config)
    
    try:
        # 快速登录
        if not fast_login(page, config):
            logging.error("登录失败，退出")
            return
        
        success_count = 0
        total_checks = 0
        start_time = time.time()
        
        logging.info("开始极速监控...")
        
        while True:
            try:
                total_checks += 1
                
                # 访问产品页面
                page.get(config['PRODUCT_URL'])
                
                # 极短等待
                time.sleep(config['STOCK_CHECK_INTERVAL'])
                
                # 超快速库存检查
                if ultra_fast_stock_check(page):
                    logging.info(f"🎯 第 {total_checks} 次检查: 检测到库存！")
                    
                    # 闪电购买
                    if lightning_purchase(page, config):
                        success_count += 1
                        logging.info(f"🎉 第 {success_count} 次抢单成功！")
                        
                        # 成功后短暂休息
                        time.sleep(random.uniform(1, 2))
                    else:
                        logging.warning("购买失败")
                else:
                    # 每100次检查输出一次状态
                    if total_checks % 100 == 0:
                        runtime = time.time() - start_time
                        speed = total_checks / runtime if runtime > 0 else 0
                        logging.info(f"📊 已检查 {total_checks} 次，成功 {success_count} 次，速度 {speed:.2f} 次/秒")
                
                # 动态延迟
                delay = config['DELAY_TIME'] + random.uniform(-0.05, 0.05)
                time.sleep(max(0.05, delay))
                
            except KeyboardInterrupt:
                logging.info("收到中断信号，退出监控...")
                break
            except Exception as e:
                logging.error(f"监控过程错误: {e}")
                time.sleep(1)
                
                # 如果连续错误，尝试重新登录
                if total_checks % 50 == 0:
                    logging.info("尝试重新登录...")
                    fast_login(page, config)
    
    finally:
        # 清理
        try:
            page.quit()
        except:
            pass
        
        runtime = time.time() - start_time
        logging.info(f"监控结束:")
        logging.info(f"  运行时间: {runtime:.1f}秒")
        logging.info(f"  总检查: {total_checks} 次")
        logging.info(f"  总成功: {success_count} 次")
        if runtime > 0:
            logging.info(f"  平均速度: {total_checks/runtime:.2f} 次/秒")

if __name__ == "__main__":
    logging.info("🚀 启动简化版快速抢单器...")
    try:
        simple_fast_monitor()
    except Exception as e:
        logging.critical(f"脚本运行错误: {e}")
    finally:
        logging.info("脚本结束")
