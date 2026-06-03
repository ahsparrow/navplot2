# NAVPLOT

Generates a PDF NOTAM briefing.

The app can be used standalone via the nplot.py script, or via GitHub pages
to serve PDFs from https://navplot.asselect.uk

## Development

### Cloudflare worker

1. Create Cloudflare worker linked to this repository, set build command to
   uv run build.py build. Disable builds for non-production branches.

2. Set build variables for NATS_USER and (encrypted) NATS_PASSWORD.

3. Set domain name (navplot.asselect.uk)

4. Create Deploy Hook. Manually trigger build using:

    curl -X POST "<deploy_hook_url>"
