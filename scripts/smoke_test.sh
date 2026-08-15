#!/bin/sh
# Read-only smoke test against a running deployment. Every check is a plain
# GET, so this never creates or modifies data — safe to run against
# production.
#
# Usage: scripts/smoke_test.sh https://api-shop-staging.onrender.com

set -e

BASE_URL="${1:?Usage: $0 <base-url>}"
BASE_URL="${BASE_URL%/}"

failures=0

check() {
    description="$1"
    url="$2"
    expected_status="$3"

    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status" = "$expected_status" ]; then
        echo "OK   $description ($status)"
    else
        echo "FAIL $description (got $status, expected $expected_status) -> $url"
        failures=$((failures + 1))
    fi
}

check "health check"        "$BASE_URL/health/"                    200
check "swagger ui"          "$BASE_URL/api/schema/swagger-ui/"     200
check "static files"        "$BASE_URL/static/admin/css/base.css"  200
check "public products list" "$BASE_URL/api/products/"             200

echo
echo "--> health payload:"
curl -s "$BASE_URL/health/"
echo

if [ "$failures" -gt 0 ]; then
    echo "$failures check(s) failed"
    exit 1
fi

echo "All checks passed"
