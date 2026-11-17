"""Модуль построения графа зависимостей алгоритмом BFS без рекурсии."""

from collections import deque

EMPTY_STR_LEN = 0


def _is_filtered(package_name: str, filter_substring: str) -> bool:
    """Проверка, содержит ли имя пакета запрещенную подстроку."""
    if len(filter_substring) == EMPTY_STR_LEN:
        return False
    return filter_substring in package_name


def build_dependency_graph_bfs(
    repo_map: dict[str, list[str]],
    root_package: str,
    filter_substring: str = "",
) -> dict[str, list[str]]:
    """Построение графа зависимостей с помощью BFS без рекурсии."""
    graph: dict[str, list[str]] = {}
    if _is_filtered(root_package, filter_substring):
        return graph

    visited: set[str] = {root_package}
    queue: deque[str] = deque([root_package])

    while queue:
        current = queue.popleft()
        raw_deps = repo_map.get(current, [])
        filtered_deps: list[str] = []

        for dep in raw_deps:
            if _is_filtered(dep, filter_substring):
                continue
            if dep not in filtered_deps:
                filtered_deps.append(dep)
            if dep not in visited:
                visited.add(dep)
                queue.append(dep)

        graph[current] = filtered_deps

    return graph
