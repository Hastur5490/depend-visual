"""Главный модуль запуска CLI-приложения визуализации зависимостей."""

import sys
from config import ConfigError, parse_arguments
from apk_provider import PackageNotFoundError, get_apk_dependencies

EXIT_CODE_SUCCESS = 0
EXIT_CODE_CONFIG_ERR = 2
EXIT_CODE_DATA_ERR = 3
NO_ITEMS_COUNT = 0


def print_dependencies(package: str, version: str, deps: list[str]) -> None:
    """Вывод прямых зависимостей пакета на экран."""
    print(f"Прямые зависимости пакета {package} ({version}):")
    if len(deps) == NO_ITEMS_COUNT:
        print("  (зависимости отсутствуют)")
        return
    for item in deps:
        print(f"  - {item}")


def main() -> int:
    """Точка входа программы."""
    try:
        config = parse_arguments()
        deps = get_apk_dependencies(
            repo_source=config.repo,
            package_name=config.package_name,
            package_version=config.package_version,
        )
        print_dependencies(
            package=config.package_name,
            version=config.package_version,
            deps=deps,
        )
        return EXIT_CODE_SUCCESS
    except ConfigError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        return EXIT_CODE_CONFIG_ERR
    except PackageNotFoundError as err:
        print(f"Ошибка получения пакета: {err}", file=sys.stderr)
        return EXIT_CODE_DATA_ERR
    except Exception as err:
        print(f"Ошибка при работе с репозиторием: {err}", file=sys.stderr)
        return EXIT_CODE_DATA_ERR


if __name__ == "__main__":
    sys.exit(main())