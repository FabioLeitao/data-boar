# Release notes and how to publish a GitHub release

Each release has a markdown file here (e.g. `1.3.1.md`) with the release notes.

## After you push the code to GitHub

To publish **v1.3.1** (or the version you just bumped) as a GitHub release with the same version number and the prepared notes:

1. **Create and push the tag** (if not already pushed with the commit):
   ```bash
   git tag v1.3.1
   git push origin v1.3.1
   ```

2. **Create the release** using GitHub CLI:
   ```bash
   gh release create v1.3.1 --notes-file docs/releases/1.3.1.md --title "1.3.1"
   ```

   Or in the GitHub web UI: **Releases** → **Draft a new release** → choose tag `v1.3.1`, set title to `1.3.1`, and paste the contents of `docs/releases/1.3.1.md` into the description.

The release will then be visible on the repository’s Releases page and the Docker image with the same version tag is already on Docker Hub.
