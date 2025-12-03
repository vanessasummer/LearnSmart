"""日志工具"""
import logging
import sys
from app.config import settings

# 配置日志格式
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# 创建logger
logger = logging.getLogger("LearnSmart")
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

# 如果还没有handler，添加一个
if not logger.handlers:
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

