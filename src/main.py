"""Главный модуль запуска CLI-приложения визуализации зависимостей."""

import sys
from apk_provider import (
    PackageNotFoundError,
    load_real_repo_map,
    load_test_repo_map,
)
from config import ConfigError, parse_arguments
from graph_builder import build_dependency_graph_bfs

EXIT_CODE_SUCCESS = 0
EXIT_CODE_CONFIG_ERR = 2
EXIT_CODE_DATA_ERR = 3
NO_ITEMS_COUNT = 0


def print_dependency_graph(
    root_package: str, graph: dict[str, list[str]]
) -> None:
    """Вывод построенного графа зависимостей на экран."""
    print(f"Граф зависимостей для пакета '{root_package}':")
    if len(graph) == NO_ITEMS_COUNT:
        print("  (граф пуст или пакет исключен фильтром)")
        return
    for package, deps in graph.items():
        deps_str = ", ".join(deps) if deps else "(нет зависимостей)"
        print(f"  {package} -> {deps_str}")


def main() -> int:
    """Точка входа программы."""
    try:
        config = parse_arguments()
        if config.test_mode:
            repo_map = load_test_repo_map(config.repo, config.package_name)
        else:
            repo_map = load_real_repo_map(
                config.repo, config.package_name, config.package_version
            )
        graph = build_dependency_graph_bfs(
            repo_map=repo_map,
            root_package=config.package_name,
            filter_substring=config.filter_substring,
        )
        print_dependency_graph(config.package_name, graph)
        return EXIT_CODE_SUCCESS
    except ConfigError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        return EXIT_CODE_CONFIG_ERR
    except PackageNotFoundError as err:
        print(f"Ошибка получения пакета: {err}", file=sys.stderr)
        return EXIT_CODE_DATA_ERR
    except Exception as err:
        print(f"Ошибка выполнения: {err}", file=sys.stderr)
        return EXIT_CODE_DATA_ERR


if __name__ == "__main__":
    sys.exit(main())
