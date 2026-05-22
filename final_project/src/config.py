import os
from pathlib import Path
from typing import Dict, Any

import yaml


class Config:
    def __init__(self, config_path: str = 'chat.yaml'):

        yaml_config: Dict[str, Any] = {}
        if Path(config_path).exists():
            with open(config_path, encoding='utf-8') as file:
                yaml_config = yaml.safe_load(file) or {}

        self.api_host = os.environ.get('API_HOST') or yaml_config.get('api_host')
        self.api_key = os.environ.get('API_KEY') or yaml_config.get('api_key')

        raw_limit_message = os.environ.get('LIMIT_MESSAGE') or yaml_config.get('limit_message')
        self.messages_limit = int(raw_limit_message) if raw_limit_message is not None else 30

        raw_limit_chars = os.environ.get('LIMIT_CHARS') or yaml_config.get('limit_chars')
        self.chars_limit = int(raw_limit_chars) if raw_limit_chars is not None else 2000

        raw_temperature = os.environ.get('TEMPERATURE') or yaml_config.get('temperature')
        self.temperature = float(raw_temperature) if raw_temperature is not None else 0.7

        self.system_message = yaml_config.get('system_prompt')
        self.model = 'gemma3:270m'

        if not self.api_host or not self.api_key:
            raise ValueError(
                'Не указаны API_HOST и API_KEY. Добавьте их в config.yaml или переменные окружения.'
            )

        if not (0 <= self.temperature <= 1):
            raise ValueError('Temperature должна быть от 0 до 1')

        if self.messages_limit <= 0 or self.chars_limit <= 0:
            raise ValueError('Лимиты должны быть положительными')
