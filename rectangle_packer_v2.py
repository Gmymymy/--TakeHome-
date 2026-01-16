import json
import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangle:
    def __init__(self, center, length, width, angle=0):
        self.center = center
        self.length = length
        self.width = width
        self.angle = angle  # 0 or 90 degrees
        self.is_rotated = angle == 90
        self.original_length = length
        self.original_width = width
        
        # 计算矩形的四个顶点
        self.update_vertices()
    
    def update_vertices(self):
        if self.is_rotated:
            half_w = self.original_length / 2
            half_h = self.original_width / 2
        else:
            half_w = self.original_width / 2
            half_h = self.original_length / 2
            
        x = self.center.x
        y = self.center.y
        
        self.vertices = [
            Point(x - half_w, y - half_h),
            Point(x + half_w, y - half_h),
            Point(x + half_w, y + half_h),
            Point(x - half_w, y + half_h)
        ]
    
    def rotate(self):
        self.is_rotated = not self.is_rotated
        self.angle = 90 if self.is_rotated else 0
        self.update_vertices()
    
    def get_dimensions(self):
        if self.is_rotated:
            return (self.original_length, self.original_width)
        return (self.original_width, self.original_length)

class Polygon:
    def __init__(self, points):
        self.points = [Point(x, y) for x, y in points]
    
    def is_point_inside(self, point):
        # 使用射线法判断点是否在多边形内
        inside = False
        n = len(self.points)
        
        for i in range(n):
            j = (i + 1) % n
            
            if ((self.points[i].y > point.y) != (self.points[j].y > point.y)) and \
               (point.x < (self.points[j].x - self.points[i].x) * (point.y - self.points[i].y) / \
                (self.points[j].y - self.points[i].y) + self.points[i].x):
                inside = not inside
                
        return inside
    
    def get_bounds(self):
        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)
        return (min_x, min_y, max_x, max_y)

class Door:
    def __init__(self, points, is_open_inward):
        # 确保points是列表格式
        if isinstance(points[0], (list, tuple)):
            self.points = [Point(x, y) for x, y in points]
        else:
            # 如果points是单个点对，转换为列表
            self.points = [Point(points[0], points[1]), Point(points[2], points[3])]
        
        self.is_open_inward = is_open_inward
        
        # 计算门的宽度
        if abs(self.points[0].x - self.points[1].x) < 1e-6:
            # 垂直门
            self.width = abs(self.points[0].y - self.points[1].y)
        else:
            # 水平门
            self.width = abs(self.points[0].x - self.points[1].x)
    
    def get_obstruction_area(self, polygon):
        # 如果是内开门，计算门打开时占据的区域
        if not self.is_open_inward:
            return []
        
        # 计算门的中心点和方向
        center_x = (self.points[0].x + self.points[1].x) / 2
        center_y = (self.points[0].y + self.points[1].y) / 2
        
        # 确定门的方向（水平或垂直）
        is_vertical = abs(self.points[0].x - self.points[1].x) < 1e-6
        
        # 计算门打开时占据的N x N区域
        N = self.width
        
        if is_vertical:
            # 垂直门
            test_point = Point(center_x + N/2, center_y)
            if polygon.is_point_inside(test_point):
                # 门向右开
                return [
                    Point(center_x, center_y - N/2),
                    Point(center_x + N, center_y - N/2),
                    Point(center_x + N, center_y + N/2),
                    Point(center_x, center_y + N/2)
                ]
            else:
                # 门向左开
                return [
                    Point(center_x - N, center_y - N/2),
                    Point(center_x, center_y - N/2),
                    Point(center_x, center_y + N/2),
                    Point(center_x - N, center_y + N/2)
                ]
        else:
            # 水平门
            test_point = Point(center_x, center_y + N/2)
            if polygon.is_point_inside(test_point):
                # 门向上开
                return [
                    Point(center_x - N/2, center_y),
                    Point(center_x + N/2, center_y),
                    Point(center_x + N/2, center_y + N),
                    Point(center_x - N/2, center_y + N)
                ]
            else:
                # 门向下开
                return [
                    Point(center_x - N/2, center_y - N),
                    Point(center_x + N/2, center_y - N),
                    Point(center_x + N/2, center_y),
                    Point(center_x - N/2, center_y)
                ]

class RectanglePacker:
    def __init__(self, boundary, door_points, items):
        self.polygon = Polygon(boundary)
        # 默认is_open_inward为False，后续将通过set_door_open_inward方法设置
        self.door = Door(door_points, False)
        self.items = items
        self.placed_rectangles = []
        self.item_map = {}  # 存储物品名称和矩形的对应关系
    
    def set_door_open_inward(self, is_open_inward):
        self.door.is_open_inward = is_open_inward
        
        # 计算多边形的边界框
        self.bounds = self.polygon.get_bounds()
        
        # 获取门的阻碍区域
        self.door_obstruction = self.door.get_obstruction_area(self.polygon)
    
    def is_rectangle_valid(self, rectangle):
        # 检查矩形是否在多边形内且不与其他矩形重叠
        
        # 检查矩形的所有顶点是否在多边形内
        for vertex in rectangle.vertices:
            if not self.polygon.is_point_inside(vertex):
                return False
        
        # 检查矩形是否与其他已放置的矩形重叠
        for placed in self.placed_rectangles:
            if self.is_overlap(rectangle, placed):
                return False
        
        # 检查矩形是否与门的阻碍区域重叠
        if self.door_obstruction:
            door_poly = Polygon([(p.x, p.y) for p in self.door_obstruction])
            for vertex in rectangle.vertices:
                if door_poly.is_point_inside(vertex):
                    return False
        
        return True
    
    def is_overlap(self, rect1, rect2):
        # 检查两个矩形是否重叠
        def is_intersecting(a1, a2, b1, b2):
            return max(a1, b1) < min(a2, b2)
        
        # 获取两个矩形的边界
        r1_min_x = min(v.x for v in rect1.vertices)
        r1_max_x = max(v.x for v in rect1.vertices)
        r1_min_y = min(v.y for v in rect1.vertices)
        r1_max_y = max(v.y for v in rect1.vertices)
        
        r2_min_x = min(v.x for v in rect2.vertices)
        r2_max_x = max(v.x for v in rect2.vertices)
        r2_min_y = min(v.y for v in rect2.vertices)
        r2_max_y = max(v.y for v in rect2.vertices)
        
        # 检查x和y方向是否都有重叠
        return is_intersecting(r1_min_x, r1_max_x, r2_min_x, r2_max_x) and \
               is_intersecting(r1_min_y, r1_max_y, r2_min_y, r2_max_y)
    
    def get_wall_edges(self):
        # 获取多边形的所有边
        edges = []
        n = len(self.polygon.points)
        
        for i in range(n):
            j = (i + 1) % n
            p1 = self.polygon.points[i]
            p2 = self.polygon.points[j]
            edges.append((p1, p2))
        
        return edges
    
    def find_wall_positions(self, item_name, dimensions):
        # 查找沿墙的可能位置
        edges = self.get_wall_edges()
        positions = []
        
        for edge in edges:
            p1, p2 = edge
            
            # 确定边的方向
            is_horizontal = abs(p1.y - p2.y) < 1e-6
            
            if is_horizontal:
                # 水平边
                length = abs(p1.x - p2.x)
                height = dimensions[1]
                
                if length < dimensions[0]:
                    continue
                    
                # 沿水平边放置
                start_x = min(p1.x, p2.x)
                end_x = max(p1.x, p2.x)
                y = p1.y
                
                # 确定放置在边的上方还是下方
                test_point = Point((start_x + end_x) / 2, y + 10)
                if self.polygon.is_point_inside(test_point):
                    # 边在下方，矩形放在上方
                    y += height / 2
                else:
                    # 边在上方，矩形放在下方
                    y -= height / 2
                
                # 沿边滑动，寻找所有可能的位置
                step = 10  # 步长
                for x in range(int(start_x), int(end_x - dimensions[0]), step):
                    center = Point(x + dimensions[0] / 2, y)
                    rect = Rectangle(center, dimensions[1], dimensions[0])
                    if self.is_rectangle_valid(rect):
                        positions.append((rect, edge))
                        
            else:
                # 垂直边
                length = abs(p1.y - p2.y)
                width = dimensions[0]
                
                if length < dimensions[1]:
                    continue
                    
                # 沿垂直边放置
                start_y = min(p1.y, p2.y)
                end_y = max(p1.y, p2.y)
                x = p1.x
                
                # 确定放置在边的左侧还是右侧
                test_point = Point(x + 10, (start_y + end_y) / 2)
                if self.polygon.is_point_inside(test_point):
                    # 边在左侧，矩形放在右侧
                    x += width / 2
                else:
                    # 边在右侧，矩形放在左侧
                    x -= width / 2
                
                # 沿边滑动，寻找所有可能的位置
                step = 10  # 步长
                for y in range(int(start_y), int(end_y - dimensions[1]), step):
                    center = Point(x, y + dimensions[1] / 2)
                    rect = Rectangle(center, dimensions[1], dimensions[0])
                    if self.is_rectangle_valid(rect):
                        positions.append((rect, edge))
        
        return positions
    
    def find_internal_positions(self, item_name, dimensions):
        # 查找内部的可能位置
        positions = []
        
        # 获取多边形的边界框
        min_x, min_y, max_x, max_y = self.bounds
        
        # 获取矩形尺寸
        width, length = dimensions
        
        # 在内部生成网格点
        step = 50  # 步长可以调整
        for x in range(int(min_x + width/2), int(max_x - width/2), step):
            for y in range(int(min_y + length/2), int(max_y - length/2), step):
                center = Point(x, y)
                rect = Rectangle(center, length, width)
                
                # 检查矩形是否有效
                if self.is_rectangle_valid(rect):
                    positions.append((rect, None))
        
        return positions
    
    def is_fridge_door_clear(self, fridge_rect):
        # 检查冰箱开门边是否有其他物品
        # 假设开门边是length方向（较长的一边）
        width, length = fridge_rect.get_dimensions()
        
        # 确定开门边的方向
        # 冰箱开门边通常是较长的一边，这里假设是length方向
        center = fridge_rect.center
        
        # 计算开门边周围的区域
        door_margin = 50  # 开门边需要的额外空间
        
        # 创建一个代表开门边影响区域的矩形
        # 假设开门边在右侧
        door_center = Point(center.x + length/2 + door_margin, center.y)
        door_rect = Rectangle(door_center, length, door_margin * 2)
        
        # 检查是否与其他物品重叠
        for placed in self.placed_rectangles:
            if self.is_overlap(door_rect, placed):
                return False
        
        return True
    
    def select_best_rotation(self, item_name, dimensions):
        # 尝试两种旋转方向，选择可用位置更多的方向
        original_dim = dimensions
        rotated_dim = (dimensions[1], dimensions[0])
        
        # 计算两种旋转方向的可用沿墙位置数量
        original_wall_positions = self.find_wall_positions(item_name, original_dim)
        rotated_wall_positions = self.find_wall_positions(item_name, rotated_dim)
        
        # 优先选择沿墙位置更多的旋转方向
        if len(original_wall_positions) >= len(rotated_wall_positions):
            return original_dim, False
        else:
            return rotated_dim, True
    
    def pack_rectangles(self):
        # 按照物品尺寸排序，先放置大的物品
        sorted_items = sorted(self.items.items(), key=lambda x: x[1][0] * x[1][1], reverse=True)
        
        for item_name, dimensions in sorted_items:
            placed = False
            
            # 优先尝试沿墙放置
            # 选择最佳旋转方向
            best_dim, is_rotated = self.select_best_rotation(item_name, dimensions)
            
            # 寻找沿墙位置
            wall_positions = self.find_wall_positions(item_name, best_dim)
            
            if wall_positions:
                # 选择第一个可用的沿墙位置
                best_rect, edge = wall_positions[0]
                if is_rotated:
                    best_rect.rotate()
                
                # 如果是冰箱，检查开门边
                if item_name == "fridge" and not self.is_fridge_door_clear(best_rect):
                    print(f"Warning: Could not place fridge {item_name} due to door clearance")
                else:
                    self.placed_rectangles.append(best_rect)
                    self.item_map[item_name] = best_rect
                    placed = True
                    print(f"Placed item {item_name} along wall")
            
            # 如果沿墙放置失败，尝试内部放置
            if not placed:
                # 尝试两种旋转方向
                for internal_rotation in [False, True]:
                    if internal_rotation:
                        internal_dim = (dimensions[1], dimensions[0])
                    else:
                        internal_dim = dimensions
                    
                    # 寻找内部位置
                    internal_positions = self.find_internal_positions(item_name, internal_dim)
                    
                    if internal_positions:
                        # 选择第一个可用的内部位置
                        best_rect, edge = internal_positions[0]
                        if internal_rotation:
                            best_rect.rotate()
                        
                        # 如果是冰箱，检查开门边
                        if item_name == "fridge" and not self.is_fridge_door_clear(best_rect):
                            print(f"Warning: Could not place fridge {item_name} in internal position due to door clearance")
                            continue
                        
                        self.placed_rectangles.append(best_rect)
                        self.item_map[item_name] = best_rect
                        placed = True
                        print(f"Placed item {item_name} in internal position")
                        break
            
            if not placed:
                print(f"Warning: Could not place item {item_name}")
        
        return len(self.placed_rectangles) == len(self.items)
    
    def get_result(self):
        result = {
            "feasible": len(self.placed_rectangles) == len(self.items),
            "placements": []
        }
        
        # 按照物品名称顺序输出结果
        for item_name in self.items.keys():
            if item_name in self.item_map:
                rect = self.item_map[item_name]
                placement = {
                    "center": (rect.center.x, rect.center.y),
                    "angle": rect.angle
                }
                result["placements"].append(placement)
        
        return result

def solve_packing(input_data):
    boundary = input_data["boundary"]
    door_points = input_data["door"]
    is_open_inward = input_data.get("isOpenInward", False)
    items = input_data["algoToPlace"]
    
    # 创建packer实例
    packer = RectanglePacker(boundary, door_points, items)
    packer.set_door_open_inward(is_open_inward)
    feasible = packer.pack_rectangles()
    
    return packer.get_result()

if __name__ == "__main__":
    # 测试示例
    import os
    
    for i in range(1, 5):
        input_file = f"example{i}.json"
        if os.path.exists(input_file):
            with open(input_file, "r") as f:
                input_data = json.load(f)
                
            print(f"\nProcessing Example {i}...")
            result = solve_packing(input_data)
            print(f"Example {i} result:")
            print(json.dumps(result, indent=2))
            print()
