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

from typing import Dict, Any
import random
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
        co.set_argument('--no-sandbox')

        logging.info("已启用无头模式")
    else:
        logging.info("使用有头模式")

    return co

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
        'PAYMENT_WAIT_TIME': int(os.getenv("PAYMENT_WAIT_TIME", "30")),  # 购买成功后等待用户付款的时间
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
        '--disable-dev-shm-usage',
        '--hide-crash-restore-bubble',
        '--start-maximized'
    ]

    co.set_pref('credentials_enable_service', False)

    for arg in performance_args:
        co.set_argument(arg)

    # 应用无头模式配置
    co = apply_headless_config(co, config)

    # 设置浏览器首选项
    co.set_pref('credentials_enable_service', False)

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
        email_success = False
        for selector in email_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).clear()
                    page(selector).input(config['EMAIL'])
                    logging.info(f"快速输入邮箱: {selector}")
                    email_success = True
                    break
            except:
                continue

        if not email_success:
            logging.warning("快速邮箱输入失败")

        # 输入密码
        password_success = False
        for selector in password_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).clear()
                    page(selector).input(config['PASSWORD'])
                    logging.info(f"快速输入密码: {selector}")
                    password_success = True
                    break
            except:
                continue

        if not password_success:
            logging.warning("快速密码输入失败")

        # 点击登录
        login_clicked = False
        for selector in login_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).click()
                    logging.info(f"快速点击登录: {selector}")
                    login_clicked = True
                    break
            except:
                continue

        if not login_clicked:
            logging.warning("快速登录点击失败")
        
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
    """闪电购买 - 安全版本，避免在结算过程中被中断"""
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

        # 步骤2: 等待页面响应和系统验证
        logging.info("等待5秒进行系统验证（反机器人验证、库存检查等）...")
        time.sleep(5)  # 等待5秒确保系统验证通过（反机器人验证、库存检查等）
        logging.info("系统验证等待完成")

        # 步骤3: 处理条款（如果存在）
        tos_selectors = [
            '#tos-checkbox',
            '.tos-checkbox',
            'input[name="tos"]',
            'text:I agree'
        ]

        for selector in tos_selectors:
            try:
                if page.s_ele(selector, timeout=0.5):
                    page(selector).click()
                    logging.info(f"点击条款: {selector}")
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
                if page.s_ele(selector, timeout=1):
                    page(selector).click()
                    logging.info(f"点击结算: {selector}")

                    # 等待进入付款页面
                    if wait_for_payment_page(page):
                        pinner.pin('闪电购买完成 - 已进入付款页面')
                        logging.info("已进入付款页面，请在浏览器中完成付款...")

                        # 不立即返回，让用户有时间看到付款页面
                        # 这里不做额外等待，让主循环处理等待逻辑
                        return True
                    else:
                        logging.warning("未能进入付款页面")
                        return False
            except:
                continue

        logging.warning("未找到结算按钮")
        return False

    except Exception as e:
        logging.error(f"闪电购买错误: {e}")
        return False


def wait_for_payment_page(page, max_wait_time: int = 15) -> bool:
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
        logging.info("开始等待付款页面...")

        while time.time() - start_time < max_wait_time:
            # 检查是否已进入付款页面
            for indicator in payment_indicators:
                if page.s_ele(indicator, timeout=0.3):
                    logging.info(f"检测到付款页面标识: {indicator}")
                    return True

            # 检查URL是否包含付款相关关键词
            try:
                current_url = page.url.lower()
                payment_url_keywords = ['payment', 'checkout', 'order', 'cart', 'billing', 'pay']

                for keyword in payment_url_keywords:
                    if keyword in current_url:
                        logging.info(f"URL包含付款关键词: {keyword} - {current_url}")
                        return True
            except:
                pass

            # 短暂等待后继续检查
            time.sleep(0.5)

        logging.warning(f"等待付款页面超时 ({max_wait_time}秒)")
        return False

    except Exception as e:
        logging.error(f"等待付款页面错误: {e}")
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

                        # 购买成功后，给用户足够时间完成付款
                        wait_time = config['PAYMENT_WAIT_TIME']
                        logging.info(f"购买成功，等待{wait_time}秒让用户完成付款...")
                        time.sleep(wait_time)  # 给用户配置的时间完成付款

                        # 如果配置为单次购买成功后停止，则退出循环
                        if config.get('STOP_AFTER_SUCCESS', True):
                            logging.info("购买成功，根据配置停止运行")
                            break

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
