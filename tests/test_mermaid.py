"""Тестирование генерации диаграмм на языке Mermaid."""

import unittest
from src.mermaid_visualizer import generate_mermaid_diagram


class TestMermaidVisualizer(unittest.TestCase):
    """Проверка корректности формирования синтаксиса Mermaid."""

    def test_generate_mermaid_for_simple_graph(self) -> None:
        """Проверка генерации узлов и ребер Mermaid."""
        graph = {
            "curl": ["libcurl", "so:libz.so.1"],
            "libcurl": [],
            "so:libz.so.1": [],
        }
        diagram = generate_mermaid_diagram(graph)
        lines = diagram.splitlines()
        self.assertEqual(lines[0], "graph TD")
        self.assertIn('    node_0["curl"]', lines)
        self.assertIn('    node_1["libcurl"]', lines)
        self.assertIn('    node_2["so:libz.so.1"]', lines)
        self.assertIn("    node_0 --> node_1", lines)
        self.assertIn("    node_0 --> node_2", lines)

    def test_generate_mermaid_empty_graph(self) -> None:
        """Проверка вывода при пустом графе зависимостей."""
        diagram = generate_mermaid_diagram({})
        self.assertIn("graph TD", diagram)
        self.assertIn("Граф зависимостей пуст", diagram)


if __name__ == "__main__":
    unittest.main()
