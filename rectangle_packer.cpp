#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <cmath>
#include <algorithm>
#include <fstream>

// 定义点类
class Point {
public:
    double x, y;
    
    Point(double x = 0, double y = 0) : x(x), y(y) {}
    
    bool operator==(const Point& other) const {
        return std::abs(x - other.x) < 1e-6 && std::abs(y - other.y) < 1e-6;
    }
};

// 定义矩形类
class Rectangle {
public:
    Point center;
    double original_length;
    double original_width;
    bool is_rotated;
    std::vector<Point> vertices;
    
    Rectangle(Point center, double length, double width) 
        : center(center), original_length(length), original_width(width), is_rotated(false) {
        updateVertices();
    }
    
    void updateVertices() {
        double half_w, half_h;
        if (is_rotated) {
            half_w = original_length / 2;
            half_h = original_width / 2;
        } else {
            half_w = original_width / 2;
            half_h = original_length / 2;
        }
        
        vertices.clear();
        vertices.emplace_back(center.x - half_w, center.y - half_h);
        vertices.emplace_back(center.x + half_w, center.y - half_h);
        vertices.emplace_back(center.x + half_w, center.y + half_h);
        vertices.emplace_back(center.x - half_w, center.y + half_h);
    }
    
    void rotate() {
        is_rotated = !is_rotated;
        updateVertices();
    }
    
    std::pair<double, double> getDimensions() const {
        if (is_rotated) {
            return std::make_pair(original_length, original_width);
        }
        return std::make_pair(original_width, original_length);
    }
    
    int getAngle() const {
        return is_rotated ? 90 : 0;
    }
};

// 定义多边形类
class Polygon {
public:
    std::vector<Point> points;
    
    Polygon(const std::vector<Point>& points) : points(points) {}
    
    bool isPointInside(const Point& point) const {
        bool inside = false;
        size_t n = points.size();
        
        for (size_t i = 0; i < n; ++i) {
            size_t j = (i + 1) % n;
            
            if (((points[i].y > point.y) != (points[j].y > point.y)) &&
                (point.x < (points[j].x - points[i].x) * (point.y - points[i].y) /
                 (points[j].y - points[i].y) + points[i].x)) {
                inside = !inside;
            }
        }
        
        return inside;
    }
    
    std::tuple<double, double, double, double> getBounds() const {
        double min_x = points[0].x;
        double max_x = points[0].x;
        double min_y = points[0].y;
        double max_y = points[0].y;
        
        for (const auto& point : points) {
            min_x = std::min(min_x, point.x);
            max_x = std::max(max_x, point.x);
            min_y = std::min(min_y, point.y);
            max_y = std::max(max_y, point.y);
        }
        
        return std::make_tuple(min_x, min_y, max_x, max_y);
    }
};

// 定义门类
class Door {
public:
    std::vector<Point> points;
    bool is_open_inward;
    double width;
    
    Door(const std::vector<Point>& points, bool is_open_inward) 
        : points(points), is_open_inward(is_open_inward) {
        if (std::abs(points[0].x - points[1].x) < 1e-6) {
            // 垂直门
            width = std::abs(points[0].y - points[1].y);
        } else {
            // 水平门
            width = std::abs(points[0].x - points[1].x);
        }
    }
    
    std::vector<Point> getObstructionArea(const Polygon& polygon) const {
        if (!is_open_inward) {
            return {};
        }
        
        double center_x = (points[0].x + points[1].x) / 2;
        double center_y = (points[0].y + points[1].y) / 2;
        
        bool is_vertical = std::abs(points[0].x - points[1].x) < 1e-6;
        double N = width;
        
        if (is_vertical) {
            Point test_point(center_x + N / 2, center_y);
            if (polygon.isPointInside(test_point)) {
                // 门向右开
                return {
                    Point(center_x, center_y - N / 2),
                    Point(center_x + N, center_y - N / 2),
                    Point(center_x + N, center_y + N / 2),
                    Point(center_x, center_y + N / 2)
                };
            } else {
                // 门向左开
                return {
                    Point(center_x - N, center_y - N / 2),
                    Point(center_x, center_y - N / 2),
                    Point(center_x, center_y + N / 2),
                    Point(center_x - N, center_y + N / 2)
                };
            }
        } else {
            Point test_point(center_x, center_y + N / 2);
            if (polygon.isPointInside(test_point)) {
                // 门向上开
                return {
                    Point(center_x - N / 2, center_y),
                    Point(center_x + N / 2, center_y),
                    Point(center_x + N / 2, center_y + N),
                    Point(center_x - N / 2, center_y + N)
                };
            } else {
                // 门向下开
                return {
                    Point(center_x - N / 2, center_y - N),
                    Point(center_x + N / 2, center_y - N),
                    Point(center_x + N / 2, center_y),
                    Point(center_x - N / 2, center_y)
                };
            }
        }
    }
};

// 定义矩形放置器类
class RectanglePacker {
public:
    Polygon polygon;
    Door door;
    std::map<std::string, std::pair<double, double>> items;
    std::vector<Rectangle> placed_rectangles;
    std::tuple<double, double, double, double> bounds;
    std::vector<Point> door_obstruction;
    
    RectanglePacker(const Polygon& polygon, const Door& door, const std::map<std::string, std::pair<double, double>>& items)
        : polygon(polygon), door(door), items(items), bounds(polygon.getBounds()) {
        door_obstruction = door.getObstructionArea(polygon);
    }
    
    bool isRectangleValid(const Rectangle& rectangle) const {
        // 检查矩形的所有顶点是否在多边形内
        for (const auto& vertex : rectangle.vertices) {
            if (!polygon.isPointInside(vertex)) {
                return false;
            }
        }
        
        // 检查矩形是否与其他已放置的矩形重叠
        for (const auto& placed : placed_rectangles) {
            if (isOverlap(rectangle, placed)) {
                return false;
            }
        }
        
        // 检查矩形是否与门的阻碍区域重叠
        if (!door_obstruction.empty()) {
            Polygon door_poly(door_obstruction);
            for (const auto& vertex : rectangle.vertices) {
                if (door_poly.isPointInside(vertex)) {
                    return false;
                }
            }
        }
        
        return true;
    }
    
    bool isOverlap(const Rectangle& rect1, const Rectangle& rect2) const {
        auto getRectBounds = [](const Rectangle& rect) -> std::tuple<double, double, double, double> {
            double min_x = rect.vertices[0].x;
            double max_x = rect.vertices[0].x;
            double min_y = rect.vertices[0].y;
            double max_y = rect.vertices[0].y;
            
            for (const auto& vertex : rect.vertices) {
                min_x = std::min(min_x, vertex.x);
                max_x = std::max(max_x, vertex.x);
                min_y = std::min(min_y, vertex.y);
                max_y = std::max(max_y, vertex.y);
            }
            
            return std::make_tuple(min_x, min_y, max_x, max_y);
        };
        
        auto [r1_min_x, r1_min_y, r1_max_x, r1_max_y] = getRectBounds(rect1);
        auto [r2_min_x, r2_min_y, r2_max_x, r2_max_y] = getRectBounds(rect2);
        
        return !(r1_max_x < r2_min_x || r1_min_x > r2_max_x || r1_max_y < r2_min_y || r1_min_y > r2_max_y);
    }
    
    std::vector<std::pair<Point, Point>> getWallEdges() const {
        std::vector<std::pair<Point, Point>> edges;
        size_t n = polygon.points.size();
        
        for (size_t i = 0; i < n; ++i) {
            edges.emplace_back(polygon.points[i], polygon.points[(i + 1) % n]);
        }
        
        return edges;
    }
    
    std::vector<Rectangle> findWallPositions(const std::string& item_name, double width, double length) {
        std::vector<Rectangle> positions;
        auto edges = getWallEdges();
        
        for (const auto& edge : edges) {
            const Point& p1 = edge.first;
            const Point& p2 = edge.second;
            
            bool is_horizontal = std::abs(p1.y - p2.y) < 1e-6;
            
            if (is_horizontal) {
                double edge_length = std::abs(p1.x - p2.x);
                if (edge_length < width) {
                    continue;
                }
                
                double start_x = std::min(p1.x, p2.x);
                double end_x = std::max(p1.x, p2.x);
                double y = p1.y;
                
                Point test_point((start_x + end_x) / 2, y + 10);
                if (polygon.isPointInside(test_point)) {
                    y += length / 2;
                } else {
                    y -= length / 2;
                }
                
                double step = 10.0;
                for (double x = start_x; x <= end_x - width; x += step) {
                    Point center(x + width / 2, y);
                    Rectangle rect(center, length, width);
                    if (isRectangleValid(rect)) {
                        positions.push_back(rect);
                    }
                }
            } else {
                double edge_length = std::abs(p1.y - p2.y);
                if (edge_length < length) {
                    continue;
                }
                
                double start_y = std::min(p1.y, p2.y);
                double end_y = std::max(p1.y, p2.y);
                double x = p1.x;
                
                Point test_point(x + 10, (start_y + end_y) / 2);
                if (polygon.isPointInside(test_point)) {
                    x += width / 2;
                } else {
                    x -= width / 2;
                }
                
                double step = 10.0;
                for (double y = start_y; y <= end_y - length; y += step) {
                    Point center(x, y + length / 2);
                    Rectangle rect(center, length, width);
                    if (isRectangleValid(rect)) {
                        positions.push_back(rect);
                    }
                }
            }
        }
        
        return positions;
    }
    
    bool packRectangles() {
        // 按照物品尺寸排序，先放置大的物品
        std::vector<std::pair<std::string, std::pair<double, double>>> sorted_items(items.begin(), items.end());
        std::sort(sorted_items.begin(), sorted_items.end(), 
            [](const auto& a, const auto& b) {
                return a.second.first * a.second.second > b.second.first * b.second.second;
            });
        
        for (const auto& [item_name, dimensions] : sorted_items) {
            double length = dimensions.first;
            double width = dimensions.second;
            bool placed = false;
            
            // 尝试两种旋转方向
            for (int rotation = 0; rotation < 2; ++rotation) {
                double rect_width, rect_length;
                if (rotation == 0) {
                    rect_width = width;
                    rect_length = length;
                } else {
                    rect_width = length;
                    rect_length = width;
                }
                
                std::vector<Rectangle> positions = findWallPositions(item_name, rect_width, rect_length);
                
                if (!positions.empty()) {
                    Rectangle best_rect = positions[0];
                    if (rotation == 1) {
                        best_rect.rotate();
                    }
                    placed_rectangles.push_back(best_rect);
                    placed = true;
                    break;
                }
            }
            
            if (!placed) {
                std::cout << "Warning: Could not place item " << item_name << " along walls\n";
            }
        }
        
        return placed_rectangles.size() == items.size();
    }
    
    struct Result {
        bool feasible;
        std::vector<std::pair<Point, int>> placements;
    };
    
    Result getResult() const {
        Result result;
        result.feasible = placed_rectangles.size() == items.size();
        
        for (const auto& rect : placed_rectangles) {
            result.placements.emplace_back(rect.center, rect.getAngle());
        }
        
        return result;
    }
};

// 简单的JSON解析器（仅支持基本功能）
class SimpleJSONParser {
public:
    static std::map<std::string, std::string> parseJSON(const std::string& json_str) {
        // 这里实现一个简单的JSON解析器，仅支持基本的键值对
        // 实际应用中应该使用成熟的JSON库
        std::map<std::string, std::string> result;
        // 简化处理，实际需要更复杂的解析逻辑
        return result;
    }
};

// 主程序
int main() {
    // 创建一个简单的测试用例
    std::vector<Point> boundary_points = {
        Point(0, 0), Point(1000, 0), Point(1000, 1000), Point(0, 1000), Point(0, 0)
    };
    
    std::vector<Point> door_points = {Point(0, 400), Point(0, 600)};
    
    std::map<std::string, std::pair<double, double>> items = {
        {"fridge", {1220, 1330}},  // 注意：这个尺寸比边界大，应该无法放置
        {"shelf-1", {400, 200}}    // 这个应该可以放置
    };
    
    Polygon polygon(boundary_points);
    Door door(door_points, false);
    
    RectanglePacker packer(polygon, door, items);
    bool feasible = packer.packRectangles();
    
    auto result = packer.getResult();
    
    std::cout << "Feasible: " << (result.feasible ? "true" : "false") << std::endl;
    std::cout << "Placements:" << std::endl;
    
    for (size_t i = 0; i < result.placements.size(); ++i) {
        const auto& [center, angle] = result.placements[i];
        std::cout << "  Item " << i + 1 << ": Center = (" << center.x << ", " << center.y << "), Angle = " << angle << " degrees" << std::endl;
    }
    
    return 0;
}