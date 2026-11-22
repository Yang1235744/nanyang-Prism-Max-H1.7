"""nanyang-GPT ↔ Prism 集成适配层。

当 nanyang-GPT 输出 <|gen_image|>... 或 <|gen_video|>... 标记时，
本模块负责解析并调用对应的本地引擎完成生成。

使用方式：
    from prism.prism_chat_adapter import GPTChatAdapter
    adapter = GPTChatAdapter()
    results, user_text = adapter.handle_gpt_output(gpt_reply)
"""
import re
from pathlib import Path
from typing import Optional, Tuple

# 延迟导入，避免未安装 diffusers 时报错
try:
    from prism.adapters import get_engine
    _PRISM_AVAILABLE = True
except ImportError:
    _PRISM_AVAILABLE = False

GEN_IMAGE_RE = re.compile(r'<\|gen_image\|>\s*(.*?)\s*(?=<\|/gen_image\|>|$)', re.DOTALL)
GEN_VIDEO_RE = re.compile(r'<\|gen_video\|>\s*(.*?)\s*(?=<\|/gen_video\|>|$)', re.DOTALL)


class GenerationResult:
    """一次工具调用的结果。"""

    def __init__(self, kind: str, prompt: str, path: Optional[Path] = None,
                 error: Optional[str] = None):
        self.kind = kind       # 'image' | 'video'
        self.prompt = prompt
        self.path = path       # 成功时指向生成的文件
        self.error = error     # 失败时的错误信息

    @property
    def success(self) -> bool:
        return self.path is not None and self.error is None

    def summary(self) -> str:
        if self.success:
            return f'[生成完毕] {self.kind}：{self.path.resolve()}'
        return f'[生成失败] {self.error}'


class GPTChatAdapter:
    """将 nanyang-GPT 的输出标记解析为实际的图片/视频生成任务。

    nanyang-GPT 在对话中遇到需要生成的内容时，会输出如下格式的标记：
      - <|gen_image|>描述文字<|/gen_image|>
      - <|gen_video|>描述文字<|/gen_video|>

    handle_gpt_output 负责：
      1. 从 GPT 回复中提取这些标记及描述
      2. 调用对应引擎（SDXL / AnimateDiff）生成
      3. 返回结果，并附带给用户的后续回复建议
    """

    def __init__(self, device: str = 'cuda', verbose: bool = True):
        if not _PRISM_AVAILABLE:
            raise ImportError(
                '请先安装 nanyang-Prism-Max-H1.7：'
                'pip install -r requirements.txt && python scripts/download_weights.py --engine sdxl animatediff'
            )
        self.device = device
        self.verbose = verbose

    def handle_gpt_output(self, gpt_reply: str) -> Tuple[list, str]:
        """解析 GPT 回复，执行所有生成任务，返回 (结果列表, 给用户的文本)。

        Args:
            gpt_reply: nanyang-GPT 原始输出，可能包含 <|gen_image|>/<|gen_video|> 标记。

        Returns:
            (results, user_text):
                results 是 GenerationResult 列表，每个代表一次生成任务
                user_text 是展示给用户的最终文本（已移除标记）
        """
        results = []
        user_text = self._strip_markers(gpt_reply)

        # 处理图片生成
        for match in GEN_IMAGE_RE.finditer(gpt_reply):
            prompt = match.group(1).strip()
            if not prompt:
                continue
            if self.verbose:
                print(f'[GPTChatAdapter] 检测到图片生成请求: "{prompt[:60]}"')
            result = self._generate_image(prompt)
            results.append(result)
            if result.success:
                user_text += f'\n\n✅ 已为你生成图片，保存在：{result.path.name}'
            else:
                user_text += f'\n\n❌ 图片生成失败：{result.error}'

        # 处理视频生成
        for match in GEN_VIDEO_RE.finditer(gpt_reply):
            prompt = match.group(1).strip()
            if not prompt:
                continue
            if self.verbose:
                print(f'[GPTChatAdapter] 检测到视频生成请求: "{prompt[:60]}"')
            result = self._generate_video(prompt)
            results.append(result)
            if result.success:
                user_text += f'\n\n✅ 已为你生成视频（30秒），保存在：{result.path.name}'
            else:
                user_text += f'\n\n❌ 视频生成失败：{result.error}'

        return results, user_text

    def _generate_image(self, prompt: str) -> GenerationResult:
        try:
            client = get_engine('sdxl', device=self.device)
            out_path = client.generate_image(prompt=prompt, negative_prompt='')
            return GenerationResult(kind='image', prompt=prompt, path=out_path)
        except Exception as e:
            return GenerationResult(kind='image', prompt=prompt, error=str(e))

    def _generate_video(self, prompt: str) -> GenerationResult:
        try:
            client = get_engine('animatediff', device=self.device)
            out_path = client.generate_video(prompt=prompt, duration=30.0, fps=12)
            return GenerationResult(kind='video', prompt=prompt, path=out_path)
        except Exception as e:
            return GenerationResult(kind='video', prompt=prompt, error=str(e))

    @staticmethod
    def _strip_markers(text: str) -> str:
        """移除所有生成标记，只保留正常对话文本。"""
        text = GEN_IMAGE_RE.sub('', text)
        text = GEN_VIDEO_RE.sub('', text)
        return text.strip()
