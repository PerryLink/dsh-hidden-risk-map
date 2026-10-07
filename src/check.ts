/**
 * Pure check core: `(input, ruleset, options) => Report`.
 *
 * No plugin context, no I/O, no clock and no model access, so the whole rule set
 * is unit-testable without credentials. Every finding carries the verbatim
 * clause that produced it, and every check that could not run is reported in
 * `skipped` so an empty issue list can never be read as "nothing is wrong".
 *
 * What this plugin produces is a **candidate mapping**: ledger row to clause of
 * the determination standard. Deciding whether something IS a major accident
 * hazard needs a site inspection and professional judgement, so the mappings are
 * reported as leads for review, never as conclusions.
 */

import { disabledAsSkipped, formatBasis } from './shared/rules.ts'
import { paramNumber, paramStrings, ruleById } from './shared/ruleset.ts'
import { issueId, makeReport } from './shared/report.ts'
import type { Issue, Locator, Report, Skipped } from './shared/report.ts'
import type { Ruleset } from './shared/rules.ts'
import type { ClauseSpec, HazardLedgerInput, LedgerEntry } from './model.ts'

/** Options that come from the plugin configuration rather than the rule pack. */
export interface CheckOptions {
  plugin: string
  checkedAt: string
  disabledRules: readonly string[]
  onlyRules: readonly string[]
  skipNotes?: string
}

interface RuleContext {
  input: HazardLedgerInput
  ruleset: Ruleset
  issues: Issue[]
  skipped: Skipped[]
  fired: Set<string>
  skipReasons: Map<string, string>
  add(ruleId: string, locator: Locator, found: string, expected: string, fix?: string): void
  skip(ruleId: string, reason: string): void
}

/** One row-to-clause match. */
interface Match {
  entry: LedgerEntry
  clause: ClauseSpec
  /** The keyword that selected this clause. */
  keyword: string
}

function locatorOf(entry: LedgerEntry, column?: string): Locator {
  const locator: Locator = { row: entry.row }
  if (column !== undefined) locator.column = column
  return locator
}

function basisOf(ruleset: Ruleset, ruleId: string): string {
  const rule = ruleById(ruleset, ruleId)
  return formatBasis(rule.basis, rule.alsoBasis ?? [])
}

function makeAdd(context: Omit<RuleContext, 'add' | 'skip'>): RuleContext['add'] {
  return (ruleId, locator, found, expected, fix) => {
    const rule = ruleById(context.ruleset, ruleId)
    const issue: Issue = {
      id: issueId(context.ruleset.plugin, ruleId, locator),
      ruleId,
      severity: rule.severity,
      locator,
      found,
      expected,
      basis: formatBasis(rule.basis, rule.alsoBasis ?? []),
    }
    if (fix !== undefined) issue.fix = fix
    context.issues.push(issue)
    context.fired.add(ruleId)
  }
}

/** Read the clause catalogue out of the rule pack. */
function clauseSpecs(ruleset: Ruleset, ruleId: string): ClauseSpec[] {
  const rule = ruleById(ruleset, ruleId)
  const raw = rule.params.clauses
  if (!Array.isArray(raw)) return []
  const out: ClauseSpec[] = []
  for (const entry of raw) {
    if (typeof entry !== 'object' || entry === null) continue
    const record = entry as Record<string, unknown>
    if (typeof record.article !== 'string' || record.article.trim() === '') continue
    const keywords = Array.isArray(record.keywords)
      ? record.keywords.filter((value): value is string => typeof value === 'string' && value.trim() !== '')
      : []
    if (keywords.length === 0) continue
    out.push({
      article: record.article.trim(),
      industry: typeof record.industry === 'string' ? record.industry.trim() : '',
      excerpt: typeof record.excerpt === 'string' ? record.excerpt.trim() : '',
      keywords: keywords.map((value) => value.trim()),
    })
  }
  return out
}

/**
 * Map every ledger row onto the clauses whose keywords it contains.
 *
 * Keyword matching is literal on purpose: a fuzzy judgement about whether a
 * ledger sentence "is about" molten-metal water accumulation is exactly the kind
 * of call that must stay with the reviewer.
 */
function mapEntries(context: RuleContext): Match[] {
  const specs = clauseSpecs(context.ruleset, 'HR-001')
  const matches: Match[] = []
  for (const entry of context.input.entries) {
    const haystack = `${entry.text}\n${Object.values(entry.fields).join('\n')}`
    for (const clause of specs) {
      const keyword = clause.keywords.find((term) => haystack.includes(term))
      if (keyword === undefined) continue
      matches.push({ entry, clause, keyword })
      break
    }
  }
  return matches
}

/**
 * HR-001 — ledger rows that cannot be located in the determination standard.
 *
 * This is the plugin's core value: it turns "the ledger was checked and no major
 * hazard was flagged" into "these 7 rows could not be mapped to any clause, please
 * look at them by hand".
 */
function checkUnmapped(context: RuleContext): void {
  const ruleId = 'HR-001'
  const specs = clauseSpecs(context.ruleset, ruleId)
  if (specs.length === 0) {
    context.skip(ruleId, '规则库未配置 clauses：条款关键词表随判定标准版本变化，本条不执行；请在本机构规则库中填写')
    return
  }
  const usable = context.input.entries.filter((entry) => entry.text.trim() !== '')
  if (usable.length === 0) {
    context.skip(ruleId, '台账中没有可用的隐患描述文本，无法做条款映射')
    return
  }
  const matches = mapEntries(context)
  const mapped = new Set(matches.map((match) => match.entry.row))
  for (const entry of usable) {
    if (mapped.has(entry.row)) continue
    context.add(
      ruleId,
      locatorOf(entry, '隐患描述'),
      `台账条目「${entry.text.slice(0, 80)}」未能匹配到判定标准的任何条款关键词`,
      '台账条目应能对应到判定标准的具体条款，或确认不属于该标准的适用范围',
      '人工核对：可能属于其他行业条款、属于危化品/消防/燃气/特种设备等另有规定的情形，或表述与条款用词差异较大（可在 keywords 中补充本企业习惯用词）',
    )
  }
}

/** HR-002 — a matched clause must belong to the deployment's industry. */
function checkIndustry(context: RuleContext): void {
  const ruleId = 'HR-002'
  const rule = ruleById(context.ruleset, ruleId)
  const industry = typeof rule.params.industry === 'string' ? rule.params.industry.trim() : ''
  const matches = mapEntries(context)
  if (matches.length === 0) {
    context.skip(ruleId, '台账条目未命中任何条款，无法核对行业归属')
    return
  }
  const otherRegimes = paramStrings(rule, 'otherRegimes', ['危险化学品', '消防', '燃气', '特种设备'])
  for (const match of matches) {
    const haystack = `${match.entry.text}\n${Object.values(match.entry.fields).join('\n')}`
    const regime = otherRegimes.find((term) => haystack.includes(term))
    if (regime !== undefined) {
      context.add(
        ruleId,
        locatorOf(match.entry, '隐患描述'),
        `条目命中「${match.clause.article}」（${match.clause.industry}），且涉及「${regime}」`,
        '工贸企业内涉及危险化学品、消防（火灾）、燃气、特种设备等方面的重大事故隐患判定另有规定的，适用其规定',
        `按判定标准第二条，本条的${regime}事项应改查相应规定，本条映射仅供参考`,
      )
      continue
    }
    if (industry === '') continue
    if (match.clause.industry === '' || match.clause.industry === industry) continue
    context.add(
      ruleId,
      locatorOf(match.entry, '隐患描述'),
      `条目命中「${match.clause.article}」，该条适用于「${match.clause.industry}」，而本机构配置的行业为「${industry}」`,
      '应核对是否为本企业所属行业的判定条款',
      '核对命中条款是否适用；也可能是条目本身跨行业，或本机构 industry 配置需要调整',
    )
  }
  if (industry === '') {
    context.skip(ruleId, '规则库未配置 industry（本企业所属行业），未核对命中条款的行业归属')
  }
}

/** HR-003 — a matched row should carry the configured remediation fields. */
function checkRemediationFields(context: RuleContext): void {
  const ruleId = 'HR-003'
  const rule = ruleById(context.ruleset, ruleId)
  const required = paramStrings(rule, 'requiredFields', [])
  if (required.length === 0) {
    context.skip(
      ruleId,
      '规则库未配置 requiredFields：本条的直接依据应来自隐患整改闭环管理制度，本次未逐字核实到具体条款；如需启用请填写本机构要求的字段名',
    )
    return
  }
  const matches = mapEntries(context)
  if (matches.length === 0) {
    context.skip(ruleId, '台账条目未命中任何条款，无需核对整改闭环信息')
    return
  }
  for (const match of matches) {
    const missing = required.filter((field) => {
      const value = match.entry.fields[field]
      return value === undefined || value.trim() === ''
    })
    if (missing.length === 0) continue
    context.add(
      ruleId,
      locatorOf(match.entry),
      `条目命中「${match.clause.article}」，但缺 ${missing.join('、')}`,
      `按本机构配置，命中判定条款的条目应填写 ${required.join('、')}`,
      '补齐整改闭环信息；本插件只核对字段是否存在，不判断整改是否合格',
    )
  }
}

/** HR-004 — a clause hit by many rows is worth a look. */
function checkClauseConcentration(context: RuleContext): void {
  const ruleId = 'HR-004'
  const rule = ruleById(context.ruleset, ruleId)
  const ceiling = paramNumber(rule, 'maxHitsPerClause', 0)
  if (ceiling <= 0) {
    context.skip(ruleId, '规则库未配置 maxHitsPerClause，本条不执行')
    return
  }
  const matches = mapEntries(context)
  if (matches.length === 0) {
    context.skip(ruleId, '台账条目未命中任何条款，无法统计条款集中度')
    return
  }
  const byArticle = new Map<string, Match[]>()
  for (const match of matches) {
    const bucket = byArticle.get(match.clause.article)
    if (bucket === undefined) byArticle.set(match.clause.article, [match])
    else bucket.push(match)
  }
  for (const [article, bucket] of byArticle) {
    if (bucket.length <= ceiling) continue
    const first = bucket[0] as Match
    context.add(
      ruleId,
      locatorOf(first.entry),
      `判定条款「${article}」被 ${bucket.length} 条台账命中（行号：${bucket.map((match) => match.entry.row).join('、')}）`,
      `同一条款被超过 ${ceiling} 条台账命中时应人工确认是否为重复登记或系统性缺陷`,
      '核对是否为重复登记；若确为多处同类缺陷，应作为系统性问题单独分析',
    )
  }
}

const CHECKERS: readonly ((context: RuleContext) => void)[] = [
  checkUnmapped,
  checkIndustry,
  checkRemediationFields,
  checkClauseConcentration,
]

/**
 * Run the whole rule pack against one hazard ledger.
 * @param input - normalized ledger.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value and rule selection.
 * @returns the report, with `skipped` listing every check that did not run.
 */
export function runCheck(input: HazardLedgerInput, ruleset: Ruleset, options: CheckOptions): Report {
  const disabled = new Set([...ruleset.disabled, ...options.disabledRules])
  const only = new Set(options.onlyRules)
  const base = {
    input,
    ruleset,
    issues: [] as Issue[],
    skipped: [] as Skipped[],
    fired: new Set<string>(),
    skipReasons: new Map<string, string>(),
  }
  const context: RuleContext = {
    ...base,
    add: makeAdd(base),
    skip: (ruleId, reason) => {
      base.skipReasons.set(ruleId, reason)
    },
  }

  for (const checker of CHECKERS) checker(context)

  const withNote = (reason: string): string => (options.skipNotes === undefined ? reason : `${reason}；${options.skipNotes}`)
  const skipped: Skipped[] = disabledAsSkipped(ruleset, [...disabled], withNote('该规则在当前配置中被禁用'))
  const already = new Set(skipped.map((entry) => entry.rule))
  for (const [ruleId, reason] of base.skipReasons) {
    if (already.has(ruleId)) continue
    if (disabled.has(ruleId) || (options.onlyRules.length > 0 && !only.has(ruleId))) continue
    skipped.push({ rule: ruleId, reason: withNote(reason) })
    already.add(ruleId)
  }
  for (const rule of ruleset.rules) {
    if (disabled.has(rule.id) || base.fired.has(rule.id) || already.has(rule.id)) continue
    if (options.onlyRules.length > 0 && !only.has(rule.id)) continue
    skipped.push({ rule: rule.id, reason: withNote('材料满足该检查的前置条件且未发现差异条目') })
  }
  if (options.onlyRules.length > 0) {
    const notSelected = ruleset.rules.filter((rule) => !only.has(rule.id) && !disabled.has(rule.id))
    if (notSelected.length > 0) {
      skipped.push({
        rule: notSelected.map((rule) => rule.id).join(','),
        reason: withNote(`本次调用通过 only 参数把执行范围限制为 ${[...only].join(', ')}，上列规则未执行`),
      })
    }
  }

  return makeReport({
    plugin: options.plugin,
    target: input.target,
    rulesetVersion: ruleset.version,
    checkedAt: options.checkedAt,
    issues: context.issues,
    skipped,
  })
}
