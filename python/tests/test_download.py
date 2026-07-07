import hashlib
import io
from pathlib import Path

import pytest
from falcon_mcp.falcon_mcp import download_binary

BIN = b"fake-binary-contents"
DIGEST = hashlib.sha256(BIN).hexdigest()

def make_opener(binary_bytes, checksum_line):
    """Return an opener(url) -> context manager yielding .read() bytes, by URL suffix."""
    calls = {"count": 0}
    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            self.close()
            return False
    def opener(url):
        calls["count"] += 1
        if url.endswith("checksums.txt"):
            return _Resp(checksum_line.encode())
        return _Resp(binary_bytes)
    opener.calls = calls
    return opener

def test_download_verifies_and_caches(tmp_path):
    name = "falcon-mcp-1.2.3-linux-x86_64"
    opener = make_opener(BIN, f"{DIGEST}  {name}\n")
    path = download_binary("1.2.3", dest_dir=tmp_path, opener=opener,
                           binary_name=name)
    assert Path(path).read_bytes() == BIN
    assert Path(path).stat().st_mode & 0o111  # executable bit set

def test_cache_hit_skips_network(tmp_path):
    name = "falcon-mcp-1.2.3-linux-x86_64"
    (tmp_path / name).write_bytes(BIN)
    opener = make_opener(BIN, f"{DIGEST}  {name}\n")
    download_binary("1.2.3", dest_dir=tmp_path, opener=opener, binary_name=name)
    assert opener.calls["count"] == 0

def test_checksum_mismatch(tmp_path):
    name = "falcon-mcp-1.2.3-linux-x86_64"
    opener = make_opener(BIN, f"{'0'*64}  {name}\n")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        download_binary("1.2.3", dest_dir=tmp_path, opener=opener, binary_name=name)
    assert not (tmp_path / name).exists()

def test_missing_checksum_entry(tmp_path):
    name = "falcon-mcp-1.2.3-linux-x86_64"
    opener = make_opener(BIN, f"{DIGEST}  some-other-file\n")
    with pytest.raises(RuntimeError, match="no checksum entry"):
        download_binary("1.2.3", dest_dir=tmp_path, opener=opener, binary_name=name)
