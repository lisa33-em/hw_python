import sys

from src.config import Config
from src.ollamaChat import OllamaBot
from src.file_handler import replace_placeholders, parse_chunk_command
from src.chunk_load import process_file_in_chunks


def main() -> int:
    try:
        config = Config()
    except ValueError as e:
        print(f'Ошибка конфигурации: {e}')
        return 1

    bot = OllamaBot(config)
    print('ИИ-ассистент запущен')

    while True:
        try:
            user_input = input('\nВы: ').strip()

            if not user_input:
                continue

            if user_input == '\\q':
                print('До свидания')
                break

            if user_input == '/reset':
                bot.reset()
                print('Чат очищен')
                continue

            if user_input.startswith('/file_chunk'):
                args = user_input[len('/file_chunk') :].strip()
                method, value, auto = parse_chunk_command(args)

                filepath = input('Путь к файлу: ').strip()
                if not filepath:
                    print('Путь не указан.')
                    continue

                prompt = input('Задайте правила работы с каждым фрагментом? ').strip()
                if not prompt:
                    print('Промпт нет.')
                    continue

                process_file_in_chunks(
                    bot=bot,
                    filepath=filepath,
                    prompt=prompt,
                    chunk_method=method,
                    chunk_value=value,
                    confirm=auto,
                )
                continue

            processed_input = replace_placeholders(user_input)

            print('Бот: ', end='', flush=True)

            try:
                for chunk in bot.send_message_streaming(processed_input):
                    print(chunk, end='', flush=True)
                print()
            except KeyboardInterrupt:
                print('\n[Прервано пользователем]')
                continue

        except Exception as e:
            print(f'\nОшибка: {e}')
            print('Продолжаем работу...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
