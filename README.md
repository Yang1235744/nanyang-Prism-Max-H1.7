# nanyang-Prism-Max-H1.7

**全新生成底座 · 接入图形化大型生成 · 对话与生成彻底解耦**

---

nanyang-Prism-Max-H1.7 是南阳系列中专攻 **图像/视频生成** 的产品，与「南阳 GPT」对话模型完全分离：各自独立仓库、独立维护。

版本路线说明：
- **Helios 1.2 / 1.5 已停止使用**，仅保留自研代码供查看，不再提供模型拉取/下载链接。
- **自研生成路线已放弃**，新版本切换到全新建设路线。
- 当前主推 **Prism H1.7**，接入图形化大型生成底座，持续往上迭代。

## 快速开始

```bash
git clone https://github.com/Yang1235744/nanyang-Prism-Max-H1.7.git
cd nanyang-Prism-Max-H1.7
pip install -r requirements.txt

# 设置 API 密钥（从 .env.example 复制后填入真实密钥）
cp .env.example .env
```

### 配置 MiniMax H3

在 `.env` 或环境变量中填入以下信息：

```bash
export MINIMAX_API_KEY="sk-api-YBHaqZGNzc40ywK5G-Be5om9jguhB3REjlgv05NWtsN7cX1Y6e1g3Me8-wGsa2D6rkGg0KNaCvOg3iUAnth0ToOv5mk2whgR14S6PfeA6DuIJN35JLkZdHw"
# 可选：自定义端点（默认已是 easyframe.cn 代理）
export MINIMAX_API_BASE="https://minimax.api.easyframe.cn/api/v3"
```

### 运行

```bash
# 生成图片
python scripts/generate.py --engine minimax-h3 \
    --prompt "雪地里的红狐" --t image --size 1024 1024

# 生成 15 秒带音频视频
python scripts/generate.py --engine minimax-h3 \
    --prompt "海浪拍打礁石" --t video --duration 15 --fps 12
```

## 架构

```
用户 Prompt → nanyang-GPT (对话层) → 工具标记 <|gen_image|> <|gen_video|>
                                              ↓
                                   Prism Max H1.7
                                     （生成层）
                                              ↓
                                   接入图形化大型生成底座（MiniMax H3）
```

- **对话与生成彻底分离**：nanyang-GPT 只做聊天；Prism Max H1.7 只做生成
- **统一接口**：所有引擎实现 `BaseAdapter`，可插拔扩展
- **环境配置**：API key 走环境变量，不硬编码进源码

## 路线图

- [x] v1.7.0a0 — 骨架发布 · 多引擎适配器框架
- [x] v1.7.1 — MiniMax H3 正式集成 + API 密钥接入
- [ ] v1.7.2 — 更多引擎可插拔（本地兜底通道）
- [ ] v1.8 — 口型同步，剧情对白
- [ ] v1.9 — 批量生产流水线

## 许可

MIT © nanyang 2026
