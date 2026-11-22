# nanyang-Prism-Max-H1.7 —— 图像/视频生成底座，nanyang-GPT 的专属"小弟"。
__version__ = '1.7.1'

# 公开 API：供 nanyang-GPT 运行时调用
from prism.prism_chat_adapter import GPTChatAdapter, GenerationResult
from prism.adapters import get_engine, list_engines
