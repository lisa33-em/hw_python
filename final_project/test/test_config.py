import os
import pytest
from src.config import Config


def test_config_from_yaml() -> None:
    config = Config('chat.yaml')

    assert config.api_host == 'http://localhost:11434/v1/'
    assert config.api_key == 'ollama'
    assert config.messages_limit == 30
    assert config.chars_limit == 2000
    assert config.temperature == 0.7
    assert config.system_message == 'You are a helpful AI bot.'
    assert config.model == 'gemma3:270m'


def test_config_env_priority() -> None:
    old_host = os.environ.get('API_HOST')
    old_key = os.environ.get('API_KEY')
    old_limit = os.environ.get('LIMIT_MESSAGE')

    os.environ['API_HOST'] = 'http://env.com/v1/'
    os.environ['API_KEY'] = 'env_key'
    os.environ['LIMIT_MESSAGE'] = '100'

    config = Config('chat.yaml')

    assert config.api_host == 'http://env.com/v1/'
    assert config.api_key == 'env_key'
    assert config.messages_limit == 100

    if old_host:
        os.environ['API_HOST'] = old_host
    else:
        del os.environ['API_HOST']

    if old_key:
        os.environ['API_KEY'] = old_key
    else:
        del os.environ['API_KEY']

    if old_limit:
        os.environ['LIMIT_MESSAGE'] = old_limit
    else:
        del os.environ['LIMIT_MESSAGE']


def test_config_missing_required() -> None:
    with pytest.raises(ValueError, match='Не указаны API_HOST и API_KEY'):
        Config('not_exist.yaml')


def test_config_invalid_temperature() -> None:
    with open('bad_temp.yaml', 'w') as f:
        f.write('api_host: http://test.com/v1/\n')
        f.write('api_key: test\n')
        f.write('temperature: 2.5\n')

    with pytest.raises(ValueError, match='Temperature должна быть от 0 до 1'):
        Config('bad_temp.yaml')

    os.remove('bad_temp.yaml')
