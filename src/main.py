"""Главный модуль запуска CLI-приложения визуализации зависимостей."""

import sys
from apk_provider import (
    PackageNotFoundError,
    load_real_repo_map,
    load_test_repo_map,
)
from config import ConfigError, parse_arguments
from graph_builder import build_dependency_graph_bfs, compute_load_order
from mermaid_visualizer import generate_mermaid_diagram

EXIT_CODE_SUCCESS = 0
EXIT_CODE_CONFIG_ERR = 2
EXIT_CODE_DATA_ERR = 3
NO_ITEMS_COUNT = 0
FIRST_STEP_NUM = 1


def print_load_order(root_package: str, order: list[str]) -> None:
    """Вывод порядка загрузки зависимостей на экран."""
    print(f"Порядок загрузки зависимостей для пакета '{root_package}':")
    if len(order) == NO_ITEMS_COUNT:
        print("  (список загрузки пуст)")
        return
    for idx, pkg in enumerate(order, start=FIRST_STEP_NUM):
        print(f"  {idx}. {pkg}")


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
        if config.load_order:
            order = compute_load_order(graph, config.package_name)
            print_load_order(config.package_name, order)
        else:
            print(generate_mermaid_diagram(graph))
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
