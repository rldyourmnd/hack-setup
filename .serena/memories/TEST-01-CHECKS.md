# TEST-01-CHECKS

## Purpose

Prove Codex artifacts, the installer catalog, and required host versions.

## Source Of Truth

- `justfile` recipes `gate`, `check`, `test` (devin-setup has its own justfile twin).
- `scripts/check_codex_setup.py`: dependency-free Python 3.11 artifact validator (includes `check_ps1_ascii` — non-ASCII allowed only inside .ps1 comments; PS5.1 decodes BOM-less files as ANSI).
- `scripts/check_stack.py`: host doctor + generated `build/stack-standard.md`.
- `devin-setup/scripts/check_devin_setup.py`: devin twin validator + `check_shared_sync` (shared lib/modules must be byte-identical to `install/`) + hook smoke.
- `devin-setup/scripts/{sync_stack_pin.py,repair_devin_setup.py}`: generated stack-pin copy + managed user-config single writer.
- `tests/test_check_codex_setup.py`: validator plus `./setup --dry-run` (routes through `setup.ps1` on win32).
- `tests/test_check_stack.py`: version extract, standard contents, `doctor_decision`, live required doctor.
- `tests/test_env_sh.py` + `tests/test_env_ps1.py`: POSIX + Windows env twins (PATH heads, HACK_USER_BIN, per-platform asserts).
- `tests/test_member_setup.py`: member flag/module catalog contracts.
- `tests/test_lane_guard.py`: hack_mode.py push deny/allow — `git -C` target repos (incl. deleted caller cwd — issue #24 regression), quoted refspecs, `--all`/`--mirror`, bare HEAD, `gh pr merge`, orchestrator marker, history law (squash/rebase denied on every repo incl. orchestrator + lane-free).
- `tests/test_repair_config_cleanup.py`: repair config-cleanup keeps foreign `[hooks.state.*]` tables + `[[array-of-tables]]`, drops stale legacy.
- `devin-setup/tests/test_devin_setup.py`: devin checker, shared-twin byte parity, hook events incl. lane guard + history law (redirects USERPROFILE/APPDATA on nt — HOME does nothing on Windows).
- `tests/test_devin_forwarder.py`: root `.devin/hooks/devin_mode.py` forwarder reaches the devin-setup hook and exits 0 (exit 2 = Devin blocks).
- `tests/conftest.py`: GetShortPathNameW tempdir redirect on win32 for non-ASCII temp paths.
- `scripts/verify_serena.py`: stdio MCP client proving handshake → activate_project → tools/list → `find_symbol` (python_ty must be up) → list/write/read/delete memory. Tool errors are `isError` results, not RPC errors — the script checks both.

## Entry Points

- `just gate`: `./setup --status`, `check_codex_setup.py`, `check_stack.py`, `codex --version`.
- `just check`: source-only Codex/stack validation and native Just formatting. This is `stack-pin.control.proof`. It requires pin `control` paths, config == pin session/models/features, and AGENTS Mechanism.
- `just test`: `pytest -q` (use `pytest` / `~/.local/bin/pytest`, not `python3 -m pytest` on uv CPython).
- `just live`: `scripts/verify_serena.py` — REAL MCP proof, network + uvx required, not part of `gate`.
- `ruff check scripts tests`

## Proof levels

Output is labeled so nobody confuses a file check with a live wire-up:
`[artifact]` pin/config/docs consistency (check_codex_setup),
`[installed]` host tools match the pin (check_stack doctor),
`[live]` real MCP/deploy evidence (verify_serena, deploy health).

## Current Behavior

The artifact validator requires catalog ids `prereqs`, `member`, `codex-cli`, `runtimes`, `project-verify`, that `install/modules/<nn>-*` matches those rows, and that each module dir has both `module.sh` and `module.ps1` twins (`setup.ps1`/`bootstrap.ps1`/`env.ps1` + catalog `entry_windows` required since ADR 0012 native Windows). `codex-pin.json` and `runtimes.{node,bun}.packages` must cover all 5 PINNED_PLATFORMS incl. `windows-x86_64`; `installer_ps1` required on codex-pin and `runtimes.uv`. Repo skills must be `repo-orientation`, `quality-gate`, `one-repo-workflow`, `apply-stack-rule`. Plugin iteration is marketplace-driven (`.agents/plugins/marketplace.json` is the SoT): names map to `registered.<suffix>_plugin{,_skills}` (saint-tibo uses bare `plugin`/`plugin_skills`), each plugin's disk skills must equal its pin list, and every plugin skill must be AGENTS-named `$<plugin>:<skill>`. Nested templates must be `plugins/hack-agent-standards/nested/{README,web,api,mobile,desktop,telegram,infra}.md`. `justfile` must exist and define `gate`/`check`/`setup`/`test`. `Makefile` / `makefile` / `GNUmakefile` must not exist. `AGENTS.md` must route to `plugins/hack-agent-standards/standards`, include `## Motion`, and must not mention `docs/rules`. INDEX markdown links must exist. `docs/rules/` and `docs/agent-standards/` must not exist. `.codex/config.toml` must match `registered.session` (never + danger-full-access + live web search) and `models` (`gpt-6-astra` / `gpt-6-sol` / `xhigh` / requested `872000`/`700000`). `agents.enabled` and `features.multi_agent*` must be false. Do not add `.codex/agents/*.toml`. No project `.rules`. Project config must not define `profiles`; when the codex binary exists the user config must have no legacy `[profiles.sol]` and `~/.codex/sol.config.toml` must match `models.*`. Installed plugin caches under `~/.codex/plugins/cache/saint-tibo/<name>/<version>` must be byte-identical to `plugins/<name>/` (re-run `codex plugin add` on drift). Every `standards/*.md` file must be linked from INDEX.

Stack-pin schema 2: `control.rules` = `plugins/hack-agent-standards/standards/INDEX.md`. `registered.standards_plugin.id` = `hack-agent-standards@saint-tibo`. typescript `7.0.2` with no `compat_package`, `api_client.workspace` = `not-web`, `quality.just` = `1.58.0`. `do_not_use` includes Next.js, pnpm, asyncpg, TS6-in-web, `@hey-api/openapi-ts@next`, `bun add shadcn`, unconstrained RapidOCR/opencv-python, httpx 1.x, GNU make. Required conflicts include `hey-api-ts7-runtime` and `docling-opencv-cv2`.

Required probes must be OK: codex, node, bun, python, uv, just (just is installed by module 30 from pinned per-platform release assets, so requiring it is fair). Declared tools (rustc, go, docker, compose, psql, redis-server, ruff, pytest, ty) may DRIFT or be MISSING without failing the default doctor. CI (`.github/workflows/ci.yml`, free OSS runners only) retains the native roles and shared merge stops: `artifacts` + `devin-artifacts` (checkers, pinned pytest via `uvx --from pytest==<quality.pytest.version>`, `sh -n` over every module/deploy/notify shell file in a loop — a bare `sh -n a b` checks only `a`), `setup-e2e` + `devin-e2e` matrixes on ubuntu/macos, `setup-e2e-windows` + `devin-e2e-windows` (native install + pinned pytest on real Windows), and `deploy-e2e` (self-SSH provision on ubuntu, systemd timer drives a real deploy tick — issue #7 live proof). CI does not call Devin account-backed plugin installation or listing; account activation is unperformed.

## Invariants

- Do not claim the setup is ready unless `just gate` was actually run.
- `just reverify` is hackathon-day / network, not an everyday gate.

## Verification

- `just gate`
- `just test`

## Known Gaps

- Live `test_check_stack_doctor_passes` is host-state, not hermetic.

## Source and account boundaries

The source recipe selects `--source` on the Codex and stack checkers, which keeps
all authored pin/projection/generated consistency checks and avoids installed
configuration and version probes. Syntax checking leaves no Python bytecode.
The Devin checker has the same source boundary and reserves hook smoke fixtures
for normal/native execution. The native readiness gate retains its full checks.

The current CI uses shared preparation/completion at the existing library pin
and checks the generated Devin stack copy without rewriting it. Devin's optional
account-backed plugin installation/listing does not run on CI. The remaining
native installation, artifact, unit and isolated deployment checks retain their
real execution. This is source/component evidence, not account or model proof.

Ordinary pull requests retain the integration branch's full native policy: both
Codex and Devin run Linux, macOS and Windows before merge. The aggregate requires
all platform outcomes and shared merge stops. The old moving runner-label check
contexts need scoped metadata adoption; missing contexts are not bypassed.
