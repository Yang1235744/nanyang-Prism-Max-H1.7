"""MiniMax H3 —— 训练数据收集工具。

从 MiniMax H3 API 批量拉取高质量图文/视频对，写入训练数据集目录，
供后续自蒸馏 / 微调使用。

用法：
  python -m prism.max train_data --engine minimax-h3 \
      --prompt-list prompts.txt --out-dir data/training
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prism.adapters.minimax_h3 import MiniMaxH3Adapter


def main():
    p = argparse.ArgumentParser(description='用 MiniMax H3 收集训练数据')
    p.add_argument('--prompt-list', required=True, help='每行一个 prompt 的文件路径')
    p.add_argument('--out-dir', '-o', default='data/training', help='输出根目录')
    p.add_argument('--api-key', default=os.environ.get('MINIMAX_API_KEY', ''),
                   help='MiniMax API 密钥（也可通过 MINIMAX_API_KEY 环境变量设置）')
    p.add_argument('--image-only', action='store_true',
                   help='只生成图片；默认图片+视频')
    args = p.parse_args()

    try:
        client = MiniMaxH3Adapter(api_key=args.api_key or None)
    except RuntimeError as e:
        print(f'配置错误：{e}', file=sys.stderr)
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'prompts.jsonl').write_text('', encoding='utf-8')

    # 读提示词列表
    prompts = [line.strip() for line in open(args.prompt_list, encoding='utf-8') if line.strip()]
    if not prompts:
        print('提示词列表为空', file=sys.stderr)
        return

    print(f'共 {len(prompts)} 条提示词，开始收集...')

    for i, prompt in enumerate(prompts, 1):
        print(f'[{i}/{len(prompts)}] {prompt[:60]}...')

        # --- 图片 ---
        try:
            img_path = client.generate_image(prompt=prompt, size=(1024, 1024))
            dest_img = out_dir / f'{i:04d}_img.png'
            img_path.rename(dest_img)
            print(f'  ✓ 图片 → {dest_img}')
        except Exception as exc:
            print(f'  ✗ 图片失败：{exc}', file=sys.stderr)
            dest_img = None

        # --- 视频（可选跳过）---
        if not args.image_only:
            try:
                vid_path = client.generate_video(prompt=prompt, duration=5.0, fps=12, audio=False)
                dest_vid = out_dir / f'{i:04d}_vid.mp4'
                vid_path.rename(dest_vid)
                print(f'  ✓ 视频 → {dest_vid}')
            except Exception as exc:
                print(f'  ✗ 视频失败：{exc}', file=sys.stderr)
                dest_vid = None

        # 记录元信息
        meta = {'index': i, 'prompt': prompt}
        if dest_img:
            meta['image'] = str(dest_img)
        if dest_vid:
            meta['video'] = str(dest_vid)
        (out_dir / 'prompts.jsonl').write_text(
            '\n'.join(json.dumps(m, ensure_ascii=False) for m in
                      list((out_dir / 'prompts.jsonl').read_text(encoding='utf-8').strip().split('\n')) + [json.dumps(meta, ensure_ascii=False)]) + '\n',
            encoding='utf-8')

        # 礼貌等待，避免限流
        time.sleep(1)

    print(f'\n完成！数据已保存到 {out_dir.resolve()}')


if __name__ == '__main__':
    main()
