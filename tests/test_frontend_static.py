"""Static frontend structure checks for the split main and upload pages."""


from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "frontend"
DOCKER_ROOT = REPO_ROOT / "docker"


def _read(name: str) -> str:
    return (FRONTEND_ROOT / name).read_text(encoding="utf-8")


def _read_asset(name: str) -> str:
    return (FRONTEND_ROOT / "assets" / name).read_text(encoding="utf-8")


def _read_docker_frontend(name: str) -> str:
    return (DOCKER_ROOT / "frontend" / name).read_text(encoding="utf-8")


def test_frontend_exposes_separate_main_and_upload_pages() -> None:
    """The landing page and upload workspace should be separate documents."""
    main = _read("main.html")
    upload = _read("upload.html")
    index = _read("index.html")

    assert 'data-page="main"' in main
    assert 'href="/upload.html"' in main
    assert "Open Upload Page" in main
    assert 'id="upload-app"' not in main

    assert 'data-page="upload"' in upload
    assert 'id="upload-app"' in upload
    assert 'id="upload-form"' in upload
    assert 'type="file"' in upload
    assert "Start Pipeline Job" in upload
    assert 'id="upload-dynamic-fields"' in upload
    assert "dedicated upload workspace" in upload
    assert 'id="upload-result"' in upload
    assert 'href="/main.html"' in upload

    assert "/main.html" in index
    assert "window.location.replace" in index


def test_frontend_navigation_links_main_and_upload_from_all_pages() -> None:
    """Every frontend page should expose consistent navigation to main and upload."""
    for name in ("main.html", "upload.html", "status.html", "artifacts.html", "help.html"):
        html = _read(name)
        assert 'href="/main.html">Main<' in html
        assert 'href="/upload.html">Upload<' in html


def test_upload_script_binds_submit_without_waiting_for_form_options() -> None:
    """Upload submission should be bound before async parameter loading finishes."""
    script = _read_asset("app.js")
    start = script.index("async function initUploadPage()")
    end = script.index("async function initStatusPage()")
    upload_init = script[start:end]

    assert 'form.addEventListener("submit"' in upload_init
    assert 'await getJson("/form-options")' not in upload_init
    assert "void loadUploadFormOptions" in upload_init
    assert "async function loadUploadFormOptions" in script


def test_nginx_frontend_allows_large_upload_bodies() -> None:
    """Frontend nginx should not reject meeting videos with the default tiny body limit."""
    config = _read_docker_frontend("nginx.conf")

    assert "client_max_body_size 2048M;" in config
    assert "proxy_pass http://api:8000/api/;" in config
