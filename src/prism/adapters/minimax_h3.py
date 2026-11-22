import os
import time
from pathlib import Path
from typing import Tuple

import requests

from .base import BaseAdapter


class MiniMaxH3Adapter(BaseAdapter):
    """MiniMax H3 图像/视频生成引擎适配器。

    使用环境变量提供认证：
      MINIMAX_API_KEY     —— API 密钥（必填）
      MINIMAX_GROUP_ID    —— Group ID（可选，部分接口需要）
    API 端点默认走 easyframe.cn 加速代理：
      https://minimax.api.easyframe.cn/api/v3
    """

    MODEL_NAME = 'mini-max/h3-v1'
    DEFAULT_BASE_URL = 'https://minimax.api.easyframe.cn/api/v3'
    CACHE_DIR = Path.home() / '.cache' / 'nanyang-prism' / 'engine-cache'

    def __init__(self, api_key: str = None, group_id: str = None):
        self.api_key = api_key or os.environ.get('MINIMAX_API_KEY', '')
        self.group_id = group_id or os.environ.get('MINIMAX_GROUP_ID', '')
        self.base_url = os.environ.get(
            'MINIMAX_API_BASE', self.DEFAULT_BASE_URL
        )
        if not self.api_key:
            raise RuntimeError(
                '缺少 MiniMax API 密钥。请设置环境变量 MINIMAX_API_KEY\n'
                '示例：export MINIMAX_API_KEY="sk-api-xxx"\n'
                '或在 .env 文件中填写 MINIMAX_API_KEY=sk-api-xxx'
            )
        self._ensure_cache()

    def _ensure_cache(self):
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _headers(self) -> dict:
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    # ------------------------------------------------------------------
    # 图片生成 —— POST /images/generations（同步）
    # ------------------------------------------------------------------
    def generate_image(self, prompt, negative_prompt='', size=(1024, 1024),
                       steps=30, cfg_scale=7.5) -> Path:
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
            headers=self._headers(),
            timeout=300,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data.get('data', [{}])[0].get('b64_json') or data.get('result', {}).get('b64_json')
        if not b64:
            raise RuntimeError(f'图片生成失败，响应体：{data}')
        import base64
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(base64.b64decode(b64)))
        img.save(out)
        return out

    # ------------------------------------------------------------------
    # 视频生成 —— POST /videos/generations + GET /tasks/{id} 轮询
    # ------------------------------------------------------------------
    def generate_video(self, prompt, negative_prompt='', duration=15.0, fps=12, audio=True) -> Path:
        out = self.CACHE_DIR / f'video_{int(time.time())}.mp4'
        payload = {
            'model': self.MODEL_NAME.replace('h3', 'h3-video'),
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'duration': duration,
            'fps': fps,
            'audio': audio,
        }
        resp = requests.post(
            f'{self.base_url}/videos/generations',
            json=payload,
            headers=self._headers(),
            timeout=60,
        )
        resp.raise_for_status()
        task_id = resp.json().get('task_id') or resp.json().get('data', {}).get('task_id')
        if not task_id:
            raise RuntimeError(f'视频生成请求未返回 task_id，响应体：{resp.text}')

        # 轮询直到完成（最多 300 次 × 1s ≈ 5 分钟）
        for _ in range(300):
            t_resp = requests.get(
                f'{self.base_url}/tasks/{task_id}',
                headers=self._headers(),
                timeout=30,
            )
            t_resp.raise_for_status()
            info = t_resp.json().get('data', t_resp.json())
            status = info.get('status', '')
            if status == 'completed':
                url = info.get('result', {}).get('url') or info.get('url')
                if not url:
                    raise RuntimeError(f'视频已完成但无下载链接: {info}')
                video_bytes = requests.get(url, timeout=120).content
                out.write_bytes(video_bytes)
                return out
            if status in ('failed', 'cancelled', 'error'):
                err_msg = info.get('error', info.get('message', ''))
                raise RuntimeError(f'视频生成失败 [{status}]: {err_msg}')
            time.sleep(1)

        raise TimeoutError(f'视频生成超时（300s），task_id={task_id}')
