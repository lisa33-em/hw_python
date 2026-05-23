from src.file_handler import (
    replace_placeholders,
    split_by_paragraphs,
    split_by_length,
    parse_chunk_command,
)


def test_replace_file_not_found() -> None:
    result = replace_placeholders('Файл @::/nonexistent.txt::')
    assert 'Ошибка' in result


def test_split_by_paragraphs() -> None:
    content = 'Раздели\n\nпо\n\nабзацам'
    chunks = split_by_paragraphs(content, 1)
    assert len(chunks) == 3


def test_split_by_paragraphs_grouped() -> None:
    content = 'ааа\n\nббб\n\nввв\n\ггг'
    chunks = split_by_paragraphs(content, 2)
    assert len(chunks) == 2


def test_split_by_length() -> None:
    content = 'ш' * 500
    chunks = split_by_length(content, 100)
    assert 5 <= len(chunks) <= 6


def test_parse_chunk_command() -> None:
    method, value, auto = parse_chunk_command('paragraph=3')
    assert method == 'paragraph'
    assert value == 3
    assert auto is False

    method, value, auto = parse_chunk_command('len=200 -y')
    assert method == 'len'
    assert value == 200
    assert auto is True

    method, value, auto = parse_chunk_command('-y')
    assert method == 'paragraph'
    assert value == 1
    assert auto is True
