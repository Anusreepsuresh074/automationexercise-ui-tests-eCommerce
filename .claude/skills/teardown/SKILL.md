---
name: teardown
description: Clears stale test data left behind by either automation suite — pytest-api's validation phase and/or ui-test-automation's execution phase, whichever a project runs — since both write resource type, ID, environment, and creation time to the same shared runtime registry (e.g. reports/created-resources.jsonl). Resolves each resource type's delete endpoint from context/api-context.md, works out safe deletion order for dependent resources, and deletes only entries created before today — never same-day entries, so today's data stays available for debugging a run that just happened. Never invents a resource type, endpoint, or auth flow; only clears what the registry says was actually created, regardless of whether an API test or a UI-driven browser flow created it — cleanup is always a direct API-layer delete call either way, never a re-driven browser action. Only ever runs after the calling agent (or the user directly) has asked "Run teardown to clear stale test data from before today? (y/n)" and gotten an explicit yes — this stays true even when the motivating trigger is data piling up from repeated CI/CD regression runs; teardown is never wired to run unattended inside a pipeline. One shared skill for both suites, not a fork per domain, since the cleanup logic never actually depends on which suite created an entry.
---

# Teardown

Clears out stale test data left behind by prior runs of **either** automation suite: for every resource type recorded in the runtime created-resource registry with a creation timestamp **before today**, this skill resolves the real delete endpoint, works out the order dependent resources must be removed in, and calls it directly against the target environment. It doesn't matter whether a resource was created by a `pytest-api` test hitting the API directly or a `ui-test-automation` test driving the browser through a form — both write to the same registry, and cleanup for either is identical: resolve the resource type's delete endpoint and call it through the API layer, never by re-driving the browser (slower, more fragile, and pointless when a direct call already does the job). Entries created **today are left alone** — same-day data (including whatever the run that just finished created) stays in the environment in case a failing test needs to be debugged against it. It never writes a test method, page object, or fixture code, never invents an endpoint that isn't in `context/api-context.md`, and never runs without the user having explicitly said yes to a direct "run teardown now?" confirmation.

**Workflow position:** runs after `pytest-api`'s validation phase and/or `ui-test-automation`'s execution phase have finished (whichever a project actually uses — the same relative step, step 6, in either agent's sequence), gated on the user confirming they want stale test data cleared. An API-only project runs this after `pytest-api`; a UI-only project runs it after `ui-test-automation`; a project running both invokes it once to cover data either suite created. `context/schema-validation-report.md` and `create-report`'s downstream report are both already captured before teardown deletes anything, so clearing data afterward never affects report accuracy. Because only prior-day entries are eligible, running teardown right after a validation/execution pass never touches what that same pass just created.

## When to use

- Right after `pytest-api`'s validation phase and/or `ui-test-automation`'s execution phase finishes executing a suite that created one or more resources, **and** the user has answered yes to "Run teardown to clear stale test data (created before today)?"
- Periodically (e.g. once a day, or before a new test run) to clear out resources created on prior days — including the accumulation from repeated CI/CD regression runs, which is often the actual reason to invoke this regularly rather than only once after a single local run.
- Someone asks "clear out the test data from before today" or "why is test data piling up in `<environment>`?" — a common symptom of a nightly/scheduled regression pipeline (per `ci-integration`) running day after day with nobody separately clearing prior-day data.
- **Never run proactively, as an automatic follow-on to either suite, or wired into the CI/CD pipeline itself as an unattended step** — the confirmation is a hard gate every single time, even when the motivating reason is CI/CD accumulation. A human (or the calling agent, with a human present) asks and gets an explicit yes in the moment teardown actually runs; an automated regression job piling up data is a reason to invoke this skill *interactively, more often* — never a reason to skip the gate.

## Prerequisites (hard stop if missing)

| Input | Source skill | Required? |
|---|---|---|
| Explicit user "yes" to running teardown now | Human (or the calling agent's confirmation step) | **Yes** — if not yet asked/answered, ask `Run teardown to clear stale test data (created before today)? (y/n)` and stop until answered |
| Runtime created-resource registry (e.g. `reports/created-resources.jsonl`) with one or more entries | `pytest-api`'s validation phase and/or `ui-test-automation`'s execution phase — whichever ran and created resources | **Yes** — if empty or missing, say `Nothing to clear — no tracked test data found.` and stop |
| `context/api-context.md` | `get-context` | **Yes** — needed to resolve each resource type's delete endpoint, regardless of whether the resource was created via a direct API call or a UI-driven flow |
| Auth fixture / token flow | `get-api-auth` (and whatever `get-ui-auth`/`ui-test-automation` additionally wired for UI-driven creates) | **Yes** — teardown's delete calls reuse the same underlying API auth either suite's create calls used |

## Downstream handoff (nothing here is re-derived downstream)

Nothing in the core sequence re-checks teardown's own logic — `create-report` reports on the run `pytest-api`'s validation phase and/or `ui-test-automation`'s execution phase already captured, independent of whether teardown has cleared the underlying stale data yet. If a delete call itself throws unexpectedly (not a 404/410), that's a teardown failure to surface directly to the user, not something a downstream skill re-implements.

## Guardrails

These are hard constraints, not style preferences. If a step below seems to conflict with one of these, the guardrail wins.

- **Never run without an explicit yes.** This is the hard gate teardown exists behind: ask (or confirm the calling agent already asked) `Run teardown to clear stale test data (created before today)? (y/n)` and stop on anything other than an affirmative answer. This is separate from — and in addition to — confirming which environment, per the destructive-action guardrail below.
- **Never auto-invoke from inside a CI/CD pipeline job.** Even though accumulated data from repeated regression runs is a common, legitimate reason to *want* frequent teardown, this skill must never be wired into `ci-integration`'s pipeline as an unattended step that fires without a human present to answer the gate above. If CI-driven accumulation is the problem, the answer is running this skill interactively more often — never loosening or bypassing the gate to make it CI-safe.
- **Never touch today's entries.** Compare each registry entry's recorded creation timestamp against the current date (in the environment/project's reference timezone — confirm which one rather than assuming UTC). If it was created today, skip it: don't delete it, don't mark it, leave it in the registry untouched. This is the point of the skill — same-day data must stay available for debugging a run that just happened. Only entries created on a prior day are eligible for deletion, even when the user's "yes" sounded like "clear everything."
- **Read-only on everything except the registry and its own notes file.** Never modify `context/api-context.md`, `context/test-case-matrix.md`, `context/ui-test-case-matrix.md`, test methods, page objects, fixture code, or endpoint/payload/schema files — for either suite. The only things this skill writes are: entries in the runtime created-resource registry (marking stale ones cleared once deleted) and its own `context/teardown-notes.md`.
- **No fabrication.** Only call a delete endpoint for a resource type actually documented in `context/api-context.md`'s endpoint inventory. If no delete endpoint is documented for a resource type the registry says was created, say so explicitly under Open Questions in `context/teardown-notes.md` — never invent one, and never silently drop cleanup for it either.
- **Deletion order matters.** If resource A depends on resource B (created together, or A references B), delete in reverse-dependency order. Document the reasoning only when it's non-obvious — don't caption every line.
- **Idempotent teardown.** A delete call must not fail the run if the resource is already gone (e.g. a delete-endpoint test already removed it, or a previous teardown run partially completed). Classify a `404`/`410`-class response as "already gone" and continue; treat every other error class as a genuine teardown failure and surface it — never swallow those silently.
- **No automatic wiring into either suite's test session.** Never add post-yield deletion, a finalizer, or an autouse fixture that deletes resources as part of running the suite — that would delete same-day data the moment it's created, defeating the whole point of this skill. Teardown always runs as its own explicit, confirmed pass over the persisted registry, invoked separately from `pytest` (API tests) and from whatever runs the UI suite (pytest+Selenium/Playwright/Cypress) alike.
- **Executing deletes against a live API is a destructive action.** Same as `pytest-api`'s validation-phase and `ui-test-automation`'s execution-phase execution guardrails: confirm which environment first, and never run against production without the user explicitly naming it and approving that. This is on top of, not instead of, the yes/no gate above.
- **No credentials in output.** Reuse whatever auth fixture `get-api-auth` documented and `pytest-api`/`ui-test-automation` already wired for their respective create calls — never hardcode or print a token, key, or password.
- **Closed vocabulary for how each resource's cleanup was resolved.** Use exactly one of: `documented-delete-endpoint`, `cascade-via-parent`, `no-delete-endpoint-available`. Don't invent other labels.
- **Only clear resources the registry says were actually created.** Every resource type touched must trace back to an actual entry in the created-resource registry — never speculative cleanup for a resource type not recorded there, regardless of which suite might plausibly have created it.
- **Idempotent re-runs.** Re-running teardown only acts on registry entries not already marked cleared (and still eligible by age) — it must not attempt to re-delete (or double-count) an entry a prior teardown run already cleared, and must not re-derive the whole registry from scratch.

## Steps

1. **Confirm the go-ahead.** If the calling agent hasn't already asked and recorded a yes in this conversation, ask directly: `Run teardown to clear stale test data (created before today)? (y/n)`. Stop here on anything other than an explicit yes.
2. **Read the runtime registry.** Load the created-resource registry `pytest-api` and/or `ui-test-automation` populate (e.g. `reports/created-resources.jsonl`) and filter to entries not yet marked cleared. If invoked right after a run, scope to the environment that run targeted; if invoked standalone/periodically, confirm which environment(s) to clean per the destructive-action guardrail rather than assuming.
3. **Partition by age.** Compare each entry's creation timestamp against today's date. Entries created today are left untouched — don't include them in any deletion pass, don't mark them. Entries created on a prior day are candidates for cleanup.
4. **Resolve each stale resource type's delete endpoint.** Cross-reference `context/api-context.md`'s endpoint inventory for a `DELETE` (or equivalent) operation on that resource — the same resolution regardless of whether an API test or a UI flow originally created it. Classify the resolution using the closed vocabulary above:
   - `documented-delete-endpoint` — a DELETE endpoint for this exact resource is in the inventory.
   - `cascade-via-parent` — no direct delete endpoint, but deleting a parent resource is documented to cascade-remove this one; cite the parent's delete endpoint instead.
   - `no-delete-endpoint-available` — neither exists; flag under Open Questions rather than fabricating one.
5. **Determine deletion order.** Where multiple stale resource types were created together (e.g. a child resource created under a parent id), order deletes so dependents go before their parents.
6. **Confirm the target environment**, per the destructive-action guardrail, then execute the deletes: for each stale registry entry with a resolvable endpoint, call it through the project's `ApiBase`/helper layer (never raw `requests`/`httpx`, and never by re-driving a browser even for a UI-created resource) in the order from Step 5, and classify the response — already-gone vs genuine failure — per the idempotency guardrail.
7. **Mark cleared entries in the registry** so a re-run doesn't attempt to delete them again. Leave `no-delete-endpoint-available` entries untouched in the registry (don't fake a clear) and record them under Open Questions. Never touch today's entries in this step.
8. **Emit `context/teardown-notes.md`** using the template below, and print a short summary in conversation: what was cleared, what failed, what's still open, and how many today-created entries were intentionally left alone.
9. **Report and hand off.** Tell the user what was cleared (or partially cleared, listing gaps and genuine failures) — teardown is the last step before `create-report`, which reports on the run independent of whether cleanup happened.

## Output

No test/framework code is touched (unless the project has no registry read/delete helper yet, in which case add a minimal one — e.g. `src/helper/teardown_helper.py` under `api-automation/`, or the equivalent under `ui-automation/` — following whichever suite's existing layout convention applies). This skill writes only:
- Live DELETE calls against the resolved endpoints for stale (prior-day) registry entries.
- Updates to the runtime created-resource registry (marking stale entries cleared; today's entries untouched).
- `context/teardown-notes.md`.

`context/teardown-notes.md`:

```markdown
# Teardown Notes

_Generated by teardown on <date>, clearing stale (pre-today) test data against <environment>. Today's entries are intentionally left in place for debugging. Re-run any time to clear out another day's worth of prior data — from either suite._

## Resource cleanup resolution

| Resource type | Created on | Registry entries cleared | Delete endpoint | Resolution | Deletion order | Notes |
|---|---|---|---|---|---|---|
| <e.g. widget> | <date, prior day> | 3 | `DELETE /widgets/{id}` | documented-delete-endpoint | 1 (no dependents) | |

## Today's entries (left in place)

| Resource type | Count | Notes |
|---|---|---|
| <e.g. widget> | <n> | retained for debugging today's run |

## Open questions / follow-ups

- <resource types with no resolvable delete endpoint, genuine (non-404/410) delete failures, ambiguous dependency ordering — or "none">
```

## Bias to counter

Models tend to (a) delete everything in the registry regardless of creation date, wiping out the very same-day data a human might need to debug a just-finished run, (b) skip teardown entirely for a resource type with no obvious delete endpoint, leaving it silently orphaned with no Open Questions entry, (c) write a fire-and-forget delete wrapped in a broad `except` that also swallows real failures, (d) run without waiting for an explicit yes because "it's obviously fine to clean up," (e) treat CI/CD regression-run accumulation as license to wire teardown into the pipeline as an unattended step, or loosen the yes-gate to make it "CI-safe," rather than just running it interactively more often, or (f) assume every registry entry came from an API test and skip resolving cleanup for a resource type that's only ever created via a UI-driven flow, because "that's not what `pytest-api` creates." Force the age check for (a) on every run — never let "clean everything" collapse today's entries into the deletion set, even when the user's yes sounded unconditional. Force an explicit Open Questions entry for (b), distinct already-gone-vs-genuine-failure handling for (c) — a bare `except: pass` around a delete call is never acceptable — a hard stop for (d) even when running teardown seems like the obviously-correct next move, an unconditional refusal to auto-wire for (e) regardless of how compelling the CI-cleanup motivation sounds, and resolution purely from the registry (never from which suite "usually" creates what) for (f).

## Notes for reuse across projects

- Never hardcode a project-specific resource type, endpoint, or dependency chain in this skill file itself — always resolve fresh from that project's `context/api-context.md` and the actual registry entries a run produced.
- Which resources need `cascade-via-parent` handling varies per API — don't assume last project's cascade behavior applies here.
- "Today" means the project's reference timezone/environment clock, not the machine running this skill — confirm which one the registry's timestamps use before comparing dates, rather than assuming UTC.
- If a project has many stale resource types, still wire all resolvable ones in the same run; only truncate what's printed inline in conversation (and say so).
- **This skill is intentionally shared, not forked per suite.** Its logic never depends on which suite created an entry, only on the resource type recorded in the registry — a project using only `pytest-api`, only `ui-test-automation`, or both, uses this exact file unmodified. Never create a parallel `ui-teardown` or `api-teardown` — that would just duplicate this file's logic and let the two drift out of sync.
