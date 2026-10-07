/**
 * Reader for the hazard ledger.
 *
 * The material is JSON or YAML with an `entries` list, where each entry is either
 * a string (the hazard text) or a mapping of the export's own columns. A flat
 * `fields` mapping of column name to value is also accepted when the caller has
 * already flattened one row.
 */

import { YamlSubsetError, parseYaml } from './shared/yaml.ts'
import type { HazardLedgerInput, LedgerEntry } from './model.ts'

/** Raised when the material cannot be read at all. */
export class MaterialError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'MaterialError'
  }
}

/** Column names the reader will look at first for the hazard text. */
const TEXT_COLUMNS = ['隐患描述', '隐患内容', '问题描述', '检查内容', '描述', 'text', 'description', 'content', 'hazard']

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function text(value: unknown): string | undefined {
  if (value === undefined || value === null) return undefined
  if (typeof value === 'string') return value.trim() === '' ? undefined : value.trim()
  if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  if (typeof value === 'boolean') return String(value)
  return undefined
}

/**
 * Pick the hazard text out of a row's fields.
 *
 * Only the known description column names are consulted. Guessing by field
 * length was tempting but wrong: it silently promoted a serial number or a date
 * to "the hazard text", which then matched no clause and looked like a finding.
 * If none of the known columns is present the caller is told which names to use.
 */
function pickText(fields: Record<string, string>): string {
  for (const column of TEXT_COLUMNS) {
    const value = fields[column]
    if (value !== undefined && value !== '') return value
  }
  return ''
}

/** Turn one raw entry into a ledger row. */
function parseEntry(raw: unknown, index: number): LedgerEntry {
  if (typeof raw === 'string') {
    const value = text(raw)
    if (value === undefined) throw new MaterialError(`entries[${index}] 为空`)
    return { row: index + 1, text: value, fields: { 隐患描述: value } }
  }
  if (!isRecord(raw)) throw new MaterialError(`entries[${index}] 必须是映射或字符串`)
  const fields: Record<string, string> = {}
  for (const [key, value] of Object.entries(raw)) {
    // Keep the key even when the cell is blank: which columns the export carries
    // is what tells the reader whether it was asked for the right shape at all.
    if (value === undefined || value === null) continue
    fields[key] = typeof value === 'string' ? value.trim() : (text(value) ?? '')
  }
  const declared = text(raw.row)
  const entry: LedgerEntry = {
    row: declared !== undefined && /^\d+$/.test(declared) ? Number.parseInt(declared, 10) : index + 1,
    text: pickText(fields),
    fields,
  }
  if (declared !== undefined && /^\d+$/.test(declared)) entry.declaredRow = Number.parseInt(declared, 10)
  return entry
}

/**
 * Parse material into the normalized input contract.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized input.
 */
export function parseMaterial(source: string, target: string): HazardLedgerInput {
  const trimmed = source.trim()
  if (trimmed === '') throw new MaterialError('材料为空')
  let document: unknown
  if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
    try {
      document = JSON.parse(trimmed)
    } catch (error) {
      throw new MaterialError(`JSON 无法解析：${error instanceof Error ? error.message : String(error)}`)
    }
  } else {
    try {
      document = parseYaml(trimmed)
    } catch (error) {
      if (error instanceof YamlSubsetError) throw new MaterialError(`YAML 无法解析：${error.message}`)
      throw error
    }
  }

  const warnings: string[] = []
  let list: unknown
  if (Array.isArray(document)) list = document
  else if (isRecord(document)) list = document.entries ?? document.rows
  if (list === undefined || list === null) throw new MaterialError('材料缺少 entries 列表，无法执行检查')
  if (!Array.isArray(list)) throw new MaterialError('entries 必须是列表')
  if (list.length === 0) throw new MaterialError('entries 为空列表，无法执行检查')

  const entries = list.map((entry, index) => parseEntry(entry, index))
  const columns = [...new Set(entries.flatMap((entry) => Object.keys(entry.fields)))]
  if (!TEXT_COLUMNS.some((column) => columns.includes(column))) {
    throw new MaterialError(
      `材料中没有可识别的隐患描述列，已识别的列名为：${columns.join(' / ') || '（无）'}；` +
        `请把描述文本放在以下任一列中：${TEXT_COLUMNS.join(' / ')}`,
    )
  }

  const usable = entries.filter((entry) => entry.text.trim() !== '')
  if (usable.length === 0) {
    throw new MaterialError(
      `台账中有 ${entries.length} 条记录，但都没有可用的隐患描述文本，无法执行检查；请确认导出内容或补填描述`,
    )
  }
  if (usable.length < entries.length) {
    warnings.push(`有 ${entries.length - usable.length} 条台账没有可用的隐患描述文本，这些条目无法做条款映射`)
  }

  return { target, entries, columns, warnings }
}
