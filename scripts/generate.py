"""CLI：python scripts/generate.py --engine sdxl --prompt ... --t image|video"""
import argparse
import os
from pathlib import Path

sys_path = str(Path(__file__).resolve().parents[1])
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)

from prism.adapters import get_engine, list_engines


def main():
    p = argparse.ArgumentParser(description='nanyang-Prism-Max-H1.7 生成工具')
    p.add_argument('--engine', required=True, choices=list_engines(), help='引擎名')
    p.add_argument('--prompt', required=True, help='生成提示词（中英文均可）')
    p.add_argument('--negative', default='', help='负向提示词')
    p.add_argument('-t', '--type', dest='output_type', default='image',
                   choices=['image', 'video'], help='输出类型（默认 image）')
    p.add_argument('--size', type=int, nargs=2, default=[1024, 1024], metavar=('W', 'H'),
                   help='图片尺寸 width height，默认 1024x1024')
    p.add_argument('--steps', type=int, default=None, help='采样步数（留空用引擎默认）')
    p.add_argument('--cfg-scale', type=float, default=None, help='CFG scale（留空用引擎默认）')
    p.add_argument('--duration', type=float, default=30.0, help='视频时长（秒），默认 30')
    p.add_argument('--fps', type=int, default=12, help='视频帧率，默认 12')
    p.add_argument('--audio', action='store_true', default=True, help='包含音轨（默认开启）')
    p.add_argument('--out', '-o', default=None, help='输出路径（不含扩展名，默认写入缓存目录）')
    args = p.parse_args()

    kwargs = {}
    client = get_engine(args.engine, **kwargs or None)

    print(f'[nanyang-Prism-Max-H1.7] 正在调用 {args.engine} 引擎生成 "{args.prompt[:50]}"...')

    if args.output_type == 'video':
        out_path = client.generate_video(
            prompt=args.prompt,
            negative_prompt=args.negative,
            duration=args.duration,
            fps=args.fps,
            audio=args.audio,
        )
    else:
        gen_kwargs = dict(prompt=args.prompt, negative_prompt=args.negative, size=tuple(args.size))
        if args.steps:
            gen_kwargs['steps'] = args.steps
        if args.cfg_scale:
            gen_kwargs['cfg_scale'] = args.cfg_scale
        out_path = client.generate_image(**gen_kwargs)

    if args.out:
        out_path = out_path.rename(Path(args.out))

    print(f'[nanyang-Prism-Max-H1.7] 完成：{out_path.resolve()}')


if __name__ == '__main__':
    main()
