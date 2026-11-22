import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from prism.adapters.minimax_h3 import MiniMaxH3Adapter
from prism.adapters.sdxl import SDXLAdapter
from prism.adapters.animatediff import AnimatedDiffAdapter


ENGINES = {
    'minimax-h3': MiniMaxH3Adapter,
    'sdxl': SDXLAdapter,
    'animatediff': AnimatedDiffAdapter,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, choices=list(ENGINES.keys()))
    args = ap.parse_args()
    adapter_cls = ENGINES[args.engine]
    adapter_cls()   # 触发首次加载，自动下载权重
    print(f'[download] {args.engine} 初始化完成，权重在 {adapter_cls.__name__.lower()} 缓存目录')


if __name__ == '__main__':
    main()
