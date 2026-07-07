"""Download and execute the platform-appropriate falcon-mcp binary."""
import hashlib
import os
import platform
import signal
import stat
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen  # (WHY: module-level so tests can patch falcon_mcp.falcon_mcp.urlopen)

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("falcon-mcp")
except Exception:  # pragma: no cover - not installed as a dist (e.g. running from source)
    __version__ = "0.0.0"

_OS_MAP = {"darwin": "macos", "linux": "linux", "windows": "windows"}
_ARCH_MAP = {"x86_64": "x86_64", "amd64": "x86_64", "arm64": "arm64", "aarch64": "arm64"}


def platform_binary_name(system: str, machine: str, version: str) -> str:
    """Return the release binary filename for the given OS/arch/version."""
    os_key = system.lower()
    arch_key = machine.lower()
    if os_key not in _OS_MAP:
        raise RuntimeError(f"Unsupported operating system: {os_key}")
    if arch_key not in _ARCH_MAP:
        raise RuntimeError(f"Unsupported architecture: {arch_key}")
    suffix = ".exe" if os_key == "windows" else ""
    return f"falcon-mcp-{version}-{_OS_MAP[os_key]}-{_ARCH_MAP[arch_key]}{suffix}"


def current_binary_name(version: str) -> str:
    """Return the release binary filename for the running platform."""
    return platform_binary_name(platform.system(), platform.machine(), version)


_RELEASES = "https://github.com/crowdstrike/falcon-mcp/releases/download"


def _release_url(version: str, filename: str) -> str:
    return f"{_RELEASES}/v{version}/{filename}"


def _expected_digest(checksums_text: str, binary_name: str) -> str:
    for line in checksums_text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == binary_name:
            return parts[0]
    raise RuntimeError(f"no checksum entry for {binary_name}")


def download_binary(version: str, *, dest_dir=None, opener=urlopen, binary_name=None):
    """Download, verify (sha256), cache, and return the path to the binary."""
    if binary_name is None:
        binary_name = current_binary_name(version)
    if dest_dir is None:
        dest_dir = Path.home() / ".falcon-mcp" / "bin" / version
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    binary_path = dest_dir / binary_name
    if binary_path.exists():
        return binary_path

    with opener(_release_url(version, "checksums.txt")) as resp:
        checksums_text = resp.read().decode()
    expected = _expected_digest(checksums_text, binary_name)

    with opener(_release_url(version, binary_name)) as resp:
        data = resp.read()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise RuntimeError(
            f"checksum mismatch for {binary_name}: expected {expected}, got {actual}"
        )

    tmp = binary_path.with_suffix(binary_path.suffix + ".tmp")
    tmp.write_bytes(data)  # (WHY: write to temp then rename — no partial file on crash)
    tmp.chmod(tmp.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    os.replace(tmp, binary_path)
    return binary_path


def _default_runner(cmd):
    """Spawn cmd, forward termination signals to the child, return its exit code."""
    process = subprocess.Popen(cmd)  # (WHY: Popen not run() — need the handle to forward signals)

    def handle_signal(signum, _frame):
        try:
            process.send_signal(signum)
        except OSError:
            pass

    signal.signal(signal.SIGTERM, handle_signal)
    if hasattr(signal, "SIGHUP"):  # (WHY: SIGHUP absent on Windows)
        signal.signal(signal.SIGHUP, handle_signal)
    try:
        return process.wait()
    except KeyboardInterrupt:
        try:
            process.send_signal(signal.SIGINT)
        except OSError:
            pass
        return process.wait()


def execute(args=None, *, runner=_default_runner):
    """Download (if needed) and run the falcon-mcp binary, returning its exit code."""
    if args is None:
        args = []
    try:
        binary_path = download_binary(__version__)
        return runner([str(binary_path)] + list(args))
    except Exception as exc:  # noqa: BLE001 - top-level guard, message to stderr
        print(f"Error executing falcon-mcp: {exc}", file=sys.stderr)
        return 1


def main():
    """Entry point: run the binary with args from the command line."""
    return execute(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
