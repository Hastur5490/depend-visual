"""Тестирование построения графа зависимостей алгоритмом BFS."""

import unittest
from src.graph_builder import build_dependency_graph_bfs


class TestGraphBuilderBfs(unittest.TestCase):
    """Проверка BFS-обхода, циклов и фильтрации пакетов."""

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


if __name__ == "__main__":
    unittest.main()
