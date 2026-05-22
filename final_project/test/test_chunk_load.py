from unittest.mock import Mock, patch
from typing import Any
from pathlib import Path

from src.chunk_load import process_file_in_chunks
from src.ollamaChat import OllamaBot


def test_process_file_in_chunks_paragraph_success(tmp_path: Any) -> None:
    test_file: Path = tmp_path / 'test.txt'
    test_file.write_text('Сила\n\nв\n\nправде', encoding='utf-8')

    bot: Mock = Mock(spec=OllamaBot)
    bot.send_message_sync = Mock(return_value='Ответ модели')

    result = process_file_in_chunks(
        bot=bot,
        filepath=str(test_file),
        prompt='Суммаризируй',
        chunk_method='paragraph',
        chunk_value=1,
        confirm=True,
    )

    assert result is True
    assert bot.send_message_sync.call_count == 3


def test_process_file_in_chunks_file_not_found() -> None:
    bot = Mock(spec=OllamaBot)

    result = process_file_in_chunks(
        bot=bot,
        filepath='no.txt',
        prompt='Prompt',
        chunk_method='paragraph',
        chunk_value=1,
        confirm=True,
    )

    assert result is False


def test_process_file_in_chunks_empty_file(tmp_path: Any) -> None:
    test_file = tmp_path / 'empty.txt'
    test_file.write_text('', encoding='utf-8')

    bot = Mock(spec=OllamaBot)

    result = process_file_in_chunks(
        bot=bot,
        filepath=str(test_file),
        prompt='Prompt',
        chunk_method='paragraph',
        chunk_value=1,
        confirm=True,
    )

    assert result is False


def test_process_file_in_chunks_api_error(tmp_path: Any) -> None:
    test_file = tmp_path / 'test.txt'
    test_file.write_text('Доучились не только.\n\nлишь все', encoding='utf-8')

    bot = Mock(spec=OllamaBot)
    bot.send_message_sync = Mock(side_effect=Exception('API Error'))

    with patch('builtins.print') as mock_print:
        result = process_file_in_chunks(
            bot=bot,
            filepath=str(test_file),
            prompt='Prompt',
            chunk_method='paragraph',
            chunk_value=1,
            confirm=True,
        )

        assert result is False
        error_calls = [str(call) for call in mock_print.call_args_list]
        assert any('Ошибка при обработке чанка' in call for call in error_calls)


def test_process_file_in_chunks_len_mode(tmp_path: Any) -> None:
    test_file = tmp_path / 'long.txt'
    test_file.write_text('MIPT' * 500, encoding='utf-8')

    bot = Mock(spec=OllamaBot)
    bot.send_message_sync = Mock(return_value='Ответ')

    result = process_file_in_chunks(
        bot=bot,
        filepath=str(test_file),
        prompt='Prompt',
        chunk_method='len',
        chunk_value=100,
        confirm=True,
    )

    assert result is True
    assert bot.send_message_sync.call_count == 20