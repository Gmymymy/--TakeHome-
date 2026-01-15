# C++ 版本矩形摆放程序说明

## 概述
这是一个C++版本的矩形物体在多边形轮廓内摆放的程序，实现了与Python版本相同的功能。

## 文件说明
- `rectangle_packer.cpp`: C++版本的核心实现文件

## 编译环境要求
- C++11 或更高版本的编译器
- 支持标准C++库

## 编译命令
### Windows (使用MinGW)
```bash
g++ -std=c++11 rectangle_packer.cpp -o rectangle_packer.exe
```

### Windows (使用Visual Studio)
1. 打开Visual Studio Command Prompt
2. 运行以下命令：
```cmd
cl /EHsc /std:c++11 rectangle_packer.cpp
```

### Linux/macOS
```bash
g++ -std=c++11 rectangle_packer.cpp -o rectangle_packer
```

## 运行程序
编译成功后，运行生成的可执行文件：

### Windows
```bash
rectangle_packer.exe
```

### Linux/macOS
```bash
./rectangle_packer
```

## 功能说明
程序实现了以下功能：
1. 点(Point)和矩形(Rectangle)的几何建模
2. 多边形(Polygon)的表示和点在多边形内的判断
3. 门(Door)的表示和内开门阻碍区域计算
4. 矩形物体在多边形内的贴墙放置算法
5. 支持矩形旋转

## 测试用例
程序中包含一个简单的测试用例，创建了一个1000x1000的正方形房间，一个位于左侧的门，以及两个物品（一个过大的冰箱和一个可以放置的架子）。

## 扩展建议
1. 集成成熟的JSON库（如nlohmann/json）来支持JSON输入输出
2. 添加更完整的错误处理和日志输出
3. 实现更高效的碰撞检测算法
4. 添加可视化功能来展示摆放结果

## 注意事项
- 目前的JSON解析功能是简化版本，实际应用中建议使用成熟的JSON库
- 程序可能需要根据具体的输入格式进行调整
- 对于复杂的多边形轮廓，可能需要优化算法以提高性能