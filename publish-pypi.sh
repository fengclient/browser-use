#!/usr/bin/env bash
set -euo pipefail

PACKAGE_NAME="browser-use-volcengine"
BRANCH="${PUBLISH_BRANCH:-main}"

if [[ -f .env.pypi ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env.pypi
  set +a
fi

git checkout "${BRANCH}"
git pull --ff-only origin "${BRANCH}"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Worktree must be clean before publishing." >&2
  exit 1
fi

read -r package_name version < <(
  uv run python - <<'PY'
import tomllib
from pathlib import Path

metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
print(metadata["name"], metadata["version"])
PY
)

if [[ "${package_name}" != "${PACKAGE_NAME}" ]]; then
  echo "Expected package ${PACKAGE_NAME}, found ${package_name} in pyproject.toml." >&2
  exit 1
fi

tag_name="${PACKAGE_NAME}-${version}"
tag_exists=0

if git rev-parse --verify --quiet "refs/tags/${tag_name}" >/dev/null; then
  tag_exists=1
  if [[ "$(git rev-list -n 1 "${tag_name}")" != "$(git rev-parse HEAD)" ]]; then
    echo "Tag ${tag_name} already exists but does not point at HEAD." >&2
    exit 1
  fi
fi

rm -rf dist
uv build
uv run --with twine python -m twine check dist/*

if [[ -z "${UV_PUBLISH_TOKEN:-}" ]]; then
  printf "PyPI token: "
  read -rs UV_PUBLISH_TOKEN
  printf "\n"
  export UV_PUBLISH_TOKEN
fi

uv publish dist/*

if [[ "${tag_exists}" == "0" ]]; then
  git tag -a "${tag_name}" -m "${PACKAGE_NAME} ${version} PyPI release"
fi

git push origin "${tag_name}"

echo "发布完成: ${PACKAGE_NAME} ${version}"
