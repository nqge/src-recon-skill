# PATH_BRUTEFORCE_REPORT.md - 路径爆破功能说明

## 📖 功能说明

在阶段 7 添加路径拼接与未授权访问测试功能。

### 工作流程

1. 读取提取的路径列表（extracted_paths.txt）
2. 对每个 HTTP 服务进行路径拼接测试
3. 将路径拼接到站点的目录结构中
4. 并发测试所有拼接的 URL
5. 生成详细的测试报告

### 输出文件

- path_bruteforce_*.txt - 每个站点的测试报告
- path_bruteforce_combined.txt - 合并的所有测试结果

### 使用工具

path_bruteforcer.py - 路径爆破工具
