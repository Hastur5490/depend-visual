"""Тестирование парсера репозитория пакетов Alpine Linux."""

import unittest
from src.apk_provider import PackageNotFoundError, parse_apkindex_content

SAMPLE_APKINDEX = """P:musl
V:1.2.5-r0
D:
S:412340

P:curl
V:8.8.0-r0
D:ca-certificates libbrotlidec libcurl=8.8.0-r0 musl>=1.2.5 zlib
S:152340

P:curl
V:8.7.1-r0
D:musl zlib
S:150000
"""

EXPECTED_CURL_DEPS_COUNT = 5
EMPTY_DEPS_COUNT = 0


class TestApkProvider(unittest.TestCase):
    """Проверка извлечения прямых зависимостей пакетов."""

    def test_extract_direct_dependencies(self) -> None:
        """Проверка корректного извлечения и очистки зависимостей."""
        deps = parse_apkindex_content(SAMPLE_APKINDEX, "curl", "8.8.0-r0")
        self.assertEqual(len(deps), EXPECTED_CURL_DEPS_COUNT)
        self.assertIn("ca-certificates", deps)
        self.assertIn("libbrotlidec", deps)
        self.assertIn("libcurl", deps)
        self.assertIn("musl", deps)
        self.assertIn("zlib", deps)

    def test_package_without_dependencies(self) -> None:
        """Проверка пакета с пустым списком зависимостей."""
        deps = parse_apkindex_content(SAMPLE_APKINDEX, "musl", "1.2.5-r0")
        self.assertEqual(len(deps), EMPTY_DEPS_COUNT)

    def test_package_not_found_raises(self) -> None:
        """Проверка генерации ошибки, если пакет или версия не найдены."""
        with self.assertRaises(PackageNotFoundError):
            parse_apkindex_content(SAMPLE_APKINDEX, "curl", "9.9.9")


if __name__ == "__main__":
    unittest.main()