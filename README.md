# podtube

Web application that creates a feed subscribable by a podcatcher from services that don't support feeds. Services currently supported:

* YouTube Channels & Playlists
* Invidious Channels & Playlists
* iVoox Originals
* Instagram Reels (experimental)
* Rumble Channels
* Filesystem: Serves media files added on the storage/filesystem directory.

More information on how to use on [Usage documentation](templates/index.html)

## Cleaning up downloads

Delete downloaded media older than a chosen number of days:

```bash
flask --app main cleanup-downloads --older-than-days 30
```

Add `--dry-run` to count files without deleting them. The command preserves active
`.downloading` markers and manually managed files under `storage/filesystem/`.
