"""Global pytest fixtures and test environment configuration."""

from pathlib import Path
import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_web_dist_for_testing():
    """Ensure web/dist/index.html exists for SPA router tests if frontend has not been compiled."""
    web_dist_dir = Path(__file__).resolve().parent.parent / "web" / "dist"
    index_file = web_dist_dir / "index.html"
    created_placeholder = False

    if not index_file.exists():
        web_dist_dir.mkdir(parents=True, exist_ok=True)
        index_file.write_text(
            '<!doctype html>\n<html lang="en">\n<head><title>ARGUS</title></head>\n'
            '<body><div id="root"></div></body>\n</html>\n',
            encoding="utf-8",
        )
        created_placeholder = True

    yield

    if created_placeholder and index_file.exists():
        try:
            index_file.unlink()
            if web_dist_dir.exists() and not any(web_dist_dir.iterdir()):
                web_dist_dir.rmdir()
        except OSError:
            pass
