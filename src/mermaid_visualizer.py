"""Модуль формирования представления графа зависимостей на языке Mermaid."""

EMPTY_GRAPH_SIZE = 0


def _get_or_create_node_id(
    package_name: str, node_ids: dict[str, str], lines: list[str]
) -> str:
    """Получение безопасного идентификатора узла Mermaid и объявление метки."""
    if package_name not in node_ids:
        node_id = f"node_{len(node_ids)}"
        node_ids[package_name] = node_id
        safe_label = package_name.replace('"', "'")
        lines.append(f'    {node_id}["{safe_label}"]')
    return node_ids[package_name]


def generate_mermaid_diagram(graph: dict[str, list[str]]) -> str:
    """Генерация текстового описания графа на языке диаграмм Mermaid."""
    lines: list[str] = ["graph TD"]
    if len(graph) == EMPTY_GRAPH_SIZE:
        lines.append('    empty["Граф зависимостей пуст"]')
        return "\n".join(lines)

    node_ids: dict[str, str] = {}
    edges: list[str] = []

    for package, deps in graph.items():
        src_id = _get_or_create_node_id(package, node_ids, lines)
        for dep in deps:
            dst_id = _get_or_create_node_id(dep, node_ids, lines)
            edges.append(f"    {src_id} --> {dst_id}")

    lines.extend(edges)
    return "\n".join(lines)
