# NAVPLOT

Generates a PDF NOTAM briefing.

The app can be used standalone via the navplot.py script, or via GitHub pages
to serve PDFs from https://navplot.asselect.uk

## Development

### GitHub Pages

In GitHub pages set Build and Deployment source to "GitHub Actions". (The
GitHub workflow is defined in .github/workflows/navplot.yaml)

The action is triggered via an external scheduler - see the navplot_scheduler
project.

### ASSelect

Set the download links in the ASSelect app to:
    https://navplot.asselect.uk/today_south.pdf, etc.
