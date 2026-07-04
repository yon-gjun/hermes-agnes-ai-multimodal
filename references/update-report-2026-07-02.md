# Agnes AI Multimodal 技能 — GitHub 上传准备报告

**日期**: 2026-07-02
**测试项目**: 《运动会报名这件"小事"》5镜头短视频 (29秒)

---

## ✅ 准备工作状态

| 项目 | 状态 | 备注 |
|------|------|------|
| SKILL.md 内容 | ✅ 已更新 | 19 条 Pitfalls 全部涵盖这次测试的问题 |
| README.md | ✅ 已同步 | 与 SKILL.md 内容一致 |
| 无硬编码 API Key | ✅ 通过 | 所有文件无 `sk-` 或 `KEY_HEX` 值（仅作为示例） |
| 工作副本脚本 | ✅ 已清理 | `~/agnes_video_gen.py` 使用环境变量，`gen_clips.py` 已删除 |
| 重复 reference 文件 | ✅ 已清理 | `tts-narration-pipeline.md`、`video-production-pipeline.md` 已删除 |
| 测试产物 | ✅ 已清理 | `gen_clips.py`（含 hex Key）已删除 |
| `.env` 尾部内容污染 | ✅ 已记录 | Pitfall #18 说明原始字节精确提取法 |

---

## 本次测试新增内容

本次测试（运动会报名5镜头）新增以下经验，全部已在 SKILL.md 中补充：

| # | 内容 | 位置 |
|---|------|------|
| 14 | 镜头时长按旁白时长匹配 | Pitfall #14 |
| 15 | 镜头间交叉淡入淡出 | Pitfall #15 |
| 16 | 通过参考图保证角色一致性 | Pitfall #16 + #10 |
| 17 | 轮询同时检查 `state` 和 `status` | Pitfall #17 |
| 18 | `.env` Key 精确提取（原始字节） | Pitfall #18 |
| 19 | 工作副本只有 text 模式 | Pitfall #19 |
| — | 独立图生视频脚本模式 | `references/image-to-video-standalone.md` |

---

## 文件结构（27 个文件，无 Key 泄露）

```
agnes-ai-multimodal/
├── SKILL.md                          # 主技能文档（中英双语）
├── README.md                         # README
├── README.html                       # HTML 格式 README
├── assets/
│   └── icon.svg                      # 技能图标
├── scripts/
│   ├── agnes_image_gen.py            # 图片生成脚本
│   ├── agnes_video_gen.py            # 视频生成脚本（完整版，含 image 模式）
│   ├── agnes_watch*.py               # 监控脚本
│   └── frame_calc.py                 # 帧数计算器
├── references/ (13 个)
│   ├── end-to-end-video-pipeline.md  # 完整视频制作管线
│   ├── image-to-video-standalone.md  # 独立图生视频脚本（hex Key）
│   ├── fish-audio-child-voice.md     # Fish Audio 童声
│   ├── minimax-tts-child-voices.md   # MiniMax 童声
│   ├── chinese-text-rendering-limitation.md
│   ├── astrix-corruption-bug.md
│   ├── download-troubleshooting.md
│   ├── video-api-connectivity.md
│   ├── audio-generation-patterns.md
│   ├── openmontage-agnes-workflow.md
│   ├── test-procedure.md
│   ├── test-report-june27.md
│   └── update-report-2026-06-16.md
└── templates/
    └── agnes_img2img.py              # 图生图模板
```

---

## ⚠️ GitHub 上传注意事项

| 项目 | 说明 |
|------|------|
| **远程仓库** | 需要先创建 GitHub 仓库，执行 `git init && git add . && git commit -m "..." && git remote add origin <URL> && git push` |
| **网络问题** | 本机可能无法直接 git push（之前有 DNS 问题），需在 PowerShell 终端手动操作 |
| **推送方法** | 复制到有网络的环境推送，或用 SSH 方式（密钥已配置） |
| **API Key 检查** | 已在所有文件中确认无硬编码 Key。注意 `references/image-to-video-standalone.md` 中有 `KEY_HEX` 示例值（`736b2d...`），那只是占位示例，不是真实 Key |
