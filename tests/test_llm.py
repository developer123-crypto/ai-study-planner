import study_planner.llm as L


class Resp:
    def __init__(self, status=200, body=None, text=""):
        self.status_code, self._body, self.text = status, body or {}, text

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code != 200:
            raise RuntimeError(self.status_code)


def ok(txt):
    return Resp(200, {"candidates": [{"content": {"parts": [{"text": txt}]}}]})


def test_falls_back_to_discovered_model(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")

    def post(url, **kw):
        return ok(" hi ") if "gemini-9-flash" in url else Resp(404, text="not found")

    def get(url, **kw):
        return Resp(200, {"models": [
            {"name": "models/gemini-9-flash", "supportedGenerationMethods": ["generateContent"]},
            {"name": "models/gemini-9-flash-tts", "supportedGenerationMethods": ["generateContent"]},
        ]})

    monkeypatch.setattr(L.requests, "post", post)
    monkeypatch.setattr(L.requests, "get", get)
    assert L.ask("x") == ("gemini-9-flash", "hi")


def test_bad_key_stops_early(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "bad")
    monkeypatch.setattr(L.requests, "post", lambda *a, **k: Resp(400, text="API_KEY_INVALID"))
    try:
        L.ask("x")
        assert False
    except RuntimeError as e:
        assert "key problem" in str(e)


def test_all_errors_reported(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(L.requests, "post", lambda *a, **k: Resp(404, text="nf"))
    monkeypatch.setattr(L.requests, "get", lambda *a, **k: Resp(200, {"models": []}))
    try:
        L.ask("x")
        assert False
    except RuntimeError as e:
        assert "gemini-flash-latest: HTTP 404" in str(e)
