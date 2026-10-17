#!/usr/bin/env bash
# Full build of the site in a Linux container, for when a full local build is needed.
#
# Jekyll on Windows spends most of a build in Ruby's file-system calls (~15 minutes here); the same
# build on Linux takes a few. This streams the repository into a container with `git archive`
# (no bind-mounted source - that would be slow again), builds there with the same Ruby as the deploy
# (jekyll.yml: 3.2), and copies _site back out. Gems are kept in the volume pokeamice-docs-gems, so
# only the first run installs them.
#
#   tools/docker-build.sh                    # HEAD → P:/WEBSITE/.docs-verify/docker/_site (or $DOCS_VERIFY/docker)
#   tools/docker-build.sh --worktree         # HEAD + uncommitted changes to tracked files
#   tools/docker-build.sh --out <dir>        # somewhere else
#   then: python -m http.server 4760 --directory <dir>/_site,  python tools/check-build.py <dir>/_site
#
# Needs Docker Desktop running. Untracked files are not included (commit or `git add` them first).
set -euo pipefail
export MSYS_NO_PATHCONV=1                 # Git Bash: leave the container paths alone
repo=$(git rev-parse --show-toplevel)
out="${DOCS_VERIFY:-$repo/../../.docs-verify}/docker"   # the worktrees sit in P:/WEBSITE/pokeamice-main (1)/
rev=HEAD
while [ $# -gt 0 ]; do
  case "$1" in
    --worktree) rev=$(git -C "$repo" stash create); rev=${rev:-HEAD} ;;   # a commit object only; the stash list is untouched
    --out) out="$2"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
mkdir -p "$out"
out=$(cd "$out" && pwd)
image=ruby:3.2.6-bookworm
echo "building $(git -C "$repo" rev-parse --short "$rev") in $image → $out/_site" >&2
t0=$(date +%s)
git -C "$repo" archive "$rev" | docker run --rm -i -v pokeamice-docs-gems:/usr/local/bundle -e JEKYLL_ENV=production "$image" bash -c '
  set -e
  mkdir -p /site && tar -x -C /site && cd /site
  bundle install --quiet --jobs 8 >&2
  s=$(date +%s); bundle exec jekyll build -d /tmp/_site --quiet >&2; echo "jekyll build: $(( $(date +%s) - s )) s" >&2
  tar -C /tmp/_site -c .
' > "$out/site.tar"
rm -rf "$out/_site" && mkdir -p "$out/_site"
tar -x -C "$out/_site" -f "$out/site.tar" && rm "$out/site.tar"
echo "done in $(( $(date +%s) - t0 )) s → $out/_site" >&2
