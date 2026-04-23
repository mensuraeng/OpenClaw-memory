#!/usr/bin/env bats
# Tests for install.sh script structure and safety

load '../test_helper'

INSTALL_SCRIPT="${TESTS_DIR}/../system/install.sh"

setup() {
    setup_test_environment
}

teardown() {
    teardown_test_environment
}

# ── Script structure ──────────────────────────────────────────────────────────

@test "install.sh wraps in main() for curl-pipe safety" {
    # The script must wrap everything in main() so that `curl | bash` downloads
    # the entire script before execution begins. Without this, stdin-consuming
    # commands (like git) can eat part of the piped script.
    grep -q '^main()' "$INSTALL_SCRIPT" || grep -q '^main ()' "$INSTALL_SCRIPT"
    grep -q '^main "\$@"' "$INSTALL_SCRIPT"
}

@test "install.sh passes syntax check" {
    run bash -n "$INSTALL_SCRIPT"
    assert_success
}

# ── Stdin safety ──────────────────────────────────────────────────────────────

@test "git clone redirects stdin to /dev/null" {
    # When piped via curl | bash, git can consume stdin (the rest of the script)
    run grep 'git clone' "$INSTALL_SCRIPT"
    assert_success
    assert_output --partial '</dev/null'
}

@test "git pull redirects stdin to /dev/null" {
    run grep 'git.*pull' "$INSTALL_SCRIPT"
    assert_success
    assert_output --partial '</dev/null'
}

@test "openclaw cron commands redirect stdin to /dev/null" {
    # Both cron list and cron add should protect stdin
    run grep -c '</dev/null' "$INSTALL_SCRIPT"
    assert_success
    # At least 4: git clone, git pull, openclaw cron list, openclaw cron add
    local count="${output}"
    [ "$count" -ge 4 ]
}
