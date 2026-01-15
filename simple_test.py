# 简单测试脚本

import json
from rectangle_packer import solve_packing

# 创建一个简单的测试用例
test_input = {
    "boundary": [
        [0, 0], [1000, 0], [1000, 1000], [0, 1000], [0, 0]
    ],
    "door": [[0, 400], [0, 600]],
    "isOpenInward": False,
    "algoToPlace": {
        "fridge": [1220, 1330],  # 注意：这个尺寸比边界大，应该无法放置
        "shelf-1": [400, 200]    # 这个应该可以放置
    }
}

# 运行测试
try:
    result = solve_packing(test_input)
    print("测试结果:")
    print(json.dumps(result, indent=2))
    print("测试成功!")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()