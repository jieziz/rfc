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
from ..utils.linux_optimizer import apply_linux_optimizations
from typing import Dict, Any
import random

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
        
        # 稳定模式配置
        'DELAY_TIME': float(os.getenv("DELAY_TIME", "1.0")),
        'ELEMENT_TIMEOUT': float(os.getenv("ELEMENT_TIMEOUT", "5")),
        'PAGE_LOAD_TIMEOUT': int(os.getenv("PAGE_LOAD_TIMEOUT", "15")),
        'STOCK_CHECK_INTERVAL': float(os.getenv("STOCK_CHECK_INTERVAL", "0.5")),
        'LOGIN_CHECK_INTERVAL': int(os.getenv("LOGIN_CHECK_INTERVAL", "20")),  # 每20次检查登录
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
    co.set_load_mode('normal')  # 正常加载模式，更稳定
    
    # 基础稳定性参数
    stability_args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-web-security',
        '--start-maximized'
    ]

    for arg in stability_args:
        co.set_argument(arg)

    # 应用Linux环境优化（稳定性模式）
    co = apply_linux_optimizations(co, 'stability')
    
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
            for selector in email_selectors:
                try:
                    element = page.s_ele(selector, timeout=3)
                    if element:
                        page(selector).click()  # 先点击获得焦点
                        time.sleep(0.5)
                        page(selector).input(config['EMAIL'])
                        logging.info(f"成功输入邮箱: {selector}")
                        email_success = True
                        break
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
            return False
        
        time.sleep(1)
        
        # 输入密码 - 多次尝试
        password_success = False
        for attempt in range(3):
            for selector in password_selectors:
                try:
                    element = page.s_ele(selector, timeout=3)
                    if element:
                        page(selector).click()  # 先点击获得焦点
                        time.sleep(0.5)
                        page(selector).input(config['PASSWORD'])
                        logging.info(f"成功输入密码: {selector}")
                        password_success = True
                        break
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
    """稳定的购买流程"""
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
        
        # 等待页面响应
        time.sleep(2)
        
        # 步骤2: 处理条款（如果存在）
        tos_selectors = [
            '#tos-checkbox',
            '.tos-checkbox',
            'input[name="tos"]',
            'text:I agree',
            'text:同意条款'
        ]
        
        for selector in tos_selectors:
            try:
                element = page.s_ele(selector, timeout=1)
                if element:
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
                element = page.s_ele(selector, timeout=3)
                if element:
                    page(selector).click()
                    logging.info(f"点击结算: {selector}")
                    pinner.pin('稳定购买完成')
                    return True
            except:
                continue
        
        logging.warning("未找到结算按钮")
        return False
        
    except Exception as e:
        logging.error(f"稳定购买错误: {e}")
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
    
    try:
        # 稳定登录
        if not stable_login(page, config):
            logging.error("登录失败，退出")
            return
        
        success_count = 0
        total_checks = 0
        start_time = time.time()
        login_check_counter = 0
        
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
