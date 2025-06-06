"""
TimePinner - 简单的时间测量工具
用于测量代码执行时间
"""

import time
from typing import Dict, Optional


class Pinner:
    """时间测量器"""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.pins: Dict[str, float] = {}
        self.last_pin_time: Optional[float] = None
    
    def pin(self, label: str) -> float:
        """
        记录一个时间点
        
        Args:
            label: 时间点标签
            
        Returns:
            从上一个pin到当前pin的时间间隔（秒）
        """
        current_time = time.time()
        
        if self.start_time is None:
            self.start_time = current_time
            self.last_pin_time = current_time
            interval = 0.0
        else:
            interval = current_time - self.last_pin_time
            self.last_pin_time = current_time
        
        self.pins[label] = interval
        
        # 打印时间间隔
        print(f"{label}：{interval}")
        
        return interval
    
    def get_total_time(self) -> float:
        """获取总时间"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_pin_time(self, label: str) -> Optional[float]:
        """获取指定标签的时间间隔"""
        return self.pins.get(label)
    
    def reset(self):
        """重置计时器"""
        self.start_time = None
        self.pins.clear()
        self.last_pin_time = None
    
    def summary(self) -> str:
        """获取时间摘要"""
        if not self.pins:
            return "无时间记录"
        
        summary_lines = ["时间摘要:"]
        for label, interval in self.pins.items():
            summary_lines.append(f"  {label}: {interval:.4f}秒")
        
        total_time = self.get_total_time()
        summary_lines.append(f"  总时间: {total_time:.4f}秒")
        
        return "\n".join(summary_lines)


# 便捷函数
def create_pinner() -> Pinner:
    """创建一个新的时间测量器"""
    return Pinner()


# 示例用法
if __name__ == "__main__":
    pinner = Pinner()
    
    pinner.pin("开始")
    time.sleep(1)
    
    pinner.pin("步骤1完成")
    time.sleep(0.5)
    
    pinner.pin("步骤2完成")
    
    print("\n" + pinner.summary())
