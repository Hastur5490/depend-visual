"""Тестирование построения графа зависимостей и порядка загрузки."""

import unittest
from src.graph_builder import build_dependency_graph_bfs, compute_load_order


class TestGraphBuilderAndLoadOrder(unittest.TestCase):
    """Проверка BFS-обхода, циклов, фильтрации и порядка загрузки."""

    def test_transitive_bfs_graph(self) -> None:
        """Проверка транзитивного построения графа."""
        repo = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": [],
            "E": [],
        }
        graph = build_dependency_graph_bfs(repo, "A")
        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D", "E"])

    def test_cyclic_dependencies_handled(self) -> None:
        """Проверка отсутствия зацикливания на циклических зависимостях."""
        repo = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        graph = build_dependency_graph_bfs(repo, "A")
        self.assertEqual(graph["A"], ["B"])
        self.assertEqual(graph["B"], ["C"])
        self.assertEqual(graph["C"], ["A"])

    def test_filter_substring_excludes_branch(self) -> None:
        """Проверка исключения пакетов по подстроке."""
        repo = {
            "A": ["B_SKIP", "C"],
            "B_SKIP": ["D"],
            "C": ["E"],
            "D": [],
            "E": [],
        }
        graph = build_dependency_graph_bfs(repo, "A", filter_substring="SKIP")
        self.assertEqual(graph["A"], ["C"])
        self.assertNotIn("B_SKIP", graph)
        self.assertNotIn("D", graph)

    def test_load_order_dependencies_before_dependents(self) -> None:
        """Проверка того, что зависимости загружаются раньше пакета."""
        repo = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": [],
            "E": [],
        }
        graph = build_dependency_graph_bfs(repo, "A")
        order = compute_load_order(graph, "A")
        self.assertEqual(order[-1], "A")
        self.assertLess(order.index("D"), order.index("B"))
        self.assertLess(order.index("D"), order.index("C"))
        self.assertLess(order.index("E"), order.index("C"))

    def test_load_order_with_cycle(self) -> None:
        """Проверка построения порядка загрузки при наличии цикла."""
        repo = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        graph = build_dependency_graph_bfs(repo, "A")
        order = compute_load_order(graph, "A")
        self.assertEqual(set(order), {"A", "B", "C"})
        self.assertEqual(order[-1], "A")


if __name__ == "__main__":
    unittest.main()
