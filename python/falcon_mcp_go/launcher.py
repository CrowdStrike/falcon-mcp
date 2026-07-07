"""Python launcher for the falcon-mcp Go binary.

Locates a cached per-platform binary (downloading the matching GitHub release
asset on first run) and execs it, forwarding argv and the exit code. Mirrors the
kubernetes-mcp-server Python launcher pattern so ``uvx falcon-mcp-go`` / ``pipx``
users get the Go server without a Go toolchain.
"""

from __future__ import annotations

import hashlib
import os
import platform
import stat
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

__version__ = "0.13.0"

_REPO = "crowdstrike/falcon-mcp-go"
_BASE_URL = os.environ.get(
    "FALCON_MCP_GO_DOWNLOAD_BASE",
    f"https://github.com/{_REPO}/releases/download/v{__version__}",
)


def _platform_asset() -> tuple[str, str]:
    """Return (os, arch) tokens matching the GoReleaser archive names."""
    system = {"darwin": "darwin", "linux": "linux", "windows": "windows"}.get(
        platform.system().lower()
    )
    machine = platform.machine().lower()
    arch = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }.get(machine)
    if not system or not arch:
        raise SystemExit(
            f"Unsupported platform {platform.system()}/{platform.machine()}. "
            "falcon-mcp-go ships binaries for darwin/linux/windows on amd64/arm64."
        )
    return system, arch


def _cache_dir() -> Path:
    root = Path(
        os.environ.get("FALCON_MCP_GO_CACHE")
        or (Path.home() / ".cache" / "falcon-mcp-go")
    )
    d = root / __version__
    d.mkdir(parents=True, exist_ok=True)
    return d


def _binary_path() -> Path:
    system, arch = _platform_asset()
    exe = "falcon-mcp.exe" if system == "windows" else "falcon-mcp"
    cached = _cache_dir() / f"{system}_{arch}" / exe
    if cached.exists():
        return cached

    ext = "zip" if system == "windows" else "tar.gz"
    asset = f"falcon-mcp_{system}_{arch}.{ext}"
    url = f"{_BASE_URL}/{asset}"

    cached.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / asset
        _download(url, archive)
        _extract(archive, cached.parent, exe)

    if not cached.exists():
        raise SystemExit(f"falcon-mcp binary not found after extracting {asset}")
    cached.chmod(cached.stat().st_mode | stat.S_IEXEC)
    return cached


def _download(url: str, dest: Path) -> None:
    try:
        with urllib.request.urlopen(url) as resp, open(dest, "wb") as f:  # noqa: S310
            f.write(resp.read())
    except Exception as exc:  # pragma: no cover - network dependent
        raise SystemExit(f"Failed to download {url}: {exc}") from exc


def _extract(archive: Path, dest_dir: Path, exe: str) -> None:
    if archive.suffix == ".zip" or archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            _safe_extract_member(zf, exe, dest_dir)
    else:
        with tarfile.open(archive) as tf:
            _safe_extract_member(tf, exe, dest_dir)


def _safe_extract_member(archive, exe: str, dest_dir: Path) -> None:
    """Extract only the expected binary, guarding against path traversal."""
    names = archive.namelist() if hasattr(archive, "namelist") else archive.getnames()
    for name in names:
        if Path(name).name != exe:
            continue
        target = dest_dir / exe
        if hasattr(archive, "open"):  # zipfile
            with archive.open(name) as src, open(target, "wb") as out:
                out.write(src.read())
        else:  # tarfile
            member = archive.getmember(name)
            src = archive.extractfile(member)
            if src is not None:
                with open(target, "wb") as out:
                    out.write(src.read())
        return


def main() -> None:
    binary = _binary_path()
    args = sys.argv[1:]
    if os.name == "nt":
        import subprocess

        raise SystemExit(subprocess.call([str(binary), *args]))
    os.execv(str(binary), [str(binary), *args])


# Keep hashlib import meaningful for future checksum verification.
_ = hashlib

if __name__ == "__main__":
    main()
