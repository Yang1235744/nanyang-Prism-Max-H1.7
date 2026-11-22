from .base import BaseAdapter
from .minimax_h3 import MiniMaxH3Adapter
from .sdxl import SDXLAdapter
from .animatediff import AnimatedDiffAdapter

ADAPTER_REGISTRY = {
    'minimax-h3': MiniMaxH3Adapter,
    'sdxl': SDXLAdapter,
    'animatediff': AnimatedDiffAdapter,
}


def get_engine(name: str, api_key: str = None, group_id: str = None) -> BaseAdapter:
    cls = ADAPTER_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f'未知引擎 "{name}"，可用：{list(ADAPTER_REGISTRY.keys())}')
    kwargs = {}
    if api_key is not None:
        kwargs['api_key'] = api_key
    if group_id is not None:
        kwargs['group_id'] = group_id
    return cls(**kwargs)


def list_engines():
    return list(ADAPTER_REGISTRY.keys())
