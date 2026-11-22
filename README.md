# nanyang-Prism-Max-H1.7

**全新生成底座 · 接 MiniMax H3 / SDXL 等商用引擎 · 对话与生成彻底解耦**


anyang-Prism-Max-H1.7 是南阳系列中专攻 **图像/视频生成** 的产品，与「南阳 GPT」对话模型完全分离：各自独立仓库、独立训练、独立维护。

模型规模约 **25 GB**（fp16），采用多引擎适配器架构——底层接入 MiniMax H3 等成熟商业/开源生成底座，上层提供统一的 prompt $\rightarrow$ 真图/真视频调用接口。

## 架构速览

\\\
用户 Prompt $\rightarrow$  nanyang-GPT (对话层)  $\rightarrow$ 工具标记 $\rightarrow$  Prism Max H1.7
                                                        $|$
                                          $\leftrightarrow$ MiniMax H3 / SDXL / Flux / AnimatedDiff
\\\

- **对话与生成彻底分离**：nanyang-GPT 只做聊天；Prism Max H1.7 只做生成
- **多引擎可插拔**：新增引擎只需实现对应 Adapter 类并注册
- **统一工具协议**：沿用 <|gen_image|> / <|gen_video|> 标准标记

## 特性

| 项 | 说明 |
| --- | --- |
| 生成类型 | 高清图片（最高 1024px+）、15 秒带音频视频 |
| 适配引擎 | MiniMax H3（主力）、SDXL、Flux、AnimatedDiff（可扩展） |
| 模型规模 | ~25 GB（含多引擎权重 + 文本编码器 + VAE） |
| 输出格式 | PNG / MP4 + AAC 音轨 |
| 部署方式 | CLI / Python API / HTTP Server |
| 对话耦合 | **无**——对话由独立仓库 nanyang-GPT 负责 |

## 快速开始

\\\ash
git clone https://github.com/Yang1235744/nanyang-Prism-Max-H1.7.git
cd nanyang-Prism-Max-H1.7
pip install -r requirements.txt

python scripts/download_weights.py --engine minimax-h3
python -m prism.max generate --engine minimax-h3 --prompt "一只橘猫在阳光下打盹" --size 1024 --out out.png
python -m prism.max generate --engine animatediff --prompt "猫咪跳上窗台" --duration 15 --fps 12 --audio true --out out.mp4
\\\

## 引擎适配器 API

\\\python
from prism.adapters import get_engine

client = get_engine("minimax-h3")
img = client.generate("一只橘猫", size=(1024,1024))   # PIL.Image
mp4 = client.generate("猫咪跳上窗台", output_type="video", duration=15)   # pathlib.Path
\\\

## 路线图

- [x] v1.7.0a0 — 骨架发布 · 多引擎适配器框架
- [ ] v1.7.1 — MiniMax H3 正式集成 + 首批真图测试
- [ ] v1.7.2 — Flux / SDXL 双通道支持
- [ ] v1.8 — 剧情对白 + 口型同步
- [ ] v1.9 — 批量生产流水线

## 许可

MIT © nanyang 2026
