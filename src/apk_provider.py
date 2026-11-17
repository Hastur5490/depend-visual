"""Модуль загрузки и парсинга зависимостей пакетов Alpine Linux и тестов."""

import io
import tarfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

INDEX_ARCHIVE_NAME = "APKINDEX.tar.gz"
INDEX_FILE_NAME = "APKINDEX"
DEFAULT_ARCH = "x86_64"
REQ_TIMEOUT_SEC = 15
EMPTY_COUNT = 0
PREFIX_LEN = 2
TEST_LINE_PARTS = 2


class PackageNotFoundError(ValueError):
    """Исключение при отсутствии пакета или версии в репозитории."""


def _clean_dependency_name(dep_token: str) -> str:
    """Очистка имени зависимости от операторов сравнения версий."""
    token = dep_token.strip()
    for operator in ("=", ">=", "<=", ">", "<", "~"):
        if operator in token:
            token = token.split(operator)[EMPTY_COUNT]
            break
    return token.strip()


def _match_version(actual: str, target: str) -> bool:
    """Проверка совпадения версии пакета."""
    if actual == target:
        return True
    if actual.startswith(f"{target}-r") or actual.startswith(target):
        return True
    return False


def _parse_record(record: str) -> tuple[str, str, list[str]]:
    """Разбор одной записи блока APKINDEX."""
    pkg_name = ""
    pkg_ver = ""
    raw_deps: list[str] = []
    for line in record.splitlines():
        if line.startswith("P:"):
            pkg_name = line[PREFIX_LEN:].strip()
        elif line.startswith("V:"):
            pkg_ver = line[PREFIX_LEN:].strip()
        elif line.startswith("D:"):
            raw_deps = line[PREFIX_LEN:].strip().split()
    cleaned = [_clean_dependency_name(d) for d in raw_deps if d]
    deps = [d for d in cleaned if len(d) > EMPTY_COUNT]
    return pkg_name, pkg_ver, deps


def build_apk_index_map(
    content: str, root_name: str, root_version: str
) -> dict[str, list[str]]:
    """Построение словаря зависимостей из содержимого файла APKINDEX."""
    index_map: dict[str, list[str]] = {}
    root_found = False

    for record in content.split("\n\n"):
        pkg_name, pkg_ver, deps = _parse_record(record)
        if not pkg_name:
            continue
        if pkg_name == root_name and _match_version(pkg_ver, root_version):
            index_map[pkg_name] = deps
            root_found = True
        elif pkg_name not in index_map:
            index_map[pkg_name] = deps

    if not root_found:
        raise PackageNotFoundError(
            f"Пакет '{root_name}' версии '{root_version}' не найден."
        )
    return index_map


def _load_bytes_from_source(repo_source: str) -> bytes:
    """Загрузка байтов APKINDEX.tar.gz по URL или локальному пути."""
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


def load_real_repo_map(
    repo_source: str, root_name: str, root_version: str
) -> dict[str, list[str]]:
    """Загрузка и парсинг реального репозитория Alpine Linux."""
    archive_data = _load_bytes_from_source(repo_source)
    with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as tar:
        member = tar.extractfile(INDEX_FILE_NAME)
        if member is None:
            raise PackageNotFoundError(
                f"Файл {INDEX_FILE_NAME} отсутствует в архиве."
            )
        text_content = member.read().decode("utf-8", errors="replace")
    return build_apk_index_map(text_content, root_name, root_version)


def load_test_repo_map(
    file_path: str, root_name: str
) -> dict[str, list[str]]:
    """Загрузка графа зависимостей из файла тестового репозитория."""
    repo_map: dict[str, list[str]] = {}
    with open(file_path, "r", encoding="utf-8") as file_stream:
        for raw_line in file_stream:
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            parts = line.split(":", maxsplit=1)
            if len(parts) != TEST_LINE_PARTS:
                continue
            pkg = parts[EMPTY_COUNT].strip()
            deps = [d.strip() for d in parts[1].split() if d.strip()]
            repo_map[pkg] = deps

    if root_name not in repo_map:
        raise PackageNotFoundError(
            f"Пакет '{root_name}' не найден в тестовом репозитории."
        )
    return repo_map
