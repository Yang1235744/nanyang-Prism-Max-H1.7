from .base import BaseAdapter
from .minimax_h3 import MiniMaxH3Adapter
from .sdxl import SDXLAdapter
from .animatediff import AnimatedDiffAdapter

ADAPTER_REGISTRY = {
    'minimax-h3': MiniMaxH3Adapter,
    'sdxl': SDXLAdapter,
    'animatediff': AnimatedDiffAdapter,
}


def get_engine(name: str) -> BaseAdapter:
    if name not in ADAPTER_REGISTRY:
        raise ValueError(f"未知引擎 '{name}'，可选: {list(ADAPTER_REGISTRY.keys())}")
    return ADAPTER_REGISTRY[name]()
