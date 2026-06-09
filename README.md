# NAVPLOT

Generates NOTAM briefings in PDF format.

The app can be used standalone via the nplot.py script, or via Cloudflare
workers to serve PDFs from https://navplot.asselect.uk

## Development

### Cloudflare worker

1. Create Cloudflare worker linked to this repository, set build command to `uv run build.py
build` (this isn't picked up from wrangler.jsonc). Disable builds for non-production branches.

2. Set env vars/secrets for NATS_USER, NATS_PASSWORD and DISCORD_WEB_HOOK.

3. Create Deploy Hook. Manually trigger build using:

       curl -X POST "<deploy_hook_url>"
