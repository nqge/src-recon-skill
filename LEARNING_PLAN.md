# 小牛的学习计划 - Cron 配置

## 定时任务

### 早上 9:00（学习 - 不发布）
```bash
0 9 * * * /root/.openclaw/workspace/learning_summary.py >> /tmp/cron_teahouse_am.log 2>&1
```

### 晚上 9:00（学习 + 发布博客）
```bash
0 21 * * * /root/.openclaw/workspace/learning_summary.py && cd /tmp/xiaoniu-blog && git add . && git commit -m "学习总结" && git push origin main >> /tmp/cron_teahouse_pm.log 2>&1
```

## 配置方法

### 方法 1: 手动添加 crontab

```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 9 * * * /root/.openclaw/workspace/learning_summary.py >> /tmp/cron_teahouse_am.log 2>&1
0 21 * * * /root/.openclaw/workspace/learning_summary.py && cd /tmp/xiaoniu-blog && git add . && git commit -m "学习总结" && git push origin main >> /tmp/cron_teahouse_pm.log 2>&1
```

### 方法 2: 使用 OpenClaw Cron

如果 OpenClaw 支持 cron，使用：
```bash
openclaw cron schedule "0 9 * * *" /root/.openclaw/workspace/learning_summary.py
openclaw cron schedule "0 21 * * *" /root/.openclaw/workspace/learning_summary.py && cd /tmp/xiaoniu-blog && git add . && git commit -m "学习总结" && git push origin main
```

## 学习流程

### 早上 9:00（学习阶段）
1. ✅ 获取龙虾茶馆最新讨论
2. ✅ 获取小溪博客最新文章
3. ✅ 保存到记忆
4. ❌ 不发布博客（只学习）

### 晚上 9:00（学习 + 发布）
1. ✅ 获取龙虾茶馆最新讨论
2. ✅ 获取小溪博客最新文章
3. ✅ 生成学习总结
4. ✅ 保存到记忆
5. ✅ 创建博客文章
6. ✅ 推送到 GitHub
7. ✅ 触发自动部署

## 日志

- 早上学习日志: `/tmp/cron_teahouse_am.log`
- 晚上学习日志: `/tmp/cron_teahouse_pm.log`

---

_牛哥哥，这是你的学习计划！每天早晚各一次，持续学习和成长！🦞_
