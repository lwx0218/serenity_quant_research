#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SHARED_TEMPLATE_ROOT="$(cd "${TEMPLATE_ROOT}/.." && pwd)"
INTAKE_TEMPLATE="${SHARED_TEMPLATE_ROOT}/project-intake-template.md"

slugify() {
  local value

  value="$(printf '%s\n' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g')"

  if [ -z "${value}" ]; then
    value="project"
  fi

  printf '%s\n' "${value}"
}

escape_sed() {
  printf '%s\n' "$1" | sed 's/[\\/&]/\\&/g'
}

usage() {
  echo "Usage: ${0##*/} <target-dir> [project-name]" >&2
  echo "       <target-dir> comes first; project-name defaults to the directory name." >&2
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "${1:-}" = "" ]; then
  usage
  exit 1
fi

TARGET_INPUT="$1"
PROJECT_NAME="${2:-$(basename "${TARGET_INPUT}")}"

if [ ! -f "${INTAKE_TEMPLATE}" ]; then
  echo "Project intake template not found: ${INTAKE_TEMPLATE}" >&2
  exit 1
fi

mkdir -p "${TARGET_INPUT}"
TARGET_ROOT="$(cd "${TARGET_INPUT}" && pwd)"
TARGET_BASENAME="$(basename "${TARGET_ROOT}")"
PROJECT_SLUG="$(slugify "${TARGET_BASENAME}")"
INTAKE_DOC_REL="docs/project-intake/${PROJECT_SLUG}.md"
INTAKE_DOC_PATH="${TARGET_ROOT}/${INTAKE_DOC_REL}"

if [ "${TARGET_ROOT}" = "${TEMPLATE_ROOT}" ]; then
  echo "Refusing to bootstrap into the template source directory." >&2
  exit 1
fi

cp -R "${TEMPLATE_ROOT}/." "${TARGET_ROOT}/"

mkdir -p \
  "${TARGET_ROOT}/docs/project-intake" \
  "${TARGET_ROOT}/operations/planning" \
  "${TARGET_ROOT}/operations/work_logs" \
  "${TARGET_ROOT}/operations/reviews"

PROJECT_NAME_ESCAPED="$(escape_sed "${PROJECT_NAME}")"

while IFS= read -r file_path; do
  sed -i "s/__PROJECT_NAME__/${PROJECT_NAME_ESCAPED}/g" "${file_path}"
done < <(rg -l --hidden "__PROJECT_NAME__" "${TARGET_ROOT}")

cp "${INTAKE_TEMPLATE}" "${INTAKE_DOC_PATH}"

PROJECT_SLUG_ESCAPED="$(escape_sed "${PROJECT_SLUG}")"

sed -i \
  -e "s/__PROJECT_NAME__/${PROJECT_NAME_ESCAPED}/g" \
  -e "s/__PROJECT_SLUG__/${PROJECT_SLUG_ESCAPED}/g" \
  "${INTAKE_DOC_PATH}"

echo "Project scaffold created."
echo "Project name: ${PROJECT_NAME}"
echo "Project slug: ${PROJECT_SLUG}"
echo "Target directory: ${TARGET_ROOT}"
echo "Initial intake: ${INTAKE_DOC_REL}"
echo "Readiness: bootstrap-ready"
echo
echo "Next steps:"
echo "  cd ${TARGET_ROOT}"
echo "  pi"
echo
echo "Recommended path: start with simple work in native Pi."
echo "Upgrade to plan/spec/subagent/package only when complexity rises."
echo "Runtime prerequisites: install pi and configure provider/auth before expecting model-backed responses."
echo "Current state: bootstrap-ready. It becomes runtime-ready after pi and provider/auth are configured."
