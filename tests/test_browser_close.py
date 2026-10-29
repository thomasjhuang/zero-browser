"""Closing the last page must leave Chrome's debugging port listening."""

import jev_ultrafast.browser as browser_mod


def test_closing_the_last_page_leaves_another_page(monkeypatch):
    pages = [{"targetId": "task", "type": "page", "url": "http://127.0.0.1/form"}]
    calls = []

    def cdp(method, **params):
        calls.append(method)
        if method == "Target.getTargets":
            return {"targetInfos": [dict(page) for page in pages]}
        if method == "Target.createTarget":
            pages.append({"targetId": "keeper", "type": "page", "url": "about:blank"})
            return {"targetId": "keeper"}
        if method == "Target.closeTarget":
            pages[:] = [page for page in pages if page["targetId"] != params["targetId"]]
            return {"success": True}
        raise AssertionError(method)

    monkeypatch.setattr(browser_mod, "cdp", cdp)
    browser = browser_mod.Browser.__new__(browser_mod.Browser)
    browser.target = "task"
    browser.close()
    assert calls == ["Target.getTargets", "Target.createTarget", "Target.closeTarget"]
    assert [page["targetId"] for page in pages] == ["keeper"]
    assert browser.target is None


def test_close_leaves_an_existing_other_page_alone(monkeypatch):
    pages = [
        {"targetId": "task", "type": "page", "url": "http://127.0.0.1/form"},
        {"targetId": "other", "type": "page", "url": "about:blank"},
    ]

    def cdp(method, **params):
        if method == "Target.getTargets":
            return {"targetInfos": [dict(page) for page in pages]}
        if method == "Target.closeTarget":
            pages[:] = [page for page in pages if page["targetId"] != params["targetId"]]
            return {"success": True}
        raise AssertionError(method)

    monkeypatch.setattr(browser_mod, "cdp", cdp)
    browser = browser_mod.Browser.__new__(browser_mod.Browser)
    browser.target = "task"
    browser.close()
    assert [page["targetId"] for page in pages] == ["other"]
