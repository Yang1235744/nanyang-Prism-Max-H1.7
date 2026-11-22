import abc
from pathlib import Path
from typing import Optional, Tuple


class BaseAdapter(abc.ABC):
    \"\"\"所有生成引擎的统一接口。子类必须实现 generate_image / generate_video。\"\"\"

    @abc.abstractmethod
    def generate_image(self, prompt: str, negative_prompt: str = '',
                       size: Tuple[int, int] = (1024, 1024),
                       steps: int = 30, cfg_scale: float = 7.5) -> Path:
        \"\"\"返回本地 PNG 路径。\"\"\"
        ...

    @abc.abstractmethod
    def generate_video(self, prompt: str, negative_prompt: str = '',
                       duration: float = 15.0, fps: int = 12,
                       audio: bool = True) -> Path:
        \"\"\"返回本地 MP4 路径（含 AAC 音轨）。\"\"\"
        ...

    def generate(self, prompt: str, negative_prompt: str = '',
                 output_type: str = 'image', **kwargs) -> Path:
        if output_type == 'video':
            return self.generate_video(prompt=prompt, negative_prompt=negative_prompt, **kwargs)
        return self.generate_image(prompt=prompt, negative_prompt=negative_prompt, **kwargs)
