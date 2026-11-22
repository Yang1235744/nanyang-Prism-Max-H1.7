# nanyang-Prism-Max-H1.7

**全新生成底座 · 本地离线 GPU 推理（图片 / 视频）**

---

nanyang-Prism-Max-H1.7 是南阳系列中专攻 **图像 / 视频生成** 的独立产品，与「南阳 GPT」对话模型彻底分离：各自独立仓库、独立维护。

版本路线说明：
- **Helios 1.2 / 1.5 已停止使用**，仅保留自研代码供查看，不再提供模型拉取/下载链接。
- **自研生成路线已放弃**，新版本直接嵌入成熟开源大模型代码，本地 GPU 就能真出图、真出视频，完全离线。
- 当前主推 **Prism H1.7**，接入图形化大型生成底座，持续往上迭代。

## 能力一览

| 引擎 | 模态 | 联网需求 | 首次权重下载 | 说明 |
|------|------|---------|------------|------|
| SDXL Turbo | 图片 | ❌ 纯本地 | ~4 GB | 高清出图，4 步推理 |
| AnimateDiff | 视频 | ❌ 纯本地 | ~8 GB | **最高 30 秒带音频真视频** |

## 快速开始

无需任何 API Key，装完依赖、等一次权重下载后完全离线运行。

```bash
git clone https://github.com/Yang1235744/nanyang-Prism-Max-H1.7.git
cd nanyang-Prism-Max-H1.7
pip install -r requirements.txt

# 首次运行会自动从 HuggingFace 下载权重（约 12 GB，只下一次）
python scripts/download_weights.py --engine sdxl
python scripts/download_weights.py --engine animatediff

# --- 出图 ---
python scripts/generate.py --engine sdxl \
    --prompt "雪地里的红狐 高清摄影" --t image

# --- 出 30 秒真视频 ---
python scripts/generate.py --engine animatediff \
    --prompt "海浪拍打礁石 慢镜头" --t video --duration 30
```

生成结果缓存在 `~/.cache/nanyang-prism/{sdxl-cache,animatediff-cache}/`，后续调用直接命中缓存。

## 服务器部署

把项目完整 clone 到服务器，确认有 CUDA + PyTorch 后即可直接运行：

```bash
# 服务器上一次性初始化权重
pip install -r requirements.txt
python scripts/download_weights.py --engine sdxl
python scripts/download_weights.py --engine animatediff

# 日常生图/生视频（完全离线）
python scripts/generate.py --engine sdxl --prompt "..." --t image
python scripts/generate.py --engine animatediff --prompt "..." --t video --duration 30
```

## 统一接口

所有引擎实现同一个 `BaseAdapter` 抽象类，代码可无缝切换：

```python
from prism.adapters import get_engine

# SDXL 出图
client = get_engine('sdxl')
out_img = client.generate_image("一只在雪地里奔跑的红狐", size=(1024, 1024))

# AnimateDiff 出视频（最长 30 秒）
client = get_engine('animatediff')
out_vid = client.generate_video("海浪拍打礁石", duration=30, fps=12)
```

## 架构示意

```
用户 Prompt → nanyang-GPT（对话层，独立仓库）→ 工具标记 <|gen_image|> <|gen_video|>
                                                      ↓
                                           Prism Max H1.7
                                             （本地推理层）
                              ┌─────────────────────┴──────────────────┐
                        SDXL Turbo                   AnimateDiff
                      （本地 ~4GB 权重）          （本地 ~8GB 权重）
                         真图 1024px               真视频 最高 30s
                       4 步推理 · 快            无端点限制 · 完全离线
```

- **对话与生成彻底分离**：nanyang-GPT 只做聊天；Prism Max H1.7 只做生成
- **全部离线可运行**：权重要自己下一次（约 12GB），之后零网络依赖
- **服务端友好**：clone → 装依赖 → 下权重 → 跑，无需配置任何密钥
- **与 Helios 自研路线的关系**：原来自研 VAE/DiT 方案已废弃，改用成熟开源大模型作为本地生成底座

## 路线图

- [x] v1.7.0a0 — 骨架发布 · BaseAdapter 统一接口
- [x] v1.7.1 — SDXL Turbo 高清出图 + AnimateDiff 30 秒真视频完整落地，纯离线
- [ ] v1.7.2 — Flux / SDXL 双通道优化
- [ ] v1.8 — 口型同步，剧情对白
- [ ] v1.9 — 批量生产流水线

## 许可

MIT © nanyang 2026
