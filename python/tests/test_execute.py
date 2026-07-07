import falcon_mcp.falcon_mcp as fm

def test_execute_returns_child_code(monkeypatch):
    monkeypatch.setattr(fm, "download_binary", lambda v, **k: "/fake/falcon-mcp")
    seen = {}
    def runner(cmd):
        seen["cmd"] = cmd
        return 3
    assert fm.execute(["--port", "0"], runner=runner) == 3
    assert seen["cmd"] == ["/fake/falcon-mcp", "--port", "0"]

def test_execute_download_failure_returns_1(monkeypatch, capsys):
    def boom(v, **k):
        raise RuntimeError("nope")
    monkeypatch.setattr(fm, "download_binary", boom)
    rc = fm.execute([], runner=lambda cmd: 0)
    assert rc == 1
    assert "Error executing falcon-mcp" in capsys.readouterr().err

def test_main_forwards_argv(monkeypatch):
    monkeypatch.setattr(fm.sys, "argv", ["falcon-mcp", "--help"])
    captured = {}

    def fake_execute(args, **k):
        captured["args"] = args
        return 0

    monkeypatch.setattr(fm, "execute", fake_execute)
    assert fm.main() == 0
    assert captured["args"] == ["--help"]
