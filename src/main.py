"""Главный модуль запуска CLI-приложения визуализации зависимостей."""

import sys
from config import ConfigError, parse_arguments


def print_config(config_dict: dict[str, str]) -> None:
    """Вывод параметров конфигурации в формате ключ-значение."""
    for key, value in config_dict.items():
        print(f"{key}: {value}")


def main() -> int:
    """Точка входа программы."""
    try:
        config = parse_arguments()
        print_config(config.to_dict())
        return 0
    except ConfigError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        return 2
    except SystemExit as err:
        return int(err.code)


if __name__ == "__main__":
    sys.exit(main())