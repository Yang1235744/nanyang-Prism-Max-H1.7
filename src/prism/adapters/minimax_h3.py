import os
import time
from pathlib import Path
from typing import Tuple

import requests

from .base import BaseAdapter


class MiniMaxH3Adapter(BaseAdapter):
    """MiniMax H3 —— 云端备用通道（可选）。

    需要设置环境变量：
      MINIMAX_API_KEY     （必填）
      MINIMAX_API_BASE    （可选，默认 easyframe.cn 代理地址）

    本地引擎推荐优先使用 sdxl / animatediff（完全离线、无需 API Key）。
    """

    DEFAULT_BASE_URL = 'https://minimax.api.easyframe.cn/api/v3'
    CACHE_DIR = Path.home() / '.cache' / 'nanyang-prism' / 'engine-cache'

    def __init__(self, api_key: str = None, group_id: str = None):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.group_id = group_id or os.environ.get('MINIMAX_GROUP_ID', '')
        self.base_url = os.environ.get('MINIMAX_API_BASE', self.DEFAULT_BASE_URL)
        if not self.api_key:
            raise RuntimeError(
                'MiniMax H3 需要 API Key。\n'
                '  export MINIMAX_API_KEY="sk-api-..."  \n'
                '或使用本地引擎（sdxl / animatediff）则不需要此密钥。'
            )
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _headers(self) -> dict:
        h = {'Content-Type': 'application/json'}
        if self.api_key:
            h['Authorization'] = f'Bearer {self.api_key}'
        return h

    def generate_image(self, prompt, negative_prompt='', size=(1024, 1024),
                       steps=30, cfg_scale=7.5) -> Path:
        out = self.CACHE_DIR / f'mm_img_{int(time.time())}.png'
        payload = dict(
            model='mini-max/h3-v1', prompt=prompt,
            negative_prompt=negative_prompt,
            width=size[0], height=size[1], steps=steps, cfg_scale=cfg_scale,
        )
        resp = requests.post(f'{self.base_url}/images/generations',
                             json=payload, headers=self._headers(), timeout=300)
        resp.raise_for_status()
        data = resp.json()
        b64 = data.get('data', [{}])[0].get('b64_json') or data.get('result', {}).get('b64_json')
        if not b64:
            raise RuntimeError(f'图片生成失败，响应体：{data}')
        import base64
        from PIL import Image
        import io
        Image.open(io.BytesIO(base64.b64decode(b64))).save(out)
        return out

    def generate_video(self, prompt, negative_prompt='', duration=15.0, fps=12, audio=True) -> Path:
        out = self.CACHE_DIR / f'mm_vid_{int(time.time())}.mp4'
        payload = dict(
            model='mini-max/h3-video', prompt=prompt,
            negative_prompt=negative_prompt, duration=duration, fps=fps, audio=audio,
        )
        resp = requests.post(f'{self.base_url}/videos/generations',
                             json=payload, headers=self._headers(), timeout=60)
        resp.raise_for_status()
        task_id = (resp.json().get('task_id') or
                   resp.json().get('data', {}).get('task_id'))
        if not task_id:
            raise RuntimeError(f'视频任务创建失败：{resp.text}')
        for _ in range(300):
            t = requests.get(f'{self.base_url}/tasks/{task_id}',
                             headers=self._headers(), timeout=30)
            t.raise_for_status()
            info = t.json().get('data', t.json())
            status = info.get('status', '')
            if status == 'completed':
                url = info.get('result', {}).get('url') or info.get('url')
                if not url:
                    raise RuntimeError(f'视频完成但无下载链接：{info}')
                out.write_bytes(requests.get(url, timeout=120).content)
                return out
            if status in ('failed', 'cancelled', 'error'):
                raise RuntimeError(f'视频生成失败 [{status}]：{info.get("error", "")}')
            time.sleep(1)
        raise TimeoutError(f'视频生成超时：{task_id}')
