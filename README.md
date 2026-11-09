# Drift + Chance — Openverse edition

A free local experimental website. Uses existing openly licensed internet images from Openverse, not AI-generated images. No account, API key, PHP, Node, or extra Python packages required.

## Start on Mac

1. Unzip and open the `drift-chance-openverse` folder in VS Code.
2. If an earlier local server is running in VS Code Terminal, press **Control+C** to stop it.
3. In the VS Code Terminal (inside this folder), run:

   python3 server.py

4. Open http://localhost:8000 in Safari, enter a sentence, and click **Find images**.

To stop the server, press **Control+C**.

## Notes

- The site searches Openverse's indexed, openly licensed images. It cannot search all of the web, private accounts, or arbitrary Instagram photos.
- It mixes loose keyword associations and random archival terms; the search label shows the chosen keyword and an experimental drift seed. The seed is a conceptual trace, **not** a guaranteed source location or year.
- Each card links to the image's source. Creator and license are displayed when available. Review source-specific license and attribution requirements before publishing or redistributing images.
- Openverse can limit anonymous traffic. If you see HTTP 429, wait and try again. Some images may fail to load due to external servers.
- Results are temporarily cached in server memory for 30 minutes to reduce API requests. Nothing is downloaded to disk.
