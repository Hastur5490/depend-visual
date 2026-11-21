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
    """Исключение, если пакет или версия не найдены в репозитории."""


def _clean_dependency_name(dep_token: str) -> str:
    """Очистка зависимости от версионных ограничений и префиксов."""
    token = dep_token.strip()
    for operator in ("=", ">=", "<=", ">", "<", "~"):
        if operator in token:
            token = token.split(operator)[EMPTY_PARTS_COUNT]
            break
    return token.strip()


def _match_version(actual: str, target: str) -> bool:
    """Проверка совпадения версии: точное или без учета ревизии."""
    if actual == target:
        return True
    return actual.startswith(f"{target}-r") or actual.startswith(target)


def _extract_record_data(record: str) -> tuple[str, str, list[str]]:
    """Извлечение имени, версии и списка зависимостей из блока записи."""
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
    return pkg_name, pkg_ver, raw_deps


def _sanitize_deps(raw_deps: list[str]) -> list[str]:
    """Очистка и фильтрация непустых имен зависимостей."""
    result: list[str] = []
    for token in raw_deps:
        cleaned = _clean_dependency_name(token)
        if len(cleaned) > EMPTY_PARTS_COUNT:
            result.append(cleaned)
    return result


def parse_apkindex_content(content: str, name: str, version: str) -> list[str]:
    """Поиск пакета заданной версии в тексте APKINDEX и сбор зависимостей."""
    found_versions: list[str] = []
    for record in content.split("\n\n"):
        pkg_name, pkg_ver, raw_deps = _extract_record_data(record)
        if pkg_name != name:
            continue
        found_versions.append(pkg_ver)
        if _match_version(pkg_ver, version):
            return _sanitize_deps(raw_deps)

    if len(found_versions) > EMPTY_PARTS_COUNT:
        available = ", ".join(found_versions)
        raise PackageNotFoundError(
            f"Версия '{version}' для пакета '{name}' не найдена. "
            f"Доступные версии: {available}"
        )
    raise PackageNotFoundError(f"Пакет '{name}' не найден в индексе.")


def _build_repo_url(repo_source: str) -> str:
    """Формирование полного URL до архива APKINDEX.tar.gz."""
    target_url = repo_source.rstrip("/")
    if target_url.endswith(INDEX_ARCHIVE_NAME):
        return target_url
    if DEFAULT_ARCH not in target_url:
        target_url = f"{target_url}/{DEFAULT_ARCH}"
    return f"{target_url}/{INDEX_ARCHIVE_NAME}"


def _load_bytes_from_source(repo_source: str) -> bytes:
    """Получение байтов APKINDEX.tar.gz из HTTP/HTTPS URL или файла."""
    parsed = urlparse(repo_source)
    if parsed.scheme in ("http", "https"):
        req = urllib.request.Request(
            _build_repo_url(repo_source),
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
                f"Файл {INDEX_FILE_NAME} отсутствует в архиве."
            )
        text_content = member.read().decode("utf-8", errors="replace")

    return parse_apkindex_content(text_content, package_name, package_version)