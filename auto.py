import logging
import time
from DrissionPage import Chromium, ChromiumOptions
from dotenv import load_dotenv
import os
from TimePinner import Pinner
from typing import Optional, Dict, Any
import random





logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("log.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    load_dotenv(override=True)
    base_url = os.getenv("BASE_URL", "").rstrip('/')

    config = {
        'BASE_URL': base_url,
        'PRODUCT_URL': os.getenv("PRODUCT_URL"),
        'LOGIN_URL': os.getenv("LOGIN_URL"),
        'EMAIL': os.getenv("EMAIL"),
        'PASSWORD': os.getenv("PASSWORD"),
        'PROMO_CODE': os.getenv("PROMO_CODE", ""),
        'HEADLESS_MODE': os.getenv("HEADLESS_MODE", "False").lower() == "true",
        'DELAY_TIME': float(os.getenv("DELAY_TIME", "1")),
        'MAX_RETRIES': int(os.getenv("MAX_RETRIES", "3")),
        'ELEMENT_TIMEOUT': int(os.getenv("ELEMENT_TIMEOUT", "3")),
        'PAGE_LOAD_TIMEOUT': int(os.getenv("PAGE_LOAD_TIMEOUT", "15")),
        'PAGE_LOAD_WAIT': float(os.getenv("PAGE_LOAD_WAIT", "1")),
        'ELEMENT_WAIT': float(os.getenv("ELEMENT_WAIT", "0.3")),
        'FAST_MODE': os.getenv("FAST_MODE", "True").lower() == "true",
        'CONCURRENT_BROWSERS': int(os.getenv("CONCURRENT_BROWSERS", "1")),
        'STOCK_CHECK_INTERVAL': float(os.getenv("STOCK_CHECK_INTERVAL", "0.5"))
    }

    # 验证必需的配置
    required_fields = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
    missing_fields = [field for field in required_fields if not config.get(field)]

    if missing_fields:
        raise ValueError(f"缺少必需的配置项: {', '.join(missing_fields)}")

    return config

def check_stock(page) -> bool:
    """检查库存状态，返回True表示有库存"""
    try:
        pinner = Pinner()
        pinner.pin('检查库存开始')

        # 等待页面加载完成
        page.wait.load_start(timeout=5)

        # 检查多种缺货标识
        out_of_stock_indicators = [
            'text:Out of Stock',
            'text:缺货',
            'text:售罄',
            'text:暂时缺货',
            '.out-of-stock',
            '#out-of-stock'
        ]

        has_stock = True
        for indicator in out_of_stock_indicators:
            if page.s_ele(indicator, timeout=0.5):
                has_stock = False
                logging.info(f"检测到缺货标识: {indicator}")
                break

        # 检查是否有添加到购物车按钮
        if has_stock:
            add_to_cart_buttons = [
                '#btnCompleteProductConfig',
                '.btn-add-cart',
                'text:Add to Cart',
                'text:立即购买'
            ]

            button_found = False
            for button in add_to_cart_buttons:
                if page.s_ele(button, timeout=0.5):
                    button_found = True
                    logging.info(f"找到购买按钮: {button}")
                    break

            if not button_found:
                logging.warning("未找到购买按钮，可能缺货")
                has_stock = False

        pinner.pin('检查库存结束')
        page.stop_loading()

        status = "有库存" if has_stock else "缺货"
        logging.info(f"库存检查结果: {status}")
        return has_stock

    except Exception as e:
        logging.warning(f"检查库存时发生错误: {e}")
        return False


def wait_and_click_element(page, selectors: list, element_name: str, timeout: int = 10, max_retries: int = 3) -> bool:
    """等待并点击元素，支持多个选择器和重试"""
    for retry in range(max_retries):
        for selector in selectors:
            try:
                # 先检查元素是否存在
                if page.s_ele(selector, timeout=timeout):
                    # 使用DrissionPage的直接方式点击
                    page(selector).click()
                    logging.info(f"成功点击 {element_name}: {selector}")
                    return True
            except Exception as e:
                logging.debug(f"尝试点击 {selector} 失败: {e}")
                continue

        if retry < max_retries - 1:
            logging.warning(f"第 {retry + 1} 次尝试点击 {element_name} 失败，等待后重试...")
            time.sleep(random.uniform(1, 3))

    logging.error(f"所有尝试都失败，无法点击 {element_name}")
    return False

def perform_purchase(page, config: Dict[str, Any]) -> bool:
    """执行下单流程"""
    try:
        pinner = Pinner()
        pinner.pin('执行下单开始')

        # 等待页面完全加载
        page.wait.load_start(timeout=10)
        time.sleep(random.uniform(1, 2))

        # 尝试多种添加到购物车按钮
        add_cart_selectors = [
            '#btnCompleteProductConfig',
            '.btn-add-cart',
            'text:Add to Cart',
            'text:立即购买',
            'text:加入购物车',
            '[data-action="add-to-cart"]'
        ]

        if not wait_and_click_element(page, add_cart_selectors, "添加到购物车按钮"):
            return False

        # 等待页面响应
        page.wait.load_start(timeout=15)
        pinner.pin('加入购物车用时')
        time.sleep(random.uniform(1, 2))

        # 尝试多种同意条款复选框
        tos_selectors = [
            '#tos-checkbox',
            '.tos-checkbox',
            'input[name="tos"]',
            'text:I agree',
            'text:同意条款'
        ]

        if not wait_and_click_element(page, tos_selectors, "同意条款复选框", timeout=5):
            logging.warning("未找到同意条款复选框，继续执行...")

        # 尝试多种结算按钮
        checkout_selectors = [
            '#checkout',
            '.checkout-btn',
            'text:Checkout',
            'text:结算',
            'text:立即支付',
            '[data-action="checkout"]'
        ]

        if not wait_and_click_element(page, checkout_selectors, "结算按钮"):
            return False

        # 等待结算页面加载
        page.wait.load_start(timeout=20)
        pinner.pin('进入结算页面用时')

        # 智能等待，而不是固定30秒
        max_wait_time = 30
        wait_interval = 2
        total_waited = 0

        while total_waited < max_wait_time:
            # 检查是否有成功标识
            success_indicators = [
                'text:Order Successful',
                'text:订单成功',
                'text:Payment Successful',
                'text:支付成功',
                '.order-success',
                '.payment-success'
            ]

            for indicator in success_indicators:
                if page.s_ele(indicator, timeout=1):
                    logging.info("检测到订单成功标识")
                    pinner.pin('订单提交用时')
                    return True

            time.sleep(wait_interval)
            total_waited += wait_interval

        logging.info("订单提交完成（未检测到明确成功标识）")
        pinner.pin('订单提交用时')
        return True

    except Exception as e:
        logging.error(f"下单过程中发生错误: {e}")
        return False

def check_and_handle_login(page, config: Dict[str, Any]) -> bool:
    """检查登录状态并处理登录"""
    try:
        logging.info("检查登录状态...")
        page.get(config['LOGIN_URL'])

        # 等待页面完全加载
        logging.info("等待登录页面加载...")
        page.wait.load_start(timeout=20)

        # 额外等待确保页面元素完全渲染
        time.sleep(5)

        # 等待页面中的关键元素出现，确保页面已完全加载
        key_elements = [
            '#inputEmail',
            'input[name="email"]',
            'input[type="email"]',
            'text:My Dashboard',  # 如果已登录
            'text:Dashboard'
        ]

        element_found = False
        for element in key_elements:
            if page.s_ele(element, timeout=10):
                logging.info(f"检测到关键元素: {element}，页面加载完成")
                element_found = True
                break

        if not element_found:
            logging.warning("未检测到关键元素，但继续执行...")

        # 再等待一下确保页面稳定
        time.sleep(2)

        # 检查是否已经登录
        dashboard_indicators = [
            'text:My Dashboard',
            'text:Dashboard',
            'text:我的面板',
            '.dashboard',
            '#dashboard'
        ]

        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=3):
                logging.info("已经登录，跳过登录步骤")
                page.stop_loading()
                return True

        logging.info("需要登录，开始登录流程...")

        # 尝试输入登录信息 - 增强等待机制
        def try_input_credentials():
            """尝试输入登录凭据，带有智能等待"""
            # 邮箱输入框选择器
            email_selectors = [
                '#inputEmail',
                'input[name="email"]',
                'input[type="email"]',
                '.email-input'
            ]

            # 密码输入框选择器
            password_selectors = [
                '#inputPassword',
                'input[name="password"]',
                'input[type="password"]',
                '.password-input'
            ]

            # 等待邮箱输入框出现并输入
            logging.info("等待邮箱输入框出现...")
            email_success = False

            # 增加等待时间，确保元素完全加载
            for attempt in range(3):  # 最多尝试3次
                for selector in email_selectors:
                    try:
                        # 等待元素出现
                        element = page.s_ele(selector, timeout=5)
                        if element:
                            logging.info(f"找到邮箱输入框: {selector}")

                            # 等待元素可交互
                            time.sleep(1)

                            # 点击获得焦点
                            page(selector).click()
                            time.sleep(0.5)

                            # 输入邮箱
                            page(selector).input(config['EMAIL'])
                            logging.info(f"成功输入邮箱")
                            email_success = True
                            break
                    except Exception as e:
                        logging.debug(f"尝试 {selector} 失败: {e}")
                        continue

                if email_success:
                    break

                if attempt < 2:
                    logging.warning(f"第 {attempt + 1} 次邮箱输入尝试失败，等待后重试...")
                    time.sleep(2)

            if not email_success:
                logging.error("所有邮箱输入尝试都失败")
                return False

            time.sleep(1)

            # 等待密码输入框并输入
            logging.info("等待密码输入框出现...")
            password_success = False

            for attempt in range(3):  # 最多尝试3次
                for selector in password_selectors:
                    try:
                        # 等待元素出现
                        element = page.s_ele(selector, timeout=5)
                        if element:
                            logging.info(f"找到密码输入框: {selector}")

                            # 等待元素可交互
                            time.sleep(1)

                            # 点击获得焦点
                            page(selector).click()
                            time.sleep(0.5)

                            # 输入密码
                            page(selector).input(config['PASSWORD'])
                            logging.info(f"成功输入密码")
                            password_success = True
                            break
                    except Exception as e:
                        logging.debug(f"尝试 {selector} 失败: {e}")
                        continue

                if password_success:
                    break

                if attempt < 2:
                    logging.warning(f"第 {attempt + 1} 次密码输入尝试失败，等待后重试...")
                    time.sleep(2)

            if not password_success:
                logging.error("所有密码输入尝试都失败")
                return False

            return True

        if not try_input_credentials():
            return False

        # 输入完成后等待一下
        time.sleep(2)

        # 查找并点击登录按钮
        logging.info("查找登录按钮...")
        login_selectors = [
            '#login',
            'button[type="submit"]',
            'input[type="submit"]',
            'text:Login',
            'text:登录',
            '.login-btn'
        ]

        login_success = False
        for attempt in range(3):  # 最多尝试3次
            for selector in login_selectors:
                try:
                    # 等待登录按钮出现
                    element = page.s_ele(selector, timeout=5)
                    if element:
                        logging.info(f"找到登录按钮: {selector}")

                        # 等待按钮可点击
                        time.sleep(1)

                        # 点击登录按钮
                        page(selector).click()
                        logging.info("成功点击登录按钮")
                        login_success = True
                        break
                except Exception as e:
                    logging.debug(f"点击登录按钮失败 {selector}: {e}")
                    continue

            if login_success:
                break

            if attempt < 2:
                logging.warning(f"第 {attempt + 1} 次登录按钮点击尝试失败，等待后重试...")
                time.sleep(2)

        if not login_success:
            logging.error("未找到或无法点击登录按钮")
            return False

        # 等待登录完成
        logging.info("等待登录处理...")
        page.wait.load_start(timeout=30)
        time.sleep(5)  # 增加等待时间，确保登录处理完成

        # 验证登录是否成功
        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=5):
                logging.info("登录成功")
                return True

        # 检查是否有错误信息
        error_indicators = [
            'text:Invalid',
            'text:Error',
            'text:错误',
            'text:失败',
            '.error',
            '.alert-danger'
        ]

        for indicator in error_indicators:
            if page.s_ele(indicator, timeout=2):
                logging.error(f"登录失败，检测到错误信息: {indicator}")
                return False

        logging.warning("登录状态不明确，假设登录成功")
        return True

    except Exception as e:
        logging.error(f"登录检查过程发生错误: {e}")
        return False


def monitor_stock():
    """主监控函数"""
    config = load_config()

    # 浏览器配置优化
    co = ChromiumOptions().auto_port()
    if config['HEADLESS_MODE']:
        co.headless()

    # 性能优化设置
    co.set_load_mode('none')
    co.set_pref('credentials_enable_service', False)
    co.set_argument('--hide-crash-restore-bubble')
    co.set_argument('--start-maximized')
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--no-sandbox')

    browser = Chromium(co)
    page = browser.latest_tab
    pinner = Pinner()
    pinner.pin('脚本计时开始')

    # 检查登录状态并处理
    if not check_and_handle_login(page, config):
        logging.error("登录失败，脚本退出")
        return

    # 预处理优惠码
    if config.get('PROMO_CODE'):
        try:
            page.get(config['BASE_URL']+"/cart.php?a=view")
            time.sleep(2)

            promo_selectors = [
                '#inputPromotionCode',
                '.promo-code-input',
                'input[name="promocode"]'
            ]

            promo_input = None
            for selector in promo_selectors:
                promo_input = page.s_ele(selector, timeout=2)
                if promo_input:
                    break

            if promo_input:
                # 使用DrissionPage的直接方式输入
                for selector in promo_selectors:
                    try:
                        if page.s_ele(selector, timeout=1):
                            page(selector).input(config['PROMO_CODE'])
                            logging.info(f"成功输入优惠码: {selector}")
                            break
                    except Exception as e:
                        logging.debug(f"输入优惠码失败 {selector}: {e}")
                        continue

                validate_selectors = [
                    '@name=validatepromo',
                    '.validate-promo',
                    'text:Apply',
                    'text:应用'
                ]

                for selector in validate_selectors:
                    validate_btn = page.s_ele(selector, timeout=2)
                    if validate_btn:
                        validate_btn.click()
                        page.wait.load_start(timeout=10)
                        pinner.pin('使用优惠码用时')
                        break
            else:
                logging.warning("未找到优惠码输入框")
        except Exception as e:
            logging.warning(f"应用优惠码时发生错误: {e}")

    success_count = 0
    consecutive_failures = 0
    max_consecutive_failures = 5

    logging.info("开始监控库存...")

    while True:
        try:
            # 动态重新加载配置（支持运行时修改）
            current_config = load_config()

            # 访问产品页面
            page.get(current_config['PRODUCT_URL'])

            # 添加随机延迟，避免被检测
            time.sleep(random.uniform(0.5, 1.5))

            if check_stock(page):
                logging.info("检测到库存，尝试下单...")

                if perform_purchase(page, current_config):
                    success_count += 1
                    consecutive_failures = 0
                    logging.info(f"第 {success_count} 次下单成功！继续监控新的库存...")

                    # 成功后稍作休息
                    time.sleep(random.uniform(2, 5))
                else:
                    consecutive_failures += 1
                    logging.error(f"下单失败（连续失败 {consecutive_failures} 次），继续监控...")

                    # 连续失败太多次，增加等待时间
                    if consecutive_failures >= max_consecutive_failures:
                        logging.warning(f"连续失败 {consecutive_failures} 次，延长等待时间...")
                        time.sleep(current_config['DELAY_TIME'] * 3)
                        consecutive_failures = 0  # 重置计数器
            else:
                # 重置连续失败计数器（因为这不是下单失败）
                consecutive_failures = 0

            # 动态延迟时间
            base_delay = current_config['DELAY_TIME']
            actual_delay = base_delay + random.uniform(-0.5, 0.5)
            time.sleep(max(0.1, actual_delay))

        except KeyboardInterrupt:
            logging.info("收到中断信号，正在退出...")
            break
        except Exception as e:
            consecutive_failures += 1
            logging.error(f"监控过程发生错误: {e}")

            # 错误后等待更长时间
            error_delay = current_config.get('DELAY_TIME', 5) * 2
            time.sleep(error_delay)

            # 如果连续错误太多，尝试重新初始化浏览器
            if consecutive_failures >= max_consecutive_failures:
                logging.warning("连续错误过多，尝试重新初始化浏览器...")
                try:
                    browser.quit()
                    time.sleep(5)
                    browser = Chromium(co)
                    page = browser.latest_tab
                    if not check_and_handle_login(page, current_config):
                        logging.error("重新登录失败")
                        break
                    consecutive_failures = 0
                except Exception as init_error:
                    logging.error(f"重新初始化浏览器失败: {init_error}")
                    break

    # 清理资源
    try:
        browser.quit()
    except:
        pass

    logging.info(f"监控结束，总共成功下单 {success_count} 次")



if __name__ == "__main__":
    logging.info("脚本启动。")
    try:
        monitor_stock()
    except Exception as e:
        logging.critical(f"脚本运行过程中发生严重错误: {e}")
    finally:
        logging.info("脚本结束运行。")