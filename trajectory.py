"""
生成拟人化的滑块轨迹
"""
import random
import math
from typing import List, Tuple


def generate_trajectory(distance: int) -> List[Tuple[int, int, int]]:
    """
    生成拟人化的滑动轨迹
    
    Args:
        distance: 需要滑动的距离(像素)
    
    Returns:
        [(x, y, t), ...]: 轨迹点列表 (x坐标, y坐标偏移, 时间戳ms)
    """
    trajectory = []
    current = 0
    mid = distance * 4 / 5  # 80%距离开始减速
    t = 0
    v = 0  # 初速度
    
    # 起始点
    trajectory.append((0, 0, 0))
    
    while current < distance:
        if current < mid:
            # 加速阶段：加速度2-5
            a = random.randint(2, 5)
        else:
            # 减速阶段：负加速度
            a = -random.randint(3, 5)
        
        # 更新速度 v = v0 + at
        v0 = v
        v = v0 + a
        v = max(v, 0.5)  # 保持最小速度
        
        # 位移 s = v0*t + 0.5*a*t^2
        move = v0 + 0.5 * a
        current += move
        
        # 限制不超过目标距离
        if current > distance:
            current = distance
        
        # 添加随机的y轴偏移（模拟手抖）
        y_offset = random.randint(-2, 2)
        
        # 时间增量（毫秒）
        t += random.randint(10, 25)
        
        trajectory.append((int(current), y_offset, t))
        
        # 到达目标位置
        if current >= distance:
            break
    
    return trajectory


def add_shake_at_end(trajectory: List[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    """
    在轨迹末尾添加抖动效果（模拟人类最后调整位置）
    
    Args:
        trajectory: 原始轨迹
        
    Returns:
        添加抖动后的轨迹
    """
    if not trajectory:
        return trajectory
    
    last_x, last_y, last_t = trajectory[-1]
    
    # 添加3-5次小幅抖动
    shake_count = random.randint(3, 5)
    for i in range(shake_count):
        # 小范围前后移动
        shake_x = last_x + random.randint(-3, 3)
        shake_y = last_y + random.randint(-1, 1)
        shake_t = last_t + random.randint(15, 35)
        
        trajectory.append((shake_x, shake_y, shake_t))
        last_t = shake_t
    
    # 最后稳定在目标位置
    trajectory.append((last_x, 0, last_t + random.randint(20, 40)))
    
    return trajectory


def add_bezier_curve(trajectory: List[Tuple[int, int, int]], smoothness: int = 3) -> List[Tuple[int, int, int]]:
    """
    使用贝塞尔曲线平滑轨迹（可选）
    
    Args:
        trajectory: 原始轨迹
        smoothness: 平滑程度（在每两个点之间插入的点数）
        
    Returns:
        平滑后的轨迹
    """
    if len(trajectory) < 2:
        return trajectory
    
    smooth_trajectory = [trajectory[0]]
    
    for i in range(len(trajectory) - 1):
        x1, y1, t1 = trajectory[i]
        x2, y2, t2 = trajectory[i + 1]
        
        # 在两点之间插入平滑点
        for j in range(1, smoothness + 1):
            ratio = j / (smoothness + 1)
            
            # 线性插值
            x = int(x1 + (x2 - x1) * ratio)
            y = int(y1 + (y2 - y1) * ratio)
            t = int(t1 + (t2 - t1) * ratio)
            
            smooth_trajectory.append((x, y, t))
        
        smooth_trajectory.append((x2, y2, t2))
    
    return smooth_trajectory


if __name__ == "__main__":
    # 测试轨迹生成
    distance = 187  # 假设缺口在187px
    
    print(f"生成移动距离: {distance}px")
    
    traj = generate_trajectory(distance)
    print(f"基础轨迹点数: {len(traj)}")
    
    traj = add_shake_at_end(traj)
    print(f"添加抖动后: {len(traj)}个点")
    
    # 打印前10个点
    print("\n前10个轨迹点:")
    for i, (x, y, t) in enumerate(traj[:10]):
        print(f"  {i+1}. x={x:3d}, y={y:+2d}, t={t:4d}ms")
    
    print(f"\n最后5个轨迹点:")
    for i, (x, y, t) in enumerate(traj[-5:], len(traj)-4):
        print(f"  {i}. x={x:3d}, y={y:+2d}, t={t:4d}ms")
