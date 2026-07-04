# Agnes AI Multimodal 技能更新报告

**日期**: 2026-06-15/16  
**触发**: 游乐园视频制作项目（6场景 · 30秒 · TTS配音 · 背景音乐 · 中文字幕）

---

## 一、变更总览

| # | 文件 | 操作 | 说明 |
|---|------|------|------|
| 1 | `SKILL.md` | ✅ 更新 | 新增 6 条 Pitfalls，增加儿童语音 TTS 替代方案 |
| 2 | `scripts/agnes_video_gen.py` | ✅ 修复 | URL 检查顺序修复（`remixed_from_video_id` 优先） |
| 3 | `~/agnes_video_gen.py` | ✅ 同步 | 用户工作副本同步修复 |
| 4 | `references/tts-narration-pipeline.md` | ❌ 删除 | 内容已合并到 `end-to-end-video-pipeline.md` |
| 5 | `references/video-production-pipeline.md` | ❌ 删除 | 同上 |
| 6 | `references/end-to-end-video-pipeline.md` | ✅ 重写 | 合并后成为规范参考，新增常见失败排查表 |

---

## 二、详细变更说明

### 2.1 SKILL.md Pitfalls 增强

**新增 6 条关键注意事项（编号 8-13）：**

| # | 标题 | 说明 |
|---|------|------|
| 8 | `write_file` 在挂载目录中失败 | `video_cache` 目录写文件需用 `cat >` 代替 |
| 9 | TTS 配音片段时间短于场景时长 | 必须用 `apad`+`atrim` 补齐后再拼接 |
| 10 | 多场景提示词一致性 | 共享视觉描述 + 极其具体的元素描述 |
| 11 | 视频 API 间歇性连接问题 | Cloudflare CDN 问题，2-3 分钟后重试 |
| 12 | 中文文字无法在视频中渲染 | 低模问题，必须后期加字幕 |
| 13 | OpenAI TTS 无法产生儿童声音 | 指引到 Fish Audio / MiniMax 替代方案 |

**原文更新：** 编号 3 的 API Key 方案增加 hex 编码方案（运行时读取 `.env` 和 `write_file` 场景分别说明）。

### 2.2 `agnes_video_gen.py` 脚本修复

**问题：** API 响应中 `remixed_from_video_id` 字段被放在 `video_url` 之后检查，但实际该字段才是优先返回的下载 URL。

**修复前：**
```python
for key in ["video_url", "url", "video", ..., "remixed_from_video_id"]:
```

**修复后：**
```python
for key in ["remixed_from_video_id", "video_url", "url", "video", ...]:
```

同时修复 `~/agnes_video_gen.py` 用户工作副本的变量名 bug（`if k in data` 中 `k` 未定义 → `key`）。

### 2.3 参考文件整理

删除 2 个被 `end-to-end-video-pipeline.md` 完全覆盖的旧参考文件：
- `tts-narration-pipeline.md`
- `video-production-pipeline.md`

并重写 `end-to-end-video-pipeline.md` 为规范参考文档，新增"常见失败"排查表。

---

## 三、核心经验总结（来自本次实践）

1. **Agnes Video** 每次生成慢（~130s），但结果可靠。用 `delegate_task` 并行跑多场景可大幅缩短总时间。
2. **TTS padding** 是必备步骤——直接拼接 unpadded 的 TTS 会导致最终视频时长被截断。
3. **场景视觉一致性** 是大模型视频生成的固有局限——同一场景分 6 次生成，风格/构图/光照会漂移。最可行的改进方向是：生成一张参考图 + 全场景用 `image` 模式。
4. **`write_file`** 在 `video_cache` 目录失败是挂载路径问题，改用 `terminal printf >` 搞定。
5. **儿童声音**：OpenAI TTS 无童声音色。Fish Audio 有现成模型 ID（稚嫩女童 `101a88bb..`），但需要注册账号。

---

## 四、GitHub 提交前检查清单

| 项目 | 状态 |
|------|------|
| SKILL.md 语法正确 | ✅ |
| `scripts/agnes_video_gen.py` 无语法/逻辑错误 | ✅ |
| `~/agnes_video_gen.py`（工作副本）已同步 | ✅ |
| 过期 reference 文件已删除 | ✅ |
| 合并后的 reference 内容完整 | ✅ |
| 删除的 ref 有明确取代者（不回引起悬挂引用） | ✅ |

- `~/agnes_video_gen.py` 已清除 hex 编码，改为纯环境变量读取
- `scripts/agnes_video_gen.py`（技能内）已有环境变量读取逻辑

---

## 五、后续待办（非本次范围）

- [ ] 注册 MiniMax 账号获取 TTS API Key，添加儿童音色示例
- [ ] 考虑添加 `scripts/tts_concat.py` 辅助脚本，自动完成 TTS padding + 拼接逻辑
- [ ] 评估是否需要在 SKILL.md 中增加一个完整的 "多场景视频制作" Quickstart 案例
