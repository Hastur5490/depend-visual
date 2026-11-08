"""Модуль загрузки и парсинга зависимостей пакетов Alpine Linux (apk)."""

import io
import tarfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

INDEX_ARCHIVE_NAME = "APKINDEX.tar.gz"
INDEX_FILE_NAME = "APKINDEX"
DEFAULT_ARCH = "x86_64"
REQ_TIMEOUT_SEC = 15
EMPTY_PARTS_COUNT = 0
DEPENDENCY_PREFIX_LEN = 2


class PackageNotFoundError(ValueError):
    """Исключение, если пакет или указанная версия не найдены в репозитории."""


def _clean_dependency_name(dep_token: str) -> str:
    """Очистка зависимости от версионных ограничений и префиксов."""
    token = dep_token.strip()
    for operator in ("=", ">=", "<=", ">", "<", "~"):
        if operator in token:
            token = token.split(operator)[EMPTY_PARTS_COUNT]
            break
    return token.strip()


def _match_version(actual: str, target: str) -> bool:
    """Проверка совпадения версии: точное или без учета суффикса ревизии."""
    if actual == target:
        return True
    if actual.startswith(f"{target}-r") or actual.startswith(target):
        return True
    return False


def parse_apkindex_content(content: str, name: str, version: str) -> list[str]:
    """Поиск пакета заданной версии в тексте APKINDEX и сбор зависимостей."""
    records = content.split("\n\n")
    found_versions: list[str] = []

    for record in records:
        pkg_name = ""
        pkg_ver = ""
        raw_deps: list[str] = []
        for line in record.splitlines():
            if line.startswith("P:"):
                pkg_name = line[DEPENDENCY_PREFIX_LEN:].strip()
            elif line.startswith("V:"):
                pkg_ver = line[DEPENDENCY_PREFIX_LEN:].strip()
            elif line.startswith("D:"):
                raw_deps = line[DEPENDENCY_PREFIX_LEN:].strip().split()

        if pkg_name == name:
            found_versions.append(pkg_ver)
            if _match_version(pkg_ver, version):
                cleaned = [_clean_dependency_name(d) for d in raw_deps if d]
                return [d for d in cleaned if len(d) > EMPTY_PARTS_COUNT]

    if len(found_versions) > EMPTY_PARTS_COUNT:
        available = ", ".join(found_versions)
        raise PackageNotFoundError(
            f"Версия '{version}' для пакета '{name}' не найдена. "
            f"Доступные версии в репозитории: {available}"
        )

    raise PackageNotFoundError(
        f"Пакет '{name}' не найден в индексе репозитория."
    )


def _load_bytes_from_source(repo_source: str) -> bytes:
    """Получение байтов APKINDEX.tar.gz из HTTP/HTTPS URL или локального файла."""
    parsed = urlparse(repo_source)
    if parsed.scheme in ("http", "https"):
        target_url = repo_source.rstrip("/")
        if not target_url.endswith(INDEX_ARCHIVE_NAME):
            if DEFAULT_ARCH not in target_url:
                target_url = f"{target_url}/{DEFAULT_ARCH}"
            target_url = f"{target_url}/{INDEX_ARCHIVE_NAME}"

        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "DependencyVisualizer/1.0"},
        )
        with urllib.request.urlopen(req, timeout=REQ_TIMEOUT_SEC) as resp:
            return resp.read()

    path = Path(repo_source)
    if path.is_dir():
        path = path / INDEX_ARCHIVE_NAME
    with open(path, "rb") as file_stream:
        return file_stream.read()


def get_apk_dependencies(
    repo_source: str, package_name: str, package_version: str
) -> list[str]:
    """Извлечение прямых зависимостей пакета Alpine Linux."""
    archive_data = _load_bytes_from_source(repo_source)
    with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as tar:
        member = tar.extractfile(INDEX_FILE_NAME)
        if member is None:
            raise PackageNotFoundError(
                f"Файл {INDEX_FILE_NAME} отсутствует в архиве репозитория."
            )
        text_content = member.read().decode("utf-8", errors="replace")

    return parse_apkindex_content(text_content, package_name, package_version)