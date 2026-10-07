/**
 * Input contract for the major-hazard clause mapper.
 *
 * The material is a safety ledger: one row per recorded hazard, with the fields a
 * real ledger carries. The mapper's output is a *candidate* clause per row — the
 * judgement whether something is a major accident hazard stays with the people who
 * inspected the site.
 */

/** One ledger row. */
export interface LedgerEntry {
  /** 1-based row number in the source, excluding the header. */
  row: number
  /** Free text of the hazard as recorded. */
  text: string
  /** Values keyed by the source's own column names. */
  fields: Record<string, string>
  /** Row number as declared in the source, when it differs from the position. */
  declaredRow?: number
}

/** The whole normalized input. */
export interface HazardLedgerInput {
  target: string
  entries: LedgerEntry[]
  /** Column names the reader saw, in order. */
  columns: string[]
  warnings: string[]
}

/** One clause of the determination standard, as declared in the rule pack. */
export interface ClauseSpec {
  /** Article number, e.g. `第四条`. */
  article: string
  /** Industry or topic the article applies to. */
  industry: string
  /** Verbatim opening of the article. */
  excerpt: string
  /** Terms that select this article. */
  keywords: string[]
}
