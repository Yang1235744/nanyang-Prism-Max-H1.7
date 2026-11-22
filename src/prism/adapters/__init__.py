from .base import BaseAdapter
from .sdxl import SDXLAdapter
from .animatediff import AnimatedDiffAdapter
# 内部训练用，不对外暴露
try:
    from .minimax_h3 import MiniMaxH3Adapter
except ImportError:
    MiniMaxH3Adapter = None

ADAPTER_REGISTRY = {
    'sdxl': SDXLAdapter,
    'animatediff': AnimatedDiffAdapter,
}

# 训练时临时加入，生产环境不暴露
if MiniMaxH3Adapter is not None:
    ADAPTER_REGISTRY['minimax-h3'] = MiniMaxH3Adapter


def get_engine(name: str, api_key: str = None, group_id: str = None) -> BaseAdapter:
    cls = ADAPTER_REGISTRY.get(name)
    if cls is None:
        # minimax-h3 仅供内部训练，不在公开文档中说明
        available = [k for k in ADAPTER_REGISTRY if k != 'minimax-h3']
        hidden = [k for k in ADAPTER_REGISTRY if k == 'minimax-h3']
        hint = ''
        if name in hidden:
            hint = '（minimax-h3 为内部训练通道，不对外暴露）'
        raise ValueError(f'未知引擎 "{name}"，可用：{available}{hint}')
    kwargs = {}
    if api_key is not None:
        kwargs['api_key'] = api_key
    if group_id is not None:
        kwargs['group_id'] = group_id
    return cls(**kwargs)


def list_engines():
    # 对外只显示本地引擎
    return [k for k in ADAPTER_REGISTRY.keys() if k != 'minimax-h3']
