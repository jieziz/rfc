"""
稳定版抢单器 - 专门为稳定模式设计
确保登录流程完整，适合网络不稳定的环境
"""

import logging
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from dotenv import load_dotenv
import os
from ..utils.TimePinner import Pinner

from typing import Dict, Any
import random

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

    # 设置自定义User-Agent（无头和有头模式都适用）
    custom_ua = config.get('CUSTOM_USER_AGENT', '')
    if custom_ua:
        co.set_argument(f'--user-agent={custom_ua}')
        logging.info(f"已设置自定义User-Agent: {custom_ua}")
    else:
        # 默认使用常见的桌面浏览器User-Agent
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        co.set_argument(f'--user-agent={default_ua}')
        logging.info("已设置默认User-Agent")

    return co

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("stable_grabber.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_stable_config() -> Dict[str, Any]:
    """加载稳定模式配置"""
    load_dotenv(override=True)

    config = {
        'BASE_URL': os.getenv("BASE_URL", "").rstrip('/'),
        'PRODUCT_URL': os.getenv("PRODUCT_URL"),
        'LOGIN_URL': os.getenv("LOGIN_URL"),
        'EMAIL': os.getenv("EMAIL"),
        'PASSWORD': os.getenv("PASSWORD"),
        'PROMO_CODE': os.getenv("PROMO_CODE", ""),
        'HEADLESS_MODE': os.getenv("HEADLESS_MODE", "False").lower() == "true",
        'CUSTOM_USER_AGENT': os.getenv("CUSTOM_USER_AGENT", ""),

        # 稳定模式配置
        'DELAY_TIME': float(os.getenv("DELAY_TIME", "1.0")),
        'ELEMENT_TIMEOUT': float(os.getenv("ELEMENT_TIMEOUT", "5")),
        'PAGE_LOAD_TIMEOUT': int(os.getenv("PAGE_LOAD_TIMEOUT", "15")),
        'STOCK_CHECK_INTERVAL': float(os.getenv("STOCK_CHECK_INTERVAL", "0.5")),
        'LOGIN_CHECK_INTERVAL': int(os.getenv("LOGIN_CHECK_INTERVAL", "20")),  # 每20次检查登录
        'PAYMENT_WAIT_TIME': int(os.getenv("PAYMENT_WAIT_TIME", "45")),  # 购买成功后等待用户付款的时间（稳定模式更长）

    }
    
    # 验证必需配置
    required_fields = ['PRODUCT_URL', 'LOGIN_URL', 'EMAIL', 'PASSWORD']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"缺少必需的配置项: {', '.join(missing_fields)}")
    
    return config

def create_stable_browser(config: Dict[str, Any]):
    """创建稳定的浏览器"""
    co = ChromiumOptions().auto_port()
    
    if config['HEADLESS_MODE']:
        co.headless()
    
    # 稳定性优先的配置
    co.set_load_mode('none')  # 正常加载模式，更稳定
    
    # 基础稳定性参数
    stability_args = [
        '--disable-dev-shm-usage',
        '--hide-crash-restore-bubble',
        '--start-maximized'
    ]

    for arg in stability_args:
        co.set_argument(arg)

    # 应用无头模式配置
    co = apply_headless_config(co, config)

    # 设置浏览器首选项
    co.set_pref('credentials_enable_service', False)

    
    # 使用ChromiumPage而不是Chromium（DrissionPage官方推荐）
    page = ChromiumPage(co)

    # 设置较长的超时时间
    page.set.timeouts(page_load=config['PAGE_LOAD_TIMEOUT'])

    return page, page  # 返回两次page保持兼容性

def stable_login(page, config: Dict[str, Any]) -> bool:
    """稳定的登录流程"""
    try:
        logging.info("开始稳定登录流程...")
        page.get(config['LOGIN_URL'])
        
        # 等待页面完全加载
        time.sleep(3)
        
        # 检查是否已登录
        dashboard_indicators = [
            'text:Dashboard', 
            'text:My Dashboard', 
            '.dashboard',
            'text:我的面板'
        ]
        
        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=2):
                logging.info("已经登录")
                return True
        
        logging.info("需要登录，开始输入凭据...")
        
        # 稳定的输入流程
        email_selectors = ['#inputEmail', 'input[name="email"]', 'input[type="email"]']
        password_selectors = ['#inputPassword', 'input[name="password"]', 'input[type="password"]']
        login_selectors = ['#login', 'button[type="submit"]', 'text:Login', 'text:登录']
        
        # 输入邮箱 - 多次尝试
        email_success = False
        for attempt in range(3):
            logging.info(f"尝试第 {attempt + 1} 次邮箱输入...")

            for selector in email_selectors:
                try:
                    element = page.s_ele(selector, timeout=3)
                    if element:
                        logging.info(f"找到邮箱输入框: {selector}")

                        # 清空输入框
                        page(selector).clear()
                        time.sleep(0.5)

                        # 点击获得焦点
                        page(selector).click()
                        time.sleep(0.5)

                        # 输入邮箱
                        page(selector).input(config['EMAIL'])
                        time.sleep(0.5)

                        # 验证输入是否成功
                        current_value = page(selector).value
                        if current_value and config['EMAIL'] in current_value:
                            logging.info(f"成功输入邮箱: {selector}")
                            email_success = True
                            break
                        else:
                            logging.warning(f"邮箱输入验证失败，当前值: {current_value}")
                    else:
                        logging.debug(f"未找到邮箱输入框: {selector}")
                except Exception as e:
                    logging.debug(f"输入邮箱失败 {selector}: {e}")
                    continue

            if email_success:
                break

            if attempt < 2:
                logging.warning(f"第 {attempt + 1} 次邮箱输入失败，重试...")
                time.sleep(2)

        if not email_success:
            logging.error("邮箱输入失败")
            # 输出页面信息用于调试
            try:
                current_url = page.url
                page_title = page.title
                logging.error(f"当前页面: {current_url}")
                logging.error(f"页面标题: {page_title}")

                # 查找所有输入框
                all_inputs = page.eles('tag:input')
                logging.error(f"页面上找到 {len(all_inputs)} 个输入框")
                for i, inp in enumerate(all_inputs[:5]):  # 只显示前5个
                    try:
                        inp_type = inp.attr('type') or 'text'
                        inp_name = inp.attr('name') or 'unknown'
                        inp_id = inp.attr('id') or 'unknown'
                        logging.error(f"  输入框 {i+1}: type={inp_type}, name={inp_name}, id={inp_id}")
                    except:
                        pass
            except Exception as e:
                logging.error(f"获取调试信息失败: {e}")

            return False
        
        time.sleep(1)
        
        # 输入密码 - 多次尝试
        password_success = False
        for attempt in range(3):
            logging.info(f"尝试第 {attempt + 1} 次密码输入...")

            for selector in password_selectors:
                try:
                    element = page.s_ele(selector, timeout=3)
                    if element:
                        logging.info(f"找到密码输入框: {selector}")

                        # 清空输入框
                        page(selector).clear()
                        time.sleep(0.5)

                        # 点击获得焦点
                        page(selector).click()
                        time.sleep(0.5)

                        # 输入密码
                        page(selector).input(config['PASSWORD'])
                        time.sleep(0.5)

                        # 验证输入是否成功（密码框通常不能读取值，所以只检查是否有值）
                        try:
                            current_value = page(selector).value
                            if current_value:  # 密码框有内容
                                logging.info(f"成功输入密码: {selector}")
                                password_success = True
                                break
                        except:
                            # 有些密码框不允许读取值，假设输入成功
                            logging.info(f"密码输入完成: {selector}")
                            password_success = True
                            break
                    else:
                        logging.debug(f"未找到密码输入框: {selector}")
                except Exception as e:
                    logging.debug(f"输入密码失败 {selector}: {e}")
                    continue

            if password_success:
                break

            if attempt < 2:
                logging.warning(f"第 {attempt + 1} 次密码输入失败，重试...")
                time.sleep(2)

        if not password_success:
            logging.error("密码输入失败")
            return False
        
        time.sleep(1)
        
        # 点击登录按钮 - 多次尝试
        login_success = False
        for attempt in range(3):
            for selector in login_selectors:
                try:
                    element = page.s_ele(selector, timeout=3)
                    if element:
                        page(selector).click()
                        logging.info(f"点击登录按钮: {selector}")
                        login_success = True
                        break
                except Exception as e:
                    logging.debug(f"点击登录失败 {selector}: {e}")
                    continue
            
            if login_success:
                break
            
            if attempt < 2:
                logging.warning(f"第 {attempt + 1} 次登录点击失败，重试...")
                time.sleep(2)
        
        if not login_success:
            logging.error("登录按钮点击失败")
            return False
        
        # 等待登录完成
        logging.info("等待登录处理...")
        time.sleep(5)
        
        # 验证登录结果
        for indicator in dashboard_indicators:
            if page.s_ele(indicator, timeout=5):
                logging.info("登录成功确认")
                return True
        
        # 检查错误信息
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
                logging.error(f"登录失败，检测到错误: {indicator}")
                return False
        
        logging.warning("登录状态不明确，假设成功")
        return True
        
    except Exception as e:
        logging.error(f"稳定登录失败: {e}")
        return False

def stable_stock_check(page) -> bool:
    """稳定的库存检查"""
    try:
        # 等待页面稳定
        time.sleep(1)
        
        # 检查缺货标识
        out_of_stock_indicators = [
            'text:Out of Stock',
            'text:缺货',
            'text:售罄',
            'text:Sold Out',
            'text:暂时缺货',
            '.out-of-stock',
            '#out-of-stock'
        ]
        
        for indicator in out_of_stock_indicators:
            if page.s_ele(indicator, timeout=1):
                return False
        
        # 检查购买按钮
        buy_button_selectors = [
            '#btnCompleteProductConfig',
            '.btn-add-cart',
            'text:Add to Cart',
            'text:立即购买',
            'text:加入购物车',
            '[data-action="add-to-cart"]'
        ]
        
        for selector in buy_button_selectors:
            if page.s_ele(selector, timeout=1):
                return True
        
        return False
        
    except Exception as e:
        logging.debug(f"库存检查错误: {e}")
        return False



def stable_purchase(page, config: Dict[str, Any]) -> bool:
    """稳定的购买流程 - 安全版本，避免在结算过程中被中断"""
    try:
        pinner = Pinner()
        pinner.pin('稳定购买开始')

        # 步骤1: 点击购买按钮
        buy_selectors = [
            '#btnCompleteProductConfig',
            '.btn-add-cart',
            'text:Add to Cart',
            'text:立即购买',
            'text:加入购物车'
        ]

        clicked = False
        for selector in buy_selectors:
            try:
                element = page.s_ele(selector, timeout=2)
                if element:
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

        # 步骤3: 等待页面稳定
        time.sleep(2)  # 稳定模式额外等待时间

        pinner.pin('页面稳定完成')

        # 步骤4: 处理条款（如果存在）
        tos_selectors = [
            '#tos-checkbox',
            '.tos-checkbox',
            'input[name="tos"]',
            'text:I agree',
            'text:同意条款'
        ]

        for selector in tos_selectors:
            try:
                element = page.s_ele(selector, timeout=2)
                if element:
                    page(selector).click()
                    logging.info(f"点击条款: {selector}")
                    break
            except:
                continue

        # 步骤5: 点击结算并等待进入付款页面
        checkout_selectors = [
            '#checkout',
            '.checkout-btn',
            'text:Checkout',
            'text:结算',
            'text:立即支付'
        ]

        for selector in checkout_selectors:
            try:
                element = page.s_ele(selector, timeout=3)
                if element:
                    page(selector).click()
                    logging.info(f"点击结算: {selector}")

                    # 等待进入付款页面
                    if wait_for_payment_page_stable(page):
                        pinner.pin('稳定购买完成 - 已进入付款页面')
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
        logging.error(f"稳定购买错误: {e}")
        return False


def wait_for_payment_page_stable(page, max_wait_time: int = 45) -> bool:
    """等待进入付款页面 - 稳定版本，等待时间更长"""
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
            'text:账单'
        ]

        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            # 检查是否已进入付款页面
            for indicator in payment_indicators:
                if page.s_ele(indicator, timeout=1):
                    logging.info(f"检测到付款页面标识: {indicator}")
                    return True

            # 检查URL是否包含付款相关关键词
            try:
                current_url = page.url.lower()
                payment_url_keywords = ['payment', 'checkout', 'order', 'cart', 'billing', 'invoice']

                for keyword in payment_url_keywords:
                    if keyword in current_url:
                        logging.info(f"URL包含付款关键词: {keyword}")
                        return True
            except:
                pass

            # 稳定模式等待时间更长
            time.sleep(1)

        logging.warning("等待付款页面超时")
        return False

    except Exception as e:
        logging.error(f"等待付款页面错误: {e}")
        return False

def stable_monitor():
    """稳定模式监控"""
    config = load_stable_config()
    
    logging.info("🛡️ 启动稳定版抢单器...")
    logging.info(f"产品URL: {config['PRODUCT_URL']}")
    logging.info(f"检查间隔: {config['STOCK_CHECK_INTERVAL']}秒")
    logging.info(f"延迟时间: {config['DELAY_TIME']}秒")
    logging.info(f"无头模式: {config['HEADLESS_MODE']}")
    
    # 创建浏览器
    _, page = create_stable_browser(config)

    # 初始化变量
    success_count = 0
    total_checks = 0
    start_time = time.time()
    login_check_counter = 0

    try:
        # 稳定登录
        if not stable_login(page, config):
            logging.error("登录失败，退出")
            return
        
        logging.info("开始稳定监控...")
        
        while True:
            try:
                total_checks += 1
                login_check_counter += 1
                
                # 定期检查登录状态
                if login_check_counter >= config['LOGIN_CHECK_INTERVAL']:
                    logging.info("定期检查登录状态...")
                    if not stable_login(page, config):
                        logging.warning("登录状态检查失败，继续监控...")
                    login_check_counter = 0
                
                # 访问产品页面
                page.get(config['PRODUCT_URL'])

                # 稳定等待
                time.sleep(config['STOCK_CHECK_INTERVAL'])

                # 稳定库存检查
                if stable_stock_check(page):
                    logging.info(f"🎯 第 {total_checks} 次检查: 检测到库存！")

                    # 稳定购买
                    if stable_purchase(page, config):
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

                        # 成功后休息
                        time.sleep(random.uniform(2, 5))
                    else:
                        logging.warning("购买失败")
                else:
                    # 每50次检查输出一次状态
                    if total_checks % 50 == 0:
                        runtime = time.time() - start_time
                        speed = total_checks / runtime if runtime > 0 else 0
                        logging.info(f"📊 已检查 {total_checks} 次，成功 {success_count} 次，速度 {speed:.2f} 次/秒")

                # 稳定延迟
                delay = config['DELAY_TIME'] + random.uniform(-0.1, 0.1)
                time.sleep(max(0.1, delay))
                
            except KeyboardInterrupt:
                logging.info("收到中断信号，退出监控...")
                break
            except Exception as e:
                logging.error(f"监控过程错误: {e}")
                time.sleep(2)
                
                # 错误后重新登录
                if total_checks % 10 == 0:
                    logging.info("错误后重新登录...")
                    stable_login(page, config)
    
    finally:
        # 清理
        try:
            page.quit()
        except:
            pass
        
        runtime = time.time() - start_time
        logging.info(f"稳定监控结束:")
        logging.info(f"  运行时间: {runtime:.1f}秒")
        logging.info(f"  总检查: {total_checks} 次")
        logging.info(f"  总成功: {success_count} 次")
        if runtime > 0:
            logging.info(f"  平均速度: {total_checks/runtime:.2f} 次/秒")

if __name__ == "__main__":
    logging.info("🛡️ 启动稳定版抢单器...")
    try:
        stable_monitor()
    except Exception as e:
        logging.critical(f"脚本运行错误: {e}")
    finally:
        logging.info("脚本结束")
