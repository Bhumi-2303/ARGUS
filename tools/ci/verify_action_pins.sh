#!/usr/bin/env bash
# Verify every `uses: owner/repo@<sha> # vX.Y.Z` in .github/workflows resolves to that tag upstream.
set -u
fail=0
while read -r repo sha tag; do
  r=$(echo "$repo" | cut -d/ -f1,2)
  if timeout 30 git ls-remote --tags "https://github.com/$r.git" 2>/dev/null \
      | grep -qE "^$sha[[:space:]]+refs/tags/$tag(\^\{\})?$"; then
    echo "OK    $r@$sha ($tag)"
  else
    echo "FAIL  $r@$sha does not match tag $tag"; fail=1
  fi
done < <(grep -rhoE 'uses: *[^ @]+@[0-9a-f]{40} *# *v?[0-9][^ ]*' .github/workflows \
          | sed -E 's/uses: *([^ @]+)@([0-9a-f]{40}) *# *(.*)/\1 \2 \3/' | sort -u)
exit $fail
