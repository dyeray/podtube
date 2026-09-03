import os
import time

from main import app


def test_cleanup_downloads_deletes_only_old_cached_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cache = tmp_path / "storage" / "youtube" / "channel"
    manual = tmp_path / "storage" / "filesystem" / "library"
    cache.mkdir(parents=True)
    manual.mkdir(parents=True)

    old_file = cache / "old.mp4"
    new_file = cache / "new.mp4"
    marker = cache / "old.downloading"
    manual_file = manual / "old.mp3"
    for path in (old_file, new_file, marker, manual_file):
        path.touch()

    old_timestamp = time.time() - 31 * 86400
    for path in (old_file, marker, manual_file):
        os.utime(path, (old_timestamp, old_timestamp))

    result = app.test_cli_runner().invoke(
        args=["cleanup-downloads", "--older-than-days", "30"]
    )

    assert result.exit_code == 0
    assert result.output == "Deleted 1 file(s).\n"
    assert not old_file.exists()
    assert new_file.exists()
    assert marker.exists()
    assert manual_file.exists()


def test_cleanup_downloads_dry_run_keeps_old_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    old_file = tmp_path / "storage" / "youtube" / "channel" / "old.mp4"
    old_file.parent.mkdir(parents=True)
    old_file.touch()
    old_timestamp = time.time() - 31 * 86400
    os.utime(old_file, (old_timestamp, old_timestamp))

    result = app.test_cli_runner().invoke(
        args=["cleanup-downloads", "--older-than-days", "30", "--dry-run"]
    )

    assert result.exit_code == 0
    assert result.output == "Would delete 1 file(s).\n"
    assert old_file.exists()
