"""
TimePinner 测试
"""

import unittest
import time
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.TimePinner import Pinner, create_pinner


class TestTimePinner(unittest.TestCase):
    """TimePinner 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.pinner = Pinner()
    
    def test_create_pinner(self):
        """测试创建pinner"""
        pinner = create_pinner()
        self.assertIsInstance(pinner, Pinner)
    
    def test_pin_basic(self):
        """测试基本pin功能"""
        # 第一个pin应该返回0
        interval = self.pinner.pin("开始")
        self.assertEqual(interval, 0.0)
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 第二个pin应该返回大于0的时间间隔
        interval = self.pinner.pin("步骤1")
        self.assertGreater(interval, 0.0)
        self.assertLess(interval, 1.0)  # 应该小于1秒
    
    def test_get_pin_time(self):
        """测试获取pin时间"""
        self.pinner.pin("测试")
        time.sleep(0.05)
        self.pinner.pin("测试2")
        
        # 获取第一个pin的时间（应该是0）
        time1 = self.pinner.get_pin_time("测试")
        self.assertEqual(time1, 0.0)
        
        # 获取第二个pin的时间
        time2 = self.pinner.get_pin_time("测试2")
        self.assertGreater(time2, 0.0)
        
        # 获取不存在的pin
        time3 = self.pinner.get_pin_time("不存在")
        self.assertIsNone(time3)
    
    def test_get_total_time(self):
        """测试获取总时间"""
        # 初始状态总时间应该是0
        self.assertEqual(self.pinner.get_total_time(), 0.0)
        
        # 添加一个pin后
        self.pinner.pin("开始")
        time.sleep(0.1)
        
        total_time = self.pinner.get_total_time()
        self.assertGreater(total_time, 0.0)
        self.assertLess(total_time, 1.0)
    
    def test_reset(self):
        """测试重置功能"""
        self.pinner.pin("测试")
        time.sleep(0.05)
        self.pinner.pin("测试2")
        
        # 重置前应该有数据
        self.assertGreater(len(self.pinner.pins), 0)
        self.assertIsNotNone(self.pinner.start_time)
        
        # 重置
        self.pinner.reset()
        
        # 重置后应该清空
        self.assertEqual(len(self.pinner.pins), 0)
        self.assertIsNone(self.pinner.start_time)
        self.assertIsNone(self.pinner.last_pin_time)
        self.assertEqual(self.pinner.get_total_time(), 0.0)
    
    def test_summary(self):
        """测试摘要功能"""
        # 无数据时的摘要
        summary = self.pinner.summary()
        self.assertEqual(summary, "无时间记录")
        
        # 有数据时的摘要
        self.pinner.pin("开始")
        time.sleep(0.05)
        self.pinner.pin("结束")
        
        summary = self.pinner.summary()
        self.assertIn("时间摘要:", summary)
        self.assertIn("开始:", summary)
        self.assertIn("结束:", summary)
        self.assertIn("总时间:", summary)


if __name__ == '__main__':
    unittest.main()
