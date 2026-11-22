# 新增自定义引擎适配器

实现一个适配器只需三步：

## 1. 新建适配器类

`python
# src/prism/adapters/my_engine.py
from .base import BaseAdapter

class MyEngineAdapter(BaseAdapter):
    def generate_image(self, prompt, negative_prompt='', size=(1024,1024), **kw):
        ...   # 调用外部 SDK / API，返回本地 PNG 路径

    def generate_video(self, prompt, negative_prompt='', duration=15.0, fps=12, **kw):
        ...   # 返回本地 MP4 路径
`

## 2. 注册到适配器表

编辑 src/prism/adapters/__init__.py：

`python
from .my_engine import MyEngineAdapter
ADAPTER_REGISTRY['my-engine'] = MyEngineAdapter
`

## 3. 使用

`ash
python -m prism.max generate --engine my-engine --prompt "..."
`

参考现有适配器：minimax_h3.py、sdxl.py、nimatediff.py。
