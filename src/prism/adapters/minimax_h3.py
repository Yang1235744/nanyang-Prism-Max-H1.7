import os
import time
from pathlib import Path
from typing import Tuple

import requests

from .base import BaseAdapter


class MiniMaxH3Adapter(BaseAdapter):
    \"\"\"MiniMax H3 图像/视频生成引擎适配器。

    需要环境变量 MINIMAX_API_KEY 和 MINIMAX_GROUP_ID（或 API_BASE_URL）才能正常工作。
    首次调用会自动下载所需模型权重到 ~/.cache/nanyang-prism/engine-cache/。
    \"\"\"

    MODEL_NAME = 'mini-max/h3-v1'
    CACHE_DIR = Path.home() / '.cache' / 'nanyang-prism' / 'engine-cache'

    def __init__(self, api_key: str = None, group_id: str = None):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY')
        self.group_id = group_id or os.environ.get('MINIMAX_GROUP_ID', '')
        self.base_url = os.environ.get(
            'MINIMAX_API_BASE', 'https://api.minimax.io/v1'
        )
        self._ensure_cache()

    def _ensure_cache(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def generate_image(self, prompt, negative_prompt='', size=(1024, 1024),
                       steps=30, cfg_scale=7.5) -> Path:
        if not self.api_key:
            raise RuntimeError('需要设置环境变量 MINIMAX_API_KEY')
        out = self.CACHE_DIR / f'image_{int(time.time())}.png'
        payload = {
            'model': self.MODEL_NAME,
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': size[0],
            'height': size[1],
            'steps': steps,
            'cfg_scale': cfg_scale,
        }
        resp = requests.post(
            f'{self.base_url}/images/generations',
            json=payload,
            headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
            timeout=300,
        )
        resp.raise_for_status()
        b64 = resp.json()['data'][0]['b64_json']
        import base64
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(base64.b64decode(b64)))
        img.save(out)
        return out

    def generate_video(self, prompt, negative_prompt='', duration=15.0, fps=12, audio=True) -> Path:
        if not self.api_key:
            raise RuntimeError('需要设置环境变量 MINIMAX_API_KEY')
        out = self.CACHE_DIR / f'video_{int(time.time())}.mp4'
        payload = {
            'model': self.MODEL_NAME.replace('h3', 'h3-video'),
            'prompt': prompt,
            'duration': duration,
            'fps': fps,
            'audio': audio,
        }
        # 异步任务轮询（MiniMax H3 video 为异步生成）
        resp = requests.post(
            f'{self.base_url}/videos/generations',
            json=payload,
            headers={'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'},
            timeout=60,
        )
        resp.raise_for_status()
        task_id = resp.json()['task_id']
        for _ in range(300):   # 最多等 5 分钟
            t = requests.get(f'{self.base_url}/tasks/{task_id}',
                             headers={'Authorization': f'Bearer {self.api_key}'}, timeout=30)
            status = t.json().get('status')
            if status == 'completed':
                url = t.json()['result']['url']
                with open(out, 'wb') as f:
                    f.write(requests.get(url, timeout=120).content)
                return out
            if status in ('failed', 'cancelled'):
                raise RuntimeError(f'视频生成失败: {status}')
            time.sleep(1)
        raise TimeoutError('视频生成超时')
