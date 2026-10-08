import { readFile, readdir } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { loadRuleset } from '../src/shared/ruleset.ts'
import { parseMaterial } from '../src/parse.ts'
import { runCheck } from '../src/check.ts'
import { buildView } from '../src/view.ts'
import { findForbiddenWording } from '../src/shared/wording.ts'
import { addDays, diffDays, parseWallClock } from '../src/shared/datetime.ts'
import { parseYaml } from '../src/shared/yaml.ts'
import { Config as ConfigSchema } from '../src/config.ts'
import { inject, name as pluginName, resolvePackageFile, TOOL_NAME } from '../src/index.ts'
import type { Report } from '../src/shared/report.ts'
import type { CheckOptions } from '../src/check.ts'

const here = dirname(fileURLToPath(import.meta.url))
const packageRoot = resolve(here, '..')
const rulesPath = join(packageRoot, 'rules', 'hidden-risk-map.yaml')
const fixturesRoot = join(here, 'fixtures')
const CHECKED_AT = '2026-10-06T00:00:00.000Z'

interface CaseFile {
  ruleId: string
  configure?: Record<string, Record<string, unknown>>
  pairs: { name: string; material: string; expect: { ruleId: string; count: number } }[]
}

async function loadPack() {
  return loadRuleset(await readFile(rulesPath, 'utf8'))
}

function runOptions(overrides: Partial<CheckOptions> = {}): CheckOptions {
  return { plugin: pluginName, checkedAt: CHECKED_AT, disabledRules: [], onlyRules: [], ...overrides }
}

function withConfiguration(ruleset: Awaited<ReturnType<typeof loadPack>>, configure: CaseFile['configure']) {
  if (configure === undefined) return ruleset
  return {
    ...ruleset,
    rules: ruleset.rules.map((rule) =>
      configure[rule.id] === undefined ? rule : { ...rule, params: { ...rule.params, ...configure[rule.id] } },
    ),
  }
}

async function runFixture(materialText: string, target: string, configure?: CaseFile['configure']): Promise<Report> {
  const ruleset = withConfiguration(await loadPack(), configure)
  return runCheck(parseMaterial(materialText, target), ruleset, runOptions())
}

function issuesOf(report: Report, ruleId: string) {
  return report.issues.filter((issue) => issue.ruleId === ruleId)
}

async function ruleDirectories(): Promise<string[]> {
  const entries = await readdir(fixturesRoot, { withFileTypes: true })
  return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort()
}

async function readCases(directory: string): Promise<CaseFile> {
  return JSON.parse(await readFile(join(fixturesRoot, directory, 'cases.json'), 'utf8')) as CaseFile
}

describe('rule pack', () => {
  it('declares a citable basis for every rule', async () => {
    const ruleset = await loadPack()
    expect(ruleset.plugin).toBe(pluginName)
    expect(ruleset.rules.length).toBeGreaterThanOrEqual(4)
    for (const rule of ruleset.rules) {
      expect(rule.basis.document, `${rule.id} document`).not.toBe('')
      expect(rule.basis.clause, `${rule.id} clause`).not.toBe('')
      expect(rule.basis.excerpt.length, `${rule.id} excerpt`).toBeGreaterThanOrEqual(8)
      expect(rule.basis.source, `${rule.id} source`).toMatch(/^https?:\/\//)
      expect(['direct', 'derived-from-principle', 'institutional-configuration']).toContain(rule.basis.kind)
    }
  })

  it('never lets a principle-derived or locally configured check be an error', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      if (rule.basis.kind === 'derived-from-principle') expect(rule.severity, rule.id).not.toBe('error')
      if (rule.basis.kind === 'institutional-configuration') expect(rule.severity, rule.id).toBe('info')
    }
  })

  it('cites the current standard and never the superseded 2017 version', async () => {
    const ruleset = await loadPack()
    for (const rule of ruleset.rules) {
      expect(rule.basis.number, rule.id).toBe('应急管理部令第10号')
      expect(rule.basis.excerpt, rule.id).not.toContain('2017')
    }
    for (const rule of ruleset.rules) {
      for (const extra of rule.alsoBasis ?? []) expect(extra.number, rule.id).not.toContain('129')
    }
    const source = await readFile(rulesPath, 'utf8')
    expect(source).toContain('2023-05-15')
    expect(source).toContain('安监总管四〔2017〕129号')
    expect(source).toContain('不得再引 2017 版条号')
  })

  it('ships the clause catalogue with the article numbers from the standard', async () => {
    const ruleset = await loadPack()
    const catalogue = ruleset.rules.find((rule) => rule.id === 'HR-001')?.params.clauses
    expect(Array.isArray(catalogue)).toBe(true)
    const clauses = catalogue as { article: string; industry: string; keywords: string[] }[]
    expect(clauses.length).toBe(11)
    expect(clauses[0]?.article).toBe('第三条')
    expect(clauses.some((clause) => clause.industry === '机械')).toBe(true)
    for (const clause of clauses) {
      expect(clause.keywords.length, clause.article).toBeGreaterThan(0)
      expect(clause.article, clause.article).toMatch(/^第[一二三四五六七八九十]+条$/)
    }
  })

  it('states that the keyword table is an editorial aid, not standard text', async () => {
    const ruleset = await loadPack()
    const note = ruleset.rules.find((rule) => rule.id === 'HR-001')?.note ?? ''
    expect(note).toContain('人工归纳的检索词')
    expect(note).toContain('不是标准原文')
  })

  it('marks the remediation-closure rule as lacking a verbatim national clause', async () => {
    const ruleset = await loadPack()
    const remediation = ruleset.rules.find((rule) => rule.id === 'HR-003')
    expect(remediation?.params.requiredFields).toEqual([])
    expect(remediation?.note).toContain('本次未逐字核实到具体条款')
    expect(remediation?.basis.kind).toBe('derived-from-principle')
  })

  it('refuses a rule pack that overstates a principle-derived check', () => {
    const overstated = [
      'plugin: probe',
      'version: "0"',
      'rules:',
      '  - id: X-001',
      '    title: probe',
      '    severity: error',
      '    basis:',
      '      document: 《X》',
      '      number: X〔2020〕1号',
      '      clause: 第一条',
      '      excerpt: 这是一个足够长的逐字摘录示例。',
      '      kind: derived-from-principle',
      '      source: https://example.invalid/x',
    ].join('\n')
    expect(() => loadRuleset(overstated)).toThrow(/strongest permitted severity/)
  })
})

describe('paired fixtures', () => {
  it('has both a compliant and a violating sample for every rule', async () => {
    const ruleset = await loadPack()
    const covered = new Set<string>()
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      expect(cases.pairs.filter((pair) => pair.expect.count === 0).length, `${directory} compliant sample`).toBeGreaterThanOrEqual(1)
      expect(cases.pairs.filter((pair) => pair.expect.count > 0).length, `${directory} violating sample`).toBeGreaterThanOrEqual(1)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure)
        const matched = issuesOf(report, cases.ruleId)
        expect(
          matched.length,
          `${directory}/${pair.name} expected ${pair.expect.count} × ${cases.ruleId}, got ${matched.map((issue) => issue.found).join(' | ')}`,
        ).toBe(pair.expect.count)
        covered.add(cases.ruleId)
      }
    }
    for (const rule of ruleset.rules) expect(covered.has(rule.id), `covered ${rule.id}`).toBe(true)
  })

  it('gives every issue a citable basis and a stable id', async () => {
    for (const directory of await ruleDirectories()) {
      const cases = await readCases(directory)
      for (const pair of cases.pairs) {
        const material = await readFile(join(fixturesRoot, directory, pair.material), 'utf8')
        const report = await runFixture(material, pair.material, cases.configure)
        for (const issue of report.issues) {
          expect(issue.basis).toContain('「')
          expect(issue.id).toMatch(/^dsh-hidden-risk-map\.HR-\d{3}\.[0-9a-f]{8}$/)
          expect(issue.found).not.toBe('')
          expect(issue.expected).not.toBe('')
          expect(Object.keys(issue.locator).length).toBeGreaterThan(0)
        }
      }
    }
  })
})

describe('clause mapping', () => {
  it('keeps only the first matching clause per row', async () => {
    const ruleset = await loadPack()
    const material = JSON.stringify({ entries: [{ row: 1, 隐患描述: '转炉水冷元件未设置出水温度监测报警装置' }] })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions())
    // The row matches 第四条 (metallurgy); HR-001 stays quiet because a clause was found.
    expect(issuesOf(report, 'HR-001')).toHaveLength(0)
  })

  it('accepts a plain string list as the ledger', async () => {
    const input = parseMaterial(JSON.stringify(['炼钢连铸未设置事故钢水罐']), 'inline')
    expect(input.entries).toHaveLength(1)
    expect(input.entries[0]?.text).toBe('炼钢连铸未设置事故钢水罐')
  })

  it('refuses to guess which column holds the hazard text', () => {
    let message = ''
    try {
      parseMaterial(JSON.stringify([{ 序号: '1', 备注: '商场疏散通道被货物堵塞，未及时清理' }]), 'inline')
    } catch (error) {
      message = error instanceof Error ? error.message : String(error)
    }
    expect(message).toContain('没有可识别的隐患描述列')
    expect(message).toContain('备注')
  })

  it('warns rather than failing when some rows carry no text', async () => {
    const input = parseMaterial(JSON.stringify([{ 隐患描述: '粉尘涉爆除尘系统未设置泄爆装置' }, { 序号: '2' }]), 'inline')
    expect(input.warnings.join(' ')).toContain('没有可用的隐患描述文本')
  })
})

describe('skipped reporting', () => {
  it('admits that the industry check cannot run without a configured industry', async () => {
    const ruleset = await loadPack()
    const material = JSON.stringify({ entries: [{ row: 1, 隐患描述: '铸造用熔炼炉未设置紧急排放和应急储存设施' }] })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions())
    expect(report.skipped.find((entry) => entry.rule === 'HR-002')?.reason).toContain('未配置 industry')
  })

  it('names disabled rules exactly once and appends the configured note', async () => {
    const ruleset = await loadPack()
    const material = JSON.stringify({ entries: [{ row: 1, 隐患描述: '商场疏散通道被货物堵塞' }] })
    const report = runCheck(parseMaterial(material, 'inline'), ruleset, runOptions({ disabledRules: ['HR-001'], skipNotes: '本机构台账口径' }))
    const entries = report.skipped.filter((item) => item.rule === 'HR-001')
    expect(entries).toHaveLength(1)
    expect(entries[0]?.reason).toContain('禁用')
    expect(entries[0]?.reason).toContain('本机构台账口径')
  })
})

describe('report rendering', () => {
  it('never uses adjudicating wording and always carries the disclaimer', async () => {
    const material = await readFile(join(fixturesRoot, 'HR-001', 'HR-001-unsafe.json'), 'utf8')
    const report = await runFixture(material, 'HR-001-unsafe.json')
    const view = buildView(report)
    expect(findForbiddenWording(view.markdown)).toEqual([])
    expect(view.markdown).toContain('免责声明')
    expect(view.markdown).toContain('未执行的检查')
    expect(JSON.parse(view.reportJson)).toMatchObject({ plugin: pluginName, summary: report.summary })
  })
})

describe('plugin contract', () => {
  it('declares a static inject array covering every service apply touches', () => {
    expect(Array.isArray(inject)).toBe(true)
    expect(inject).toContain('tools')
  })

  it('exposes a Schemastery Config with serializable defaults', () => {
    const resolved = ConfigSchema(null)
    expect(resolved.rulesFile).toBe('rules/hidden-risk-map.yaml')
    expect(resolved.disabledRules).toEqual([])
    expect(resolved.timeoutMs).toBeGreaterThan(0)
  })

  it('resolves the packaged rule pack and rejects a missing one', () => {
    expect(resolvePackageFile('rules/hidden-risk-map.yaml')).toBe(rulesPath)
    expect(() => resolvePackageFile('rules/does-not-exist.yaml')).toThrow(/未找到/)
  })

  it('names the tool after the package family convention', () => {
    expect(TOOL_NAME).toBe('hidden_risk_map')
  })
})

describe('material reader', () => {
  it('rejects empty material instead of reporting an empty result', () => {
    expect(() => parseMaterial('   ', 'inline')).toThrow(/材料为空/)
  })

  it('rejects material without entries', () => {
    expect(() => parseMaterial('target: x', 'inline')).toThrow(/entries/)
  })

  it('rejects a ledger whose description column is present but blank in every row', () => {
    expect(() => parseMaterial(JSON.stringify([{ 隐患描述: '   ' }, { 隐患描述: '' }]), 'inline')).toThrow(/都没有可用的隐患描述文本/)
  })

  it('rejects a ledger whose rows carry none of the known description columns', () => {
    expect(() => parseMaterial(JSON.stringify([{ 序号: '1' }]), 'inline')).toThrow(/没有可识别的隐患描述列/)
  })
})

describe('shared kit', () => {
  it('parses wall-clock timestamps and rejects impossible dates', () => {
    expect(parseWallClock('2026-03-15')).toEqual({ date: '2026-03-15', time: '00:00', hasTime: false, minutes: 0 })
    expect(parseWallClock('2026-02-30')).toBeUndefined()
  })

  it('does calendar arithmetic', () => {
    expect(addDays('2026-03-31', 1)).toBe('2026-04-01')
    expect(diffDays('2026-03-01', '2026-03-06')).toBe(5)
  })

  it('reads the supported YAML subset and rejects the rest', () => {
    expect(parseYaml('a: 1\nb:\n  - x\n')).toEqual({ a: 1, b: ['x'] })
    expect(() => parseYaml('a: 1\na: 2\n')).toThrow(/duplicate/)
  })
})
