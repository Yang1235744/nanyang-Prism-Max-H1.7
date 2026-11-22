import time
from pathlib import Path
from typing import Tuple

try:
    from diffusers import DiffusionPipeline, DDIMScheduler
    from diffusers.utils import export_to_video
except ImportError:
    raise ImportError('需要安装 diffusers>=0.30，请运行: pip install -r requirements.txt')

from .base import BaseAdapter

DEFAULT_ANIMATEDIFF_REPO = 'guoyww/animatediff-motion-lora'
DEFAULT_VIDEO_REPO = 'cerspense/zeroscope_v2_576w'

# 最长支持视频帧数（fps=12 时约对应 30 秒）
MAX_FRAMES = 360   # 30s @ 12fps


class AnimatedDiffAdapter(BaseAdapter):
    """AnimateDiff + Zeroscope 视频生成适配器。

    首跑自动下载约 8 GB 权重到 ~/.cache/nanyang-prism/animatediff-cache/。
    完全离线运行，无需任何外部服务。
    """

    def __init__(self, device: str = 'cuda'):
        self.device = device
        self.cache_dir = Path.home() / '.cache' / 'nanyang-prism' / 'animatediff-cache'
        self._pipe = None

    def _load_pipe(self):
        if self._pipe is not None:
            return self._pipe
        motion_lora = self.cache_dir / 'motion_lora.safetensors'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not motion_lora.exists():
            from huggingface_hub import hf_hub_download
            hf_hub_download(
                DEFAULT_ANIMATEDIFF_REPO, filename='diffusion_pytorch_model.safetensors',
                local_dir=self.cache_dir, local_dir_use_symlinks=False
            )
            import shutil
            src = self.cache_dir / 'diffusion_pytorch_model.safetensors'
            if src.exists():
                shutil.move(src, motion_lora)
        self._pipe = DiffusionPipeline.from_pretrained(
            DEFAULT_VIDEO_REPO,
            motion_module=str(motion_lora),
            torch_dtype='auto',
        ).to(self.device)
        self._pipe.scheduler = DDIMScheduler.from_config(self._pipe.scheduler.config)
        self._pipe.enable_model_cpu_offload()
        return self._pipe

    def generate_image(self, *a, **kw):
        raise NotImplementedError('AnimateDiff 专门用于视频生成，请用 sdxl 获取单帧图')

    def generate_video(self, prompt, negative_prompt='', duration=30.0, fps=12, audio=True) -> Path:
        pipe = self._load_pipe()
        num_frames = min(int(duration * fps), MAX_FRAMES)
        if num_frames > MAX_FRAMES:
            duration = MAX_FRAMES / fps
            print(f'提示：视频已截断为 {duration:.1f} 秒（{num_frames} 帧），这是当前引擎上限。')
        out = self.cache_dir / f'vid_{int(time.time())}.mp4'
        frames = pipe(prompt=prompt, negative_prompt=negative_prompt,
                      num_frames=num_frames, width=576, height=320,
                      num_inference_steps=min(25, max(10, num_frames // 5)),
                      guidance_scale=8.0).frames[0]
        export_to_video(frames, str(out), fps=fps)
        return out
