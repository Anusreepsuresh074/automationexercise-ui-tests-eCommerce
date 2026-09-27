---
name: create-ui-framework-structure
description: Scaffolds a brand-new UI test automation project from scratch — genuinely confirms the browser framework/language, reporting tool, CI platform, and browsers/viewports before building anything, since UI ecosystems split far more evenly than a single default (Playwright Python, Playwright TS, Selenium Python, Cypress, and others are all live options). Builds the confirmed layer structure one piece at a time, explaining what each piece is and why it exists before creating it. Never generates UI test cases, test scripts, or resolves auth — those belong to ui-test-design, ui-test-automation, and get-ui-auth. Use once, at the start of a new UI automation project, when there's no existing UI framework to extend.
---

# Create UI Framework Structure

The first step in the UI automation core build sequence (`agents/ui-automation-agent.md`, step 1): turns a project with no UI test automation at all into a scaffolded, runnable skeleton that every later UI skill builds on top of — `get-ui-auth`'s fixtures, `ui-test-design`'s matrix, and `ui-test-automation`'s generated scripts all assume this structure already exists. This skill only builds the skeleton; it never writes a page object for a real page, a real test case, or a real login flow.

Unlike the API side of this suite (which defaults to Python/pytest without much debate), there is no single default framework here. Playwright (Python or TypeScript), Selenium (Python or other bindings), Cypress, and others are all realistic choices depending on the project's existing stack and team preference — so Step 0 has to be a genuine, answered question, not a formality on the way to a fixed answer.

## When to use

- Once, at the very start of a UI automation project — before `get-ui-context`, `get-ui-auth`, or any other UI skill has anything to read or write against.
- Never mid-project to "add a folder" to an existing UI framework — if one already exists, extend it by hand or let `ui-test-automation`'s own reuse-before-creating behavior handle it; this skill is for greenfield only.

## Guardrails

These are hard constraints, not style preferences. If a step below seems to conflict with one of these, the guardrail wins.

- **The framework choice is never assumed.** Ask directly and get an actual answer before designing anything — don't default to Playwright (or any other tool) just because it's popular. If the target project's frontend repo already has UI tests in some framework, that's strong evidence for which one to confirm, but still confirm it rather than inferring silently.
- **Plan before you build.** Once the stack is confirmed, present the full target folder structure with a one-line purpose per piece, and get the user's confirmation on the layout before creating anything.
- **Build one layer at a time, explained as you go.** After the plan is confirmed, create each layer in turn — state what it is, why it exists, and how it connects to the rest, *before* writing its files. Never batch-generate the whole tree in one shot even after the plan is confirmed.
- **Create only what's needed at this stage.** Don't pre-create placeholder page objects, speculative test files, or fixtures for pages/flows that don't exist yet in this project — those are populated later, per real page/flow, by `ui-test-automation`. This skill's job is the shape, not the content.
- **No business-specific content.** Don't invent example pages, selectors, or flows for an app this project hasn't described yet. Placeholder directories stay empty (with a short note on what belongs there) until a real page/flow exists to automate.
- **Auth is a hook here, not an implementation.** This skill creates *where* login/session fixtures will eventually live and wires no real login logic into it — resolving the actual login flow and session shape is `get-ui-auth`'s job entirely. Don't duplicate that work here.
- **Centralize configuration.** App base URL(s) per environment, browser/viewport choices, and timeouts live in one place — never scattered as literals across generated test files.
- **Record the confirmed stack where later skills can find it without re-asking.** Once Step 0 is answered, the project's copy of `agents/ui-automation-agent.md` (its "Project config" section) is where the UI framework/language, app base URL(s), and repo path for generated tests get recorded — update it (or tell the user to) so `ui-test-automation` and the rest of the sequence don't have to ask again.
- **Meaningful names only.** Every folder and file name should say what it holds — no `utils2`, `stuff/`, `helpers_final.py` equivalents in whatever language was confirmed.

## Step 0 — Confirm scope

Before designing anything, confirm these directly (don't proceed on an assumption for any of them):

1. **UI framework and language.** E.g. Playwright (Python or TypeScript), Selenium (Python or other), Cypress, or another tool the project already uses. If the target app's own repo already has UI tests, name that as the likely answer and confirm it rather than silently picking something else.
2. **Reporting tool.** Whatever the confirmed framework's natural reporting story is (e.g. Playwright's own HTML reporter, Allure, JUnit XML) — confirm which one this project wants rather than assuming.
3. **CI/CD platform.** Where this suite's runs will actually execute (Bitbucket Pipelines, GitHub Actions, GitLab CI, Jenkins, or none yet).
4. **Browsers and viewports.** Which browsers (Chromium/Firefox/WebKit, or a specific set) and which viewport sizes (desktop, mobile, both) need to be covered — this materially changes how the config/run layer is shaped.
5. **Environments.** Which environments need their own app base URL (dev/staging/prod, or project-specific names).

Don't design the target structure past this step on assumptions where the answer would change it.

## Target architecture

Present a full target tree to the user before creating anything, adapted to whatever Step 0 confirmed. The pieces every UI framework choice needs, regardless of language/tool:

- **Config layer** — per-environment app base URL(s), browser/viewport matrix, timeouts, in one place with a single loader.
- **Browser/session core** — wherever the confirmed framework's browser context/driver setup lives, so every generated test starts from the same launch/config path rather than each test configuring its own browser instance.
- **Page objects / component objects directory** — empty until `ui-test-automation` populates it per real page, one file per page/component, never one giant file.
- **Assertions/wait-helpers layer** — a single place for UI-specific assertions (visibility, text content, URL) and explicit waits, so generated tests never reach for a raw framework assertion or a bare `sleep`.
- **Fixtures/setup root** — where session/login fixtures will land once `get-ui-auth` resolves the login flow; this skill creates the empty hook, not the login logic itself.
- **Test directory** — empty, feature-grouped subfolders populated later by `ui-test-automation`.
- **Reporting output directory** — wherever the confirmed reporting tool writes its results, gitignored.
- **Dependency manifest** — whatever the confirmed language uses (`requirements.txt`, `package.json`, etc.).
- **CI pipeline stub** — a minimal config for the confirmed CI platform that installs dependencies and runs the suite.
- **`context/`** — not this skill's to create; `get-ui-context` makes it when it first writes `context/ui-context.md`.
- **README** — describing the confirmed stack and how to run the suite locally.

Don't hardcode this list as if every project gets identical folder names — the confirmed framework/language determines the exact shape (e.g. a Playwright TS project's layout looks different from a Selenium Python one even though every bullet above still applies conceptually).

### Concrete target trees, per confirmed framework

The conceptual pieces above are what every choice needs; the actual folder/file names have to be concrete and consistent, since `ui-test-automation` explicitly never defines structure itself — it discovers whatever this skill actually built and generates everything to match it exactly. Use the tree matching Step 0's confirmed choice (or the closest equivalent for a framework not listed, applying the same conventions — package-init files for a Python-based tool, a native config file for the framework, a dedicated auth-artifact location for cached sessions).

**Playwright (Python) — pytest-based:**
```
.
├── config/
│   └── config.yaml              # per-environment app base URL(s), browser/viewport matrix, timeouts
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_loader.py     # reads config.yaml + env overrides
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser_base.py      # browser/context launch — every test goes through here, never a one-off launch
│   │   └── assert_helper.py     # UI assertions + explicit-wait wrappers — never a bare assert or fixed sleep
│   ├── pages/
│   │   └── __init__.py          # <page>_page.py per real page — empty until ui-test-automation populates
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # shared fixtures — cached auth storage-state, browser context
│   └── <flow>/                  # created per feature later, e.g. tests/login/, each with its own __init__.py
├── auth/
│   └── .gitkeep                 # cached storageState JSON lands here — gitignored, never committed
├── conftest.py                   # root: pytest_addoption (--env, --browser), one-time login/global-setup hook
├── context/                      # created by get-ui-context / get-ui-auth, not this skill
├── reports/                      # Allure/HTML output, gitignored
├── requirements.txt
├── pytest.ini                    # markers section: smoke/sanity/regression + feature tags registered here
├── .env.example
├── bitbucket-pipelines.yml       # or the confirmed CI platform's equivalent
└── README.md
```

**Playwright (TypeScript):**
```
.
├── config/
│   └── config.ts                 # per-environment app base URL(s), browser/viewport matrix
├── src/
│   ├── pages/                    # <Page>.ts per real page — empty until ui-test-automation populates
│   ├── core/
│   │   └── assertHelper.ts       # UI assertions + wait wrappers
│   └── utils/
│       └── logger.ts
├── tests/
│   └── <flow>/                   # created per feature later, e.g. tests/login/login.spec.ts
├── auth/
│   └── .gitkeep                  # cached storageState.json lands here — gitignored
├── playwright.config.ts          # projects/browsers, retries, tag config, global setup wiring
├── global-setup.ts               # one-time login, saves storageState for every test to reuse
├── package.json
├── .env.example
├── <CI config for the confirmed platform>
└── README.md
```

**Selenium (Python) — pytest-based:**
```
.
├── config/
│   └── config.yaml
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_loader.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── driver_base.py        # WebDriver instantiation/teardown, explicit-wait helpers (no native auto-wait here)
│   │   └── assert_helper.py
│   ├── pages/
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # session-scoped cached auth cookie/token fixture; function-scoped driver fixture
│   └── <flow>/                   # created per feature later, each with its own __init__.py
├── conftest.py
├── context/
├── reports/
├── requirements.txt
├── pytest.ini
├── .env.example
├── <CI config for the confirmed platform>
└── README.md
```

**Cypress:**
```
.
├── cypress/
│   ├── e2e/
│   │   └── <flow>/               # created per feature later, e.g. cypress/e2e/login/login.cy.ts
│   ├── pages/                    # <page>.ts per real page — empty until ui-test-automation populates
│   ├── fixtures/                 # static test-data JSON
│   └── support/
│       ├── commands.ts           # custom commands + cy.session() setup for cached auth
│       └── e2e.ts
├── cypress.config.ts             # per-environment base URL, retries; cypress-grep wiring if that dependency exists
├── package.json
├── .env.example
├── <CI config for the confirmed platform>
└── README.md
```

If the confirmed choice is something else entirely, build the equivalent layers under equivalent names following the same conventions these four demonstrate (config isolation, a page-object location, a cached-auth-artifact location, package-init files only where the language needs them) — and say so plainly in the summary so it's clear the tree was adapted, not copied from an unlisted framework's actual convention.

## Build phases

Create these in order, stating what/why/how for each *before* writing its files — never jump ahead or batch-generate the whole tree at once:

1. **Configuration management** — app base URL(s) per environment, browser/viewport matrix, single config loader.
   *Why:* every other layer needs these without hardcoding them per test.
2. **Browser/session core** — the shared launch/context setup every test will go through.
   *Why:* one chokepoint for browser configuration means every generated test behaves consistently.
   *Concurrency default:* set a conservative local worker/parallelism cap rather than leaving it at the framework's own CPU-based default (e.g. Playwright's `workers` option) — uncapped local parallelism against a real dev/staging environment has caused genuine navigation timeouts under resource contention (confirmed by dogfooding: failures at 6 concurrent workers on a 12-core machine, clean at 4, clean at 1). This is an environment-reliability concern, not a framework bug — CI's dedicated runner can usually afford to leave its own worker count unset/higher; only the local default needs capping. Say plainly in the summary that this was set and why, so it's not mistaken for an arbitrary number.
3. **Assertions/wait-helpers layer.**
   *Why:* consistent, readable UI assertions and explicit waits instead of ad hoc ones scattered through generated tests.
4. **Page objects / component objects directory, fixtures/setup root, test directory, and the cached-auth-artifact location** (e.g. `auth/` for a Playwright storage-state file, or wherever the confirmed framework's session-caching convention puts one) — created empty, each with a short note on what belongs there and that later skills populate them per real page/flow.
   *Why:* establishes the shape without fabricating content for pages that don't exist yet in this project. The auth-artifact location exists so `get-ui-auth`/`ui-test-automation` have a known, gitignored place to cache a logged-in session rather than each inventing its own.
5. **Reporting wiring** — output directory + config pointing the confirmed tool at it.
6. **CI/CD readiness** — a minimal pipeline stub for the confirmed platform.
7. **Documentation** — README describing the confirmed stack and how to run locally.

## Limitations

This skill is only responsible for the framework shell. It must **not**:

- Generate UI test cases (that's `ui-test-design`).
- Generate UI test scripts or page objects for real pages (that's `ui-test-automation`).
- Execute tests.
- Resolve or document the real login flow or session shape (that's `get-ui-auth`) — this skill only creates the empty fixture hook it will land in.

If asked to do any of the above mid-conversation, say which skill owns that responsibility instead of doing it here.

## Notes for reuse across projects

- Never hardcode a project-specific app URL, page name, or business domain in this skill file itself — Step 0's confirmation and the target architecture above are what stay generic across every project this suite is used on.
- The confirmed framework/language varies genuinely by project — don't assume last project's choice carries over.
- Re-running this skill on a project that already has a UI framework is out of scope — point the user at extending the existing structure by hand instead of regenerating it.
