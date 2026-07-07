import pytest
from falcon_mcp.falcon_mcp import platform_binary_name

@pytest.mark.parametrize("system,machine,expected", [
    ("Darwin", "arm64", "falcon-mcp-1.2.3-macos-arm64"),
    ("Darwin", "x86_64", "falcon-mcp-1.2.3-macos-x86_64"),
    ("Linux", "aarch64", "falcon-mcp-1.2.3-linux-arm64"),
    ("Linux", "amd64", "falcon-mcp-1.2.3-linux-x86_64"),
    ("Windows", "AMD64", "falcon-mcp-1.2.3-windows-x86_64.exe"),
])
def test_platform_binary_name(system, machine, expected):
    assert platform_binary_name(system, machine, "1.2.3") == expected

def test_unsupported_arch():
    with pytest.raises(RuntimeError, match="Unsupported architecture: s390x"):
        platform_binary_name("Linux", "s390x", "1.2.3")

def test_unsupported_os():
    with pytest.raises(RuntimeError, match="Unsupported operating system: plan9"):
        platform_binary_name("Plan9", "amd64", "1.2.3")
