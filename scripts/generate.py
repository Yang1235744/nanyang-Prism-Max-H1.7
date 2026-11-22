import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from prism.adapters import get_engine


def main():
    ap = argparse.ArgumentParser(description='nanyang-Prism-Max-H1.7 生成工具')
    ap.add_argument('--engine', required=True, choices=['minimax-h3','sdxl','animatediff'])
    ap.add_argument('--prompt', required=True, help='生成提示词')
    ap.add_argument('--negative', default='', help='负向提示词')
    ap.add_argument('--output-type', '-t', choices=['image','video'], default='image')
    ap.add_argument('--size', '-s', default='1024x1024', help='图片尺寸，如 1024x1024')
    ap.add_argument('--steps', type=int, default=30)
    ap.add_argument('--cfg-scale', type=float, default=7.5)
    ap.add_argument('--duration', '-d', type=float, default=15.0, help='视频时长（秒）')
    ap.add_argument('--fps', type=int, default=12)
    ap.add_argument('--audio', action='store_true', help='视频加入音轨')
    ap.add_argument('--out', '-o', default=None, help='输出路径（不含扩展名）')
    args = ap.parse_args()

    if 'x' in args.size:
        w, h = map(int, args.size.split('x'))
    else:
        w = h = int(args.size)

    engine_name = args.engine
    if engine_name == 'animatediff' and args.output_type == 'image':
        engine_name = 'sdxl'   # AnimateDiff 不自带单图模式

    client = get_engine(engine_name)
    out_path = Path(args.out) if args.out else None

    if args.output_type == 'video':
        result = client.generate_video(
            prompt=args.prompt, negative_prompt=args.negative,
            duration=args.duration, fps=args.fps, audio=args.audio,
        )
    else:
        result = client.generate_image(
            prompt=args.prompt, negative_prompt=args.negative,
            size=(w, h), steps=args.steps, cfg_scale=args.cfg_scale,
        )

    print(f'[nanyang-Prism-Max-H1.7] 已生成: {result}')
    return result


if __name__ == '__main__':
    main()
