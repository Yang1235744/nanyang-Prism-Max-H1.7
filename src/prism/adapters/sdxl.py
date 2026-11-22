import time
from pathlib import Path
from typing import Tuple

try:
    from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
except ImportError:
    raise ImportError('需要安装 diffusers>=0.30，请运行: pip install -r requirements.txt')

from .base import BaseAdapter


DEFAULT_SDXL_REPO = 'stabilityai/stable-diffusion-xl-base-1.0'
DEFAULT_TURBO_REPO = 'stabilityai/sdxl-turbo'


class SDXLAdapter(BaseAdapter):
    \"\"\"SDXL / SDXL Turbo 本地生成引擎。无需 API Key，首次自动下载模型权重（约 13 GB）。\"\"\"

    def __init__(self, repo_id: str = None, device: str = 'cuda', cache_dir: str = None):
        self.repo_id = repo_id or DEFAULT_TURBO_REPO   # turbo 版更快（4 步即可出图）
        self.device = device
        self.cache_dir = Path(cache_dir) if cache_dir else (Path.home() / '.cache' / 'nanyang-prism' / 'sdxl-cache')
        self._pipe = None

    def _load_pipe(self):
        if self._pipe is not None:
            return self._pipe
        from huggingface_hub import snapshot_download
        model_path = snapshot_download(
            self.repo_id, local_dir=self.cache_dir,
            ignore_patterns=['*.safetensors'] if 'turbo' in self.repo_id else None
        )
        scheduler_cls = DPMSolverMultistepScheduler
        self._pipe = StableDiffusionXLPipeline.from_pretrained(
            self.cache_dir, torch_dtype='auto', safety_checker=None,
        ).to(self.device)
        self._pipe.scheduler = scheduler_cls.from_config(self._pipe.scheduler.config)
        self._pipe.enable_model_cpu_offload()
        return self._pipe

    def generate_image(self, prompt, negative_prompt='', size=(1024,1024),
                       steps=4, cfg_scale=1.0) -> Path:
        pipe = self._load_pipe()
        out = self.cache_dir / f'sdxl_{int(time.time())}.png'
        result = pipe(prompt=prompt, negative_prompt=negative_prompt,
                      width=size[0], height=size[1], num_inference_steps=steps,
                      guidance_scale=cfg_scale).images[0]
        result.save(out)
        return out

    def generate_video(self, prompt, negative_prompt='', duration=15.0, fps=12, audio=True) -> Path:
        raise NotImplementedError(
            'SDXL 只支持静态图片生成；视频请用 animatediff 或 minimax-h3 适配器'
        )
