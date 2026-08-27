# Game Freak Director Archive Corpus

This directory is excluded from the Jekyll build. It contains preservation
inputs and normalized research data, not the public presentation layer.

Pipeline stages:

1. `discover` captures archive/month pages and builds the article manifest.
2. `fetch` downloads article media and shared theme assets with hashes. The
   live Game Freak host is tried first; missing resources fall back to the
   Internet Archive with their Wayback URL and snapshot timestamp retained.
3. `extract` creates Markdown, source fragments, and ordered structure JSON.
4. `validate` verifies languages, files, hashes, hotlinks, and translation layers.

The sample configuration covers entries 1, 73, and 199. Use `discover --all`
only after reviewing the sample report and crawl scope. WARC packaging is not
part of this first test implementation; raw response bodies and response
metadata are preserved losslessly so WARC export can be added later.

Sample run:

```powershell
python tools/gamefreak_archive_pipeline.py all --strict
```

Full discovery, after reviewing scope and storage:

```powershell
python tools/gamefreak_archive_pipeline.py discover --all
```

Full resumable capture, extraction, and strict validation:

```powershell
python tools/gamefreak_archive_pipeline.py all --all --delay 0.8 --strict
```

Source anomalies are recorded in `reports/discovery-issues.yml`. A resource
that is unavailable from both the live host and Wayback remains in
`manifest/assets.yml` with `status: unavailable`; validation reports it as a
warning rather than silently omitting it.

Documented source-URL typos may use a bilingual counterpart as a correction.
Those records use `capture_source: source-url-correction` and retain both the
broken `original_url` and the working `substitute_url`.
