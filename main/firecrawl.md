# Firecrawl Setup

Firecrawl is installed for web scraping and research during demo preparation.

Credential handling:

- `FIRECRAWL_API_KEY` is stored in the Windows user environment.
- Do not commit API keys or generated `.env` files.
- Do not paste the key into request JSON, docs, or scripts.

Usage:

```powershell
firecrawl --status
firecrawl scrape "https://example.com" -o "demos/CompanyName/source/example.md"
```

Repository hygiene:

- Use `.firecrawl/` only for ignored scratch output and install checks.
- Save durable demo-specific source notes, images, and scraped content under `demos/{ProspectOrCompanyName}/`.
- Keep shared Firecrawl procedure notes in `main/`.
