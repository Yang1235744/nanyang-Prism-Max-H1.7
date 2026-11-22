# nanyang-Prism-Max-H1.7

**全新生成底座 · 数据训练 → 本地模型**

---

nanyang-Prism-Max-H1.7 是南阳系列中专攻 **图像/视频生成** 的产品，与「南阳 GPT」对话模型完全分离：各自独立仓库、独立维护。

版本路线说明：
- **Helios 1.2 / 1.5 已停止使用**，仅保留自研代码供查看，不再提供模型拉取/下载链接。
- **自研生成路线已放弃**，新版本切换到全新建设路线：用高质量 API 数据训练 → 分发可离线运行的本地模型。
- 当前主推 **Prism H1.7**，接图形化大型生成数据做训练底座，逐步迭代出本地可用的模型。

## 工作流：先收集数据，再训模型

```
Step 1  准备提示词列表（ prompts.txt ）
Step 2  python scripts/train_data.py --prompt-list prompts.txt --out-dir data/training
        ↑ 调用 MiniMax H3 API，批量生成图文/视频样本写入本地数据集
Step 3  python scripts/train_model.py --data-dir data/training --epochs N
        ↑ 在本地 GPU 上训你自己的模型（蒸馏 / 微调）
Step 4  训练完成，把产出的权重推送到 GitHub / NAS
        其他用户 git clone + pip install 后，直接本地推理，无需任何云端依赖
```

## 快速开始 —— 数据收集阶段

```bash
git clone https://github.com/Yang1235744/nanyang-Prism-Max-H1.7.git
cd nanyang-Prism-Max-H1.7
pip install -r requirements.txt
cp .env.example .env    # 填入训练密钥
```

**.env 配置：**

```ini
MINIMAX_API_KEY=sk-api-...          # 训练密钥，见项目内 .env.example
MINIMAX_API_BASE=https://minimax.api.easyframe.cn/api/v3
```

**收集数据示例：**

```bash
# 写一份提示词（每行一个）
echo "雪地里的红狐" >> prompts.txt
echo "海浪拍打礁石" >> prompts.txt
echo "赛博朋克城市夜景" >> prompts.txt

# 批量拉取（图片+短视频，约 5s / 条）
python scripts/train_data.py \
    --prompt-list prompts.txt \
    --out-dir data/training \
    --api-key "$MINIMAX_API_KEY"

# 只要图片不要视频
python scripts/train_data.py --prompt-list prompts.txt --out-dir data/training --image-only
```

输出结构：
```
data/training/
  0001_img.png   0001_vid.mp4
  0002_img.png   0002_vid.mp4
  ...
  prompts.jsonl  ← 元信息索引
```

## 架构

```
用户 Prompt → nanyang-GPT（对话层）→ 工具标记 <|gen_image|> <|gen_video|>
                                               ↓
                                    Prism Max H1.7
                                      （训练 + 推理层）
                   ┌─────────────────────┴──────────────────────────┐
              收集阶段                        使用阶段
      MiniMax H3 API → 训练数据集       本地 GPU 训好的模型离线推理
              ↓
     ~25GB 参数规模（待训练完成后产出）
```

- **对话与生成彻底分离**：nanyang-GPT 只做聊天；Prism Max H1.7 只做生成
- **先训后用**：API 数据收集 → 本地训模 → 离线分发
- **统一接口**：所有引擎实现 `BaseAdapter`，可插拔扩展

## 路线图

- [x] v1.7.0a0 — 骨架发布 · 多引擎适配器框架
- [x] v1.7.1 — 数据收集工具（`train_data.py`）上线；MiniMax H3 接入
- [ ] v1.7.2 — 训练脚本（`train_model.py`）+ 本地推理通道
- [ ] v1.8 — 口型同步，剧情对白
- [ ] v1.9 — 批量生产流水线，离线分发包

## 许可

MIT © nanyang 2026
