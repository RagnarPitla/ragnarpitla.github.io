# Ragnar Pitla public projects

This public user-site repository owns the project hub at
`https://ragnarpitla.github.io/` and the Everett product journal at `/everett/`.
It does not publish or link to Everett's private source repository.

## Local verification

Use the same pinned container image as the GitHub Pages workflow. Do not add a
Gemfile or install Jekyll locally.

```sh
python3 scripts/verify_site.py source --root .
rm -rf _site
mkdir -p _site
docker pull ghcr.io/actions/jekyll-build-pages:v1.0.13
docker run --rm \
  -v "$PWD":/workspace \
  -e GITHUB_WORKSPACE=/workspace \
  -e INPUT_SOURCE=./ \
  -e INPUT_DESTINATION=./_site \
  -e INPUT_FUTURE=false \
  -e INPUT_VERBOSE=false \
  -e INPUT_TOKEN= \
  -e INPUT_BUILD_REVISION="$(git rev-parse HEAD)" \
  -e GITHUB_REPOSITORY=RagnarPitla/ragnarpitla.github.io \
  -e GITHUB_API_URL=https://api.github.com \
  ghcr.io/actions/jekyll-build-pages:v1.0.13
python3 scripts/verify_site.py built --root _site --origin https://ragnarpitla.github.io
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

## Publishing an Everett update

1. Check `_data/everett_truth.yml` against current Everett truth before writing.
2. Add only the needed reviewed full screenshot and deterministic thumbnail.
3. Add one `_everett_updates/YYYY-MM-DD-<slug>.md` using the quoted front matter template.
4. State source basis in prose; link only public HTTPS URLs.
5. Label current screenshot, historical mockup, or design direction accurately.
6. Add explicit alt, dimensions, caption, status, and a unique date and time.
7. Run source verification, the Docker build, built verification, and local HTTP preview.
8. Commit the Markdown, images, and any required truth-data update. Collection listings,
   tags, navigation, feed, and sitemap update automatically.
