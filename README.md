# nanyang-Prism-Max-H1.7

**全新生成底座 · 图片 / 视频本地真实生成**

---

nanyang-Prism-Max-H1.7 是南阳系列中专攻 **图像 / 视频生成** 的独立产品，与「南阳 GPT」对话模型彻底分离：各自独立仓库、独立维护。

版本路线说明：
- **Helios 1.2 / 1.5 已停止使用**，仅保留自研代码供查看，不再提供模型拉取/下载链接。
- **自研生成路线已放弃**，新版本切换到全新建设路线：直接在项目内嵌入成熟的开源大模型代码，本地 GPU 即可跑，不再出现色块问题。
- 当前主推 **Prism H1.7**，接入图形化大型生成底座，持续往上迭代。

## 能力一览

| 引擎 | 模态 | 是否需联网 | 模型来源 |
|------|------|-----------|---------|
| SDXL Turbo | 图片 | ❌ 纯本地 | stabilityai/sdxl-turbo（~4GB，首跑自动下载） |
| AnimateDiff | 视频 | ❌ 纯本地 | cerspense/zeroscope_v2_576w + motion LoRA（~8GB，首跑自动下载） |
| MiniMax H3 | 图片 / 视频 | ✅ 需要 API Key | MiniMax 官方服务（可选备用通道） |

## 快速开始 —— 纯本地模式（推荐）

无需任何 API Key，装完依赖后直接出图出视频，权重要自己下（约 4–8 GB）。

```bash
git clone https://github.com/Yang1235744/nanyang-Prism-Max-H1.7.git
cd nanyang-Prism-Max-H1.7
pip install -r requirements.txt

# 一键初始化所有本地引擎（自动从 HuggingFace 下载权重）
python scripts/download_weights.py --engine sdxl
python scripts/download_weights.py --engine animatediff

# --- 出图（SDXL Turbo，4 步即可，质量高速度快）---
python scripts/generate.py --engine sdxl \
    --prompt "雪地里的红狐 高清摄影" --t image --size 1024 1024

# --- 出视频（AnimateDiff，15 秒带音频）---
python scripts/generate.py --engine animatediff \
    --prompt "海浪拍打礁石 慢镜头" --t video --duration 15 --fps 12
```

生成结果保存在 `~/.cache/nanyang-prism/{sdxl-cache,animatediff-cache}/`。

## 备用通道 —— MiniMax H3（可选）

如果你配置了 MiniMax API Key，也可以走这条通道：

```bash
export MINIMAX_API_KEY="sk-api-YBHaqZGNzc..."
export MINIMAX_API_BASE="https://minimax.api.easyframe.cn/api/v3"

python scripts/generate.py --engine minimax-h3 \
    --prompt "赛博朋克城市夜景 霓虹灯" --t image
```

## 统一接口

所有引擎实现同一个 `BaseAdapter` 抽象类，代码可无缝切换：

```python
from prism.adapters import get_engine

# SDXL 出图
client = get_engine('sdxl')
out_img = client.generate_image("一只在雪地里奔跑的红狐", size=(1024, 1024))
print(f'图片：{out_img}')

# AnimateDiff 出视频
client = get_engine('animatediff')
out_vid = client.generate_video("海浪拍打礁石", duration=15, fps=12, audio=True)
print(f'视频：{out_vid}')
```

## 架构

```
用户 Prompt → nanyang-GPT（对话层）→ 工具标记 <|gen_image|> <|gen_video|>
                                              ↓
                                   Prism Max H1.7
                                     （本地推理层）
                         ┌──────────────────┼──────────────────┐
                   SDXL Turbo          AnimateDiff         MiniMax H3
               （本地 ~4GB 权重）   （本地 ~8GB 权重）     （可选 API 备用）
                 真图 1024px          真视频 15s           真图/真视频
```

- **对话与生成彻底分离**：nanyang-GPT 只做聊天；Prism Max H1.7 只做生成
- **全部离线可运行**：SDXL + AnimateDiff 不需要任何外部 API，权重要自己下（只下一次）
- **统一接口**：所有引擎实现 `BaseAdapter`，可插拔扩展
- **与 Helios 自研路线的关系**：原来自研 VAE/DiT 方案已废弃，改用成熟开源大模型作为本地生成底座

## 路线图

- [x] v1.7.0a0 — 骨架发布 · BaseAdapter 统一接口
- [x] v1.7.1 — SDXL Turbo + AnimateDiff 本地真生成完整实现
- [ ] v1.7.2 — Flux / SDXL 双通道优化、更多引擎接入
- [ ] v1.8 — 口型同步，剧情对白
- [ ] v1.9 — 批量生产流水线

## 许可

MIT © nanyang 2026
