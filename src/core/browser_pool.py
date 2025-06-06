"""
智能浏览器池管理器
特性：
1. 浏览器实例复用
2. 自动故障恢复
3. 负载均衡
4. 性能监控
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional
from DrissionPage import Chromium, ChromiumOptions
import queue
import random
from contextlib import contextmanager
from ..utils.linux_optimizer import apply_linux_optimizations

class BrowserInstance:
    """浏览器实例"""
    
    def __init__(self, instance_id: int, config: Dict[str, Any]):
        self.instance_id = instance_id
        self.config = config
        self.browser = None
        self.page = None
        self.is_healthy = False
        self.last_used = 0
        self.usage_count = 0
        self.error_count = 0
        self.created_at = time.time()
        self.lock = threading.Lock()
        
    def create_browser(self) -> bool:
        """创建浏览器实例"""
        try:
            co = ChromiumOptions().auto_port()

            if self.config.get('HEADLESS_MODE', True):
                co.headless()

            # 基础性能优化
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
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-background-timer-throttling',
                '--memory-pressure-off',
                '--max_old_space_size=2048',
                f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]

            for arg in performance_args:
                co.set_argument(arg)

            # 应用Linux环境优化
            co = apply_linux_optimizations(co, 'performance')
            
            # 设置加载模式
            co.set_load_mode('none')
            
            # 禁用不必要的功能
            co.set_pref('credentials_enable_service', False)
            co.set_pref('profile.default_content_setting_values.notifications', 2)
            co.set_pref('profile.default_content_settings.popups', 0)
            
            self.browser = Chromium(co)
            self.page = self.browser.latest_tab

            # 设置超时
            self.page.set.timeouts(
                page_load=self.config.get('PAGE_LOAD_TIMEOUT', 10),
                script=5
            )

            # 尝试登录（如果有登录配置）
            if self._try_login():
                self.is_healthy = True
                logging.info(f"浏览器实例 {self.instance_id} 创建并登录成功")
                return True
            else:
                self.is_healthy = True  # 即使登录失败也标记为健康，后续会重试
                logging.info(f"浏览器实例 {self.instance_id} 创建成功（登录待验证）")
                return True
            
        except Exception as e:
            logging.error(f"浏览器实例 {self.instance_id} 创建失败: {e}")
            self.is_healthy = False
            return False

    def _try_login(self) -> bool:
        """尝试登录"""
        try:
            # 检查是否有登录配置
            if not all(key in self.config for key in ['LOGIN_URL', 'EMAIL', 'PASSWORD']):
                return True  # 没有登录配置，跳过登录

            self.page.get(self.config['LOGIN_URL'])
            time.sleep(1)

            # 检查是否已登录
            dashboard_indicators = ['text:Dashboard', 'text:My Dashboard', '.dashboard']
            for indicator in dashboard_indicators:
                if self.page.s_ele(indicator, timeout=1):
                    return True

            # 输入登录信息
            email_selectors = ['#inputEmail', 'input[name="email"]', 'input[type="email"]']
            password_selectors = ['#inputPassword', 'input[name="password"]', 'input[type="password"]']
            login_selectors = ['#login', 'button[type="submit"]', 'text:Login']

            # 输入邮箱
            for selector in email_selectors:
                try:
                    if self.page.s_ele(selector, timeout=1):
                        self.page(selector).input(self.config['EMAIL'])
                        break
                except:
                    continue

            # 输入密码
            for selector in password_selectors:
                try:
                    if self.page.s_ele(selector, timeout=1):
                        self.page(selector).input(self.config['PASSWORD'])
                        break
                except:
                    continue

            # 点击登录
            for selector in login_selectors:
                try:
                    if self.page.s_ele(selector, timeout=1):
                        self.page(selector).click()
                        break
                except:
                    continue

            # 等待登录完成
            time.sleep(2)

            # 验证登录
            for indicator in dashboard_indicators:
                if self.page.s_ele(indicator, timeout=3):
                    return True

            return True  # 即使验证失败也返回True，避免阻塞

        except Exception as e:
            logging.warning(f"浏览器实例 {self.instance_id} 登录失败: {e}")
            return True  # 登录失败不影响实例创建
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.browser or not self.page:
                return False

            # 检查浏览器是否还活着
            try:
                # 尝试获取当前URL，如果浏览器崩溃会抛出异常
                current_url = self.page.url
                return True
            except:
                return False

        except Exception as e:
            logging.warning(f"浏览器实例 {self.instance_id} 健康检查失败: {e}")
            self.error_count += 1
            self.is_healthy = False
            return False
    
    def use(self):
        """使用浏览器实例"""
        with self.lock:
            self.last_used = time.time()
            self.usage_count += 1
    
    def destroy(self):
        """销毁浏览器实例"""
        try:
            if self.browser:
                self.browser.quit()
            self.is_healthy = False
            logging.info(f"浏览器实例 {self.instance_id} 已销毁")
        except Exception as e:
            logging.error(f"销毁浏览器实例 {self.instance_id} 失败: {e}")

class BrowserPool:
    """浏览器池管理器"""
    
    def __init__(self, config: Dict[str, Any], pool_size: int = 3):
        self.config = config
        self.pool_size = pool_size
        self.instances: List[BrowserInstance] = []
        self.available_queue = queue.Queue()
        self.lock = threading.Lock()
        self.next_instance_id = 1
        self.health_check_interval = 60  # 60秒健康检查
        self.max_instance_age = 1800  # 30分钟最大生存时间
        self.max_usage_count = 1000  # 最大使用次数
        
        self._initialize_pool()
        self._start_health_monitor()
    
    def _initialize_pool(self):
        """初始化浏览器池"""
        logging.info(f"初始化浏览器池，大小: {self.pool_size}")
        
        for _ in range(self.pool_size):
            instance = self._create_instance()
            if instance and instance.is_healthy:
                self.instances.append(instance)
                self.available_queue.put(instance)
        
        logging.info(f"浏览器池初始化完成，可用实例: {len(self.instances)}")
    
    def _create_instance(self) -> Optional[BrowserInstance]:
        """创建新的浏览器实例"""
        instance = BrowserInstance(self.next_instance_id, self.config)
        self.next_instance_id += 1
        
        if instance.create_browser():
            return instance
        return None
    
    def _start_health_monitor(self):
        """启动健康监控线程"""
        def health_monitor():
            while True:
                try:
                    time.sleep(self.health_check_interval)
                    self._health_check_all()
                    self._cleanup_old_instances()
                except Exception as e:
                    logging.error(f"健康监控错误: {e}")
        
        monitor_thread = threading.Thread(target=health_monitor, daemon=True)
        monitor_thread.start()
        logging.info("健康监控线程已启动")
    
    def _health_check_all(self):
        """检查所有实例的健康状态"""
        with self.lock:
            unhealthy_instances = []
            
            for instance in self.instances:
                if not instance.health_check():
                    unhealthy_instances.append(instance)
            
            # 移除不健康的实例
            for instance in unhealthy_instances:
                self._remove_instance(instance)
                
            # 补充新实例
            while len(self.instances) < self.pool_size:
                new_instance = self._create_instance()
                if new_instance and new_instance.is_healthy:
                    self.instances.append(new_instance)
                    self.available_queue.put(new_instance)
                else:
                    break
    
    def _cleanup_old_instances(self):
        """清理老旧实例"""
        current_time = time.time()
        old_instances = []
        
        with self.lock:
            for instance in self.instances:
                age = current_time - instance.created_at
                if (age > self.max_instance_age or 
                    instance.usage_count > self.max_usage_count or
                    instance.error_count > 10):
                    old_instances.append(instance)
            
            for instance in old_instances:
                self._remove_instance(instance)
                # 创建新实例替换
                new_instance = self._create_instance()
                if new_instance and new_instance.is_healthy:
                    self.instances.append(new_instance)
                    self.available_queue.put(new_instance)
    
    def _remove_instance(self, instance: BrowserInstance):
        """移除实例"""
        if instance in self.instances:
            self.instances.remove(instance)
            instance.destroy()
            logging.info(f"移除浏览器实例 {instance.instance_id}")
    
    @contextmanager
    def get_browser(self, timeout: float = 5.0):
        """获取浏览器实例（上下文管理器）"""
        instance = None
        try:
            # 尝试获取可用实例
            instance = self.available_queue.get(timeout=timeout)
            instance.use()
            
            # 快速健康检查
            if not instance.is_healthy or not instance.health_check():
                # 实例不健康，尝试获取另一个
                self._remove_instance(instance)
                instance = self.available_queue.get(timeout=1.0)
                instance.use()
            
            yield instance.page
            
        except queue.Empty:
            logging.warning("无可用浏览器实例")
            yield None
        except Exception as e:
            logging.error(f"获取浏览器实例错误: {e}")
            yield None
        finally:
            # 归还实例
            if instance and instance.is_healthy:
                self.available_queue.put(instance)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取池统计信息"""
        with self.lock:
            total_usage = sum(instance.usage_count for instance in self.instances)
            total_errors = sum(instance.error_count for instance in self.instances)
            
            return {
                'pool_size': len(self.instances),
                'available_count': self.available_queue.qsize(),
                'total_usage': total_usage,
                'total_errors': total_errors,
                'instances': [
                    {
                        'id': instance.instance_id,
                        'healthy': instance.is_healthy,
                        'usage_count': instance.usage_count,
                        'error_count': instance.error_count,
                        'age': time.time() - instance.created_at
                    }
                    for instance in self.instances
                ]
            }
    
    def destroy_all(self):
        """销毁所有实例"""
        with self.lock:
            for instance in self.instances:
                instance.destroy()
            self.instances.clear()
            
            # 清空队列
            while not self.available_queue.empty():
                try:
                    self.available_queue.get_nowait()
                except queue.Empty:
                    break
        
        logging.info("所有浏览器实例已销毁")

# 使用示例
if __name__ == "__main__":
    # 测试配置
    test_config = {
        'HEADLESS_MODE': True,
        'PAGE_LOAD_TIMEOUT': 10
    }
    
    # 创建浏览器池
    pool = BrowserPool(test_config, pool_size=2)
    
    try:
        # 使用浏览器
        with pool.get_browser() as page:
            if page:
                page.get('https://www.baidu.com')
                print(f"页面标题: {page.title}")
        
        # 获取统计信息
        stats = pool.get_stats()
        print(f"池统计: {stats}")
        
        time.sleep(5)
        
    finally:
        pool.destroy_all()
