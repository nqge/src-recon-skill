SRC 众测信息收集技能包 - 贡献指南
=================================

感谢你对 src-recon-skill 的关注！

## 如何贡献

### 报告问题

请在 GitHub Issues 中报告问题，包括：
- 问题描述
- 复现步骤
- 错误日志
- 环境信息（OS、Python 版本）

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- Python 代码遵循 PEP 8
- 添加必要的注释和文档
- 更新相关文档

### 新增工具

如果要新增工具，请：
1. 在 `tools/` 目录下创建工具脚本
2. 添加使用文档到 `docs/`
3. 在 `src-recon-auto.sh` 中集成
4. 更新 `SKILL.md`

## 许可证

提交代码即表示你同意将代码以 MIT 许可证发布。
