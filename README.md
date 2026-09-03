# Gudo Snake

Gudo Snake is a cursed snake game with two playable builds:

- `demo.py`: the original Pygame desktop build.
- `docs/`: the static GitHub Pages build.

## Run Locally

Desktop:

```bash
python demo.py
```

GitHub Pages preview:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000`.

## GitHub Pages

In the repository settings, open **Pages**, choose **Deploy from a branch**, select
the `main` branch and the `/docs` folder, then save. The site uses only static
HTML, CSS, JavaScript, images, and MP3 files, so no server-side build step is
needed.

All 29 files in `sounds/` are included in the browser build. A user click on
`START RUN` unlocks browser audio; eating food and all collision types select a
random track.
