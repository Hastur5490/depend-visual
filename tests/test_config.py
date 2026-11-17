"""Тесты валидации параметров командной строки."""

import tempfile
import unittest

from src.config import ConfigError, parse_arguments, validate_config


class TestConfigValidation(unittest.TestCase):
    """Набор тестов для проверки обработки ошибок параметров."""

    def test_successful_real_repo_config(self) -> None:
        """Проверка успешной конфигурации для реального репозитория."""
        cfg = validate_config(
            package_name="curl",
            repo="https://dl-cdn.alpinelinux.org/alpine/v3.20/main",
            test_mode=False,
            package_version="8.8.0-r0",
            filter_substring="lib",
        )
        self.assertEqual(cfg.package_name, "curl")
        self.assertFalse(cfg.test_mode)
        self.assertEqual(cfg.filter_substring, "lib")

    def test_successful_test_repo_config(self) -> None:
        """Проверка успешной конфигурации для тестового репозитория."""
        with tempfile.NamedTemporaryFile() as tmp:
            cfg = validate_config(
                package_name="A",
                repo=tmp.name,
                test_mode=True,
                package_version="1.0.0",
                filter_substring="",
            )
            self.assertTrue(cfg.test_mode)
            self.assertEqual(cfg.repo, tmp.name)

    def test_empty_package_name_error(self) -> None:
        """Демонстрация ошибки: пустое имя пакета."""
        with self.assertRaises(ConfigError):
            validate_config(
                package_name="   ",
                repo="https://example.com",
                test_mode=False,
                package_version="1.0",
                filter_substring="",
            )

    def test_empty_package_version_error(self) -> None:
        """Демонстрация ошибки: пустая версия пакета."""
        with self.assertRaises(ConfigError):
            validate_config(
                package_name="bash",
                repo="https://example.com",
                test_mode=False,
                package_version="  ",
                filter_substring="",
            )

    def test_invalid_url_for_real_mode_error(self) -> None:
        """Демонстрация ошибки: некорректный URL в обычном режиме."""
        with self.assertRaises(ConfigError):
            validate_config(
                package_name="bash",
                repo="not_a_valid_url",
                test_mode=False,
                package_version="1.0",
                filter_substring="",
            )

    def test_missing_file_for_test_mode_error(self) -> None:
        """Демонстрация ошибки: несуществующий файл в тестовом режиме."""
        with self.assertRaises(ConfigError):
            validate_config(
                package_name="A",
                repo="/nonexistent/test_graph.txt",
                test_mode=True,
                package_version="1.0",
                filter_substring="",
            )

    def test_cli_parsing_helper(self) -> None:
        """Проверка работы функции parse_arguments с CLI флагами."""
        args = [
            "--package",
            "musl",
            "--repo",
            "https://alpinelinux.org/repo",
            "--version",
            "1.2.5",
            "--filter",
            "dev",
        ]
        cfg = parse_arguments(args)
        self.assertEqual(cfg.package_name, "musl")
        self.assertEqual(cfg.package_version, "1.2.5")
        self.assertEqual(cfg.filter_substring, "dev")


if __name__ == "__main__":
    unittest.main()
