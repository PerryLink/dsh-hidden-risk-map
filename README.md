# dsh-hidden-risk-map

**Boundary:** this plugin maps each row of a **safety hazard ledger** onto candidate clauses of the
major-accident-hazard determination standard, and reports which rows could not be mapped at all. It is
not `dsh-emergency-plan` (which checks a plan's element completeness) and not a site inspection tool.
It reads a ledger and produces **leads for review** — never a determination that something is or is not
a major accident hazard, which needs a site visit and professional judgement.

> ### ⚠️ The most useful thing this plugin does is admit what it could not map
>
> The failure mode of a keyword-based mapper is silent: a row that matches nothing simply vanishes, and
> a reader concludes "no major hazards found". So `HR-001` inverts that: **every row that matched no
> clause is listed explicitly**, with the reason it might have been missed — a different industry's
> clause, a hazard type governed by other rules, or simply wording the keyword table does not carry yet.
> The plugin's headline number is therefore "N rows are unmapped", not "0 hazards".
>
> **The standard was replaced, and its article numbers moved with it.** The determination standard in
> force is **应急管理部令第10号《工贸企业重大事故隐患判定标准》** (adopted 2023-03-20, published
> 2023-04-14, **in force 2023-05-15**). Its article 15 expressly repeals
> 安监总管四〔2017〕129号《工贸行业重大生产安全事故隐患判定标准（2017版）》. This pack cites only
> the 第10号令 article numbers, and a test asserts that the superseded 2017 number never appears.
>
> **Two things this plugin deliberately does not do.** It does not decide that a row *is* a major
> hazard; and it does not classify hazards that article 2 hands to other regimes — hazardous
> chemicals, fire, gas and special equipment are governed by *other* provisions, so a row touching them
> is reported as "check the corresponding regulation instead", not mapped.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a whole ledger use `ptc` |

## What it does

Registers the `hidden_risk_map` tool. It reads a hazard ledger — one row per recorded hazard, with the
columns the ledger actually carries — applies a versioned rule pack, and returns a report whose every
finding names the article it came from.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `HR-001` | every row maps to a clause, or is listed as unmapped | warn | principle |
| `HR-002` | a matched clause belongs to this deployment's industry, or defers to another regime | warn | direct |
| `HR-003` | a matched row carries the configured remediation fields (off by default) | warn | principle |
| `HR-004` | one clause hit by many rows is flagged for review (off by default) | info | principle |

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./dsh-hidden-risk-map-0.1.0.tgz
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/hidden-risk-map.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `HR-001` `clauses` — the article table: `article`, `industry`, `excerpt` and the `keywords` that
  select it. **The keywords are an editorial aid, not standard text.** They exist to point a ledger
  sentence at a candidate article; add your site's own vocabulary as you use it.
- `HR-002` `industry` — your enterprise's industry. Empty means the industry check cannot run and says
  so. `otherRegimes` lists the hazard types article 2 hands to other provisions.
- `HR-003` `requiredFields` — the remediation-closure columns your procedure requires, e.g.
  `[整改措施, 整改责任人, 整改完成时间]`. Empty means the rule does not run.
- `HR-004` `maxHitsPerClause` — flag a clause hit by more than this many rows. `0` disables it.

## Material format

The tool accepts JSON or YAML. Each entry is either the hazard text or a mapping of the ledger's own
columns:

```yaml
entries:
  - { row: 1, 隐患描述: 炼钢连铸流程未设置事故钢水罐, 整改措施: 增设事故钢水罐, 整改责任人: 张工 }
  - { row: 2, 隐患描述: 液氨制冷机房未设置氨气泄漏监测报警装置 }
```

The text is read from the first of `隐患描述`, `隐患内容`, `问题描述`, `检查内容`, `描述`, `text`,
`description`, `content`, `hazard` that the row carries. **If none of those columns is present the
reader refuses rather than guessing** — an earlier version promoted the longest field to "the hazard
text", which silently turned a serial number into a finding.

## Rule sources

Rule data lives in `rules/hidden-risk-map.yaml`. Every rule carries a document, a document number, a
clause in the source's own numbering, a verbatim excerpt and the URL the excerpt was read from. The
loader enforces that an excerpt is a real quotation of at least eight characters, and that a check
resting only on a general principle or a local policy can never be declared `error`.

The clauses quoted come from **应急管理部令第10号**. The article table covers the three general
enterprise situations (article 3) and the industry articles (articles 4–14). The keyword lists were
written for this plugin and are labelled as such in the pack, because the standard has no keyword list
— a test asserts that the pack says so.

Two findings shaped this pack:

1. **The standard was replaced** (2017 version repealed by article 15 of the 2023 order), so only
   current article numbers are cited.
2. **Article 2 hands four hazard types to other regulations.** Hazardous chemicals, fire, gas and
   special equipment are judged under *other* provisions, so `HR-002` reports those rows as
   "check the corresponding regulation" rather than mapping them here.

## Troubleshooting

- **Most rows are reported as unmapped.** That is the plugin working: either your ledger's wording is
  outside the keyword table (add the terms) or those rows genuinely fall under another regime (check
  `HR-002`'s output).
- **The industry check never runs.** `industry` is empty. Set it, or leave the check off knowingly.
- **`HR-003` never runs.** `requiredFields` is empty, and its note records that no verbatim national
  clause for remediation-closure fields was verified — so the rule ships off rather than inventing one.
- **The reader refuses a ledger it used to accept.** It found none of the known description columns.
  The error names the columns it saw; rename one to a known name, or use the `entries` list form.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`;
  if your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-hidden-risk-map@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, paired fixtures per rule
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-hidden-risk-map   # refresh src/shared from ../_shared
```

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
