from unittest.mock import Mock, patch
from src.ollamaChat import OllamaBot


def test_add_message() -> None:
    config = Mock()
    config.api_host = 'http://localhost:11434/v1/'
    config.api_key = 'ollama'
    config.messages_limit = 5
    config.chars_limit = 1000
    config.temperature = 0.7
    config.system_prompt = 'Test prompt'
    config.model = 'test_model'

    with patch('src.ollamaChat.OpenAI'):
        bot: OllamaBot = OllamaBot(config)
        bot.history = []

        bot.history.append({'role': 'user', 'content': 'Hello'})

        assert len(bot.history) == 1


def test_context_limit_messages() -> None:
    config = Mock()
    config.messages_limit = 3
    config.chars_limit = 1000
    config.temperature = 0.7
    config.system_prompt = ''
    config.api_host = 'http://test'
    config.api_key = 'test_key'
    config.model = 'test_model'

    with patch('src.ollamaChat.OpenAI'):
        bot = OllamaBot(config)

        for i in range(5):
            bot.history.append({'role': 'user', 'content': f'Msg{i}'})

        assert len(bot.history) == 5

        bot._check_limits()

        assert len(bot.history) <= 3


def test_reset() -> None:
    config = Mock()
    config.messages_limit = 5
    config.chars_limit = 1000
    config.api_host = 'http://test'
    config.api_key = 'test_key'
    config.model = 'test_model'

    with patch('src.ollamaChat.OpenAI'):
        bot = OllamaBot(config)
        bot.history.append({'role': 'user', 'content': 'Hello'})
        bot.history.append({'role': 'assistant', 'content': 'Hi'})

        assert len(bot.history) == 2

        bot.reset()

        assert len(bot.history) == 0
