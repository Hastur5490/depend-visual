"""Модуль парсинга и валидации параметров конфигурации CLI."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

MIN_STR_LEN = 1


class ConfigError(ValueError):
    """Исключение при некорректных параметрах конфигурации."""


@dataclass(frozen=True)
class AppConfig:
    """Хранилище валидированных параметров приложения."""

    package_name: str
    repo: str
    test_mode: bool
    package_version: str
    filter_substring: str

    def to_dict(self) -> dict[str, str]:
        """Преобразование параметров в словарь для вывода."""
        return {
            "package_name": self.package_name,
            "repo": self.repo,
            "test_mode": str(self.test_mode),
            "package_version": self.package_version,
            "filter_substring": self.filter_substring,
        }


def _validate_package_name(name: str) -> None:
    """Проверка корректности имени пакета."""
    if not name or len(name.strip()) < MIN_STR_LEN:
        raise ConfigError("Имя пакета не может быть пустым.")


def _validate_package_version(version: str) -> None:
    """Проверка корректности версии пакета."""
    if not version or len(version.strip()) < MIN_STR_LEN:
        raise ConfigError("Версия пакета не может быть пустой.")


def _validate_repo(repo: str, test_mode: bool) -> None:
    """Проверка адреса репозитория или пути к тестовому файлу."""
    if not repo or len(repo.strip()) < MIN_STR_LEN:
        raise ConfigError("Адрес репозитория/путь не может быть пустым.")
    if test_mode:
        path = Path(repo)
        if not path.is_file():
            raise ConfigError(
                f"Файл тестового репозитория не найден: {repo}"
            )
    else:
        parsed = urlparse(repo)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ConfigError(
                "Для реального репозитория требуется валидный HTTP/HTTPS URL."
            )


def validate_config(
    package_name: str,
    repo: str,
    test_mode: bool,
    package_version: str,
    filter_substring: str,
) -> AppConfig:
    """Валидация всех переданных параметров."""
    _validate_package_name(package_name)
    _validate_package_version(package_version)
    _validate_repo(repo, test_mode)
    return AppConfig(
        package_name=package_name.strip(),
        repo=repo.strip(),
        test_mode=test_mode,
        package_version=package_version.strip(),
        filter_substring=filter_substring,
    )


def create_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов."
    )
    parser.add_argument(
        "-p", "--package", required=True, help="Имя анализируемого пакета"
    )
    parser.add_argument(
        "-r",
        "--repo",
        required=True,
        help="URL репозитория или путь к файлу тестового графа",
    )
    parser.add_argument(
        "-t",
        "--test-mode",
        action="store_true",
        default=False,
        help="Режим работы с тестовым репозиторием",
    )
    parser.add_argument(
        "-v", "--version", required=True, help="Версия пакета"
    )
    parser.add_argument(
        "-f",
        "--filter",
        default="",
        help="Подстрока для фильтрации пакетов",
    )
    return parser


def parse_arguments(args: list[str] | None = None) -> AppConfig:
    """Разбор аргументов командной строки и валидация параметров."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    return validate_config(
        package_name=parsed_args.package,
        repo=parsed_args.repo,
        test_mode=parsed_args.test_mode,
        package_version=parsed_args.version,
        filter_substring=parsed_args.filter,
    )