# CONCURRENCY_SETTINGS.md - 并发配置

## 📊 并发设置

所有工具的并发线程数已调整为 **15**，以避免：
- 触发站点 WAF 封禁
- 导致站点访问失败
- 被防火墙拦截
- 对目标造成过大压力

## 工具并发配置

| 工具 | 原并发 | �current | 说明 |
|------|--------|----------|------|
| **path_bruteforcer.py** | 30 | 15 | 路径爆破 |
| **js_path_extractor.py** | 30 | 15 | JS 路径提取 |
| **vuecrack.py** | 30 | 15 | Vue.js 检测 |
| **actuator_scanner.py** | 30 | 15 | Actuator 扫描 |
| **jsfind.py** | 30 | 15 | JS 文件分析 |
| **http_scanner.py** | 50 | 15 | HTTP 扫描 |
| **httpx (在脚本中)** | 50 | 30 | HTTP 探测 |

## 调整原因

1. **避免 WAF 封禁** - 高并发容易触发 Web 应用防火墙
2. **降低失败率** - 减少超时和连接错误
3. **合法测试** - 对目标站点更友好
4. **稳定性优先** - 速度可以慢一点，但要稳定

## 如果需要调整

编辑对应工具的 `__init__` 方法：

```python
def __init__(self, timeout=10, max_workers=15):
    self.max_workers = max_workers  # 修改这个值
```

或者设置环境变量：

```bash
export MAX_WORKERS=20  # 工具会读取这个环境变量
```
