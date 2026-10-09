# dsh-hidden-risk-map — 安全隐患台账条目到重大事故隐患判定标准候选条款的映射核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hidden-risk-map` 读取一份安全隐患台账——每条已登记隐患一行，带台账实际有的列——按字面关键词匹配 `隐患描述` 一类字段的文字，把每一行指向《工贸企业重大事故隐患判定标准》的候选条款，并报出台账自身的缺口而不是任何结论：完全没有匹配到条款的行、命中的条款属于其他行业或涉及判定标准第二条交给其他规定的危险化学品、消防、燃气、特种设备事项的行、命中条目缺少本机构配置的整改闭环字段的行、以及被超过配置上限的条目数命中的条款。每条发现都注明它来自哪一条条款；输出只供人工复核，台账的关键词表是人工归纳的检索词而不是标准原文，无法执行的检查在 `skipped` 中说明原因，而不是静默通过。

## 实际输出长什么样

![Terminal demo of dsh-hidden-risk-map: real output over its HR-004 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hidden-risk-map/main/docs/assets/dsh-hidden-risk-map-demo.png)

本插件对自己 `HR-004` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 台账跑完了，一条条款都没报出来，是不是就没有重大事故隐患？ | 不是。这个工具的头号数字是「没能映射到条款的行数」，不是「零隐患」的结论。`HR-001` 会把文字匹配不到任何条款关键词的行逐条列出：可能属于其他行业条款、属于另有规定的情形，或表述与关键词表用词不同。它只指出「定位不到条款」这一事实，不判断该行是否构成重大事故隐患。 |
| 导出的台账里有编号、有日期，就是没有叫 `隐患描述` 的列。 | 读取器会拒绝这份材料，不猜。它不会把最长的字段当成隐患文本。`隐患描述`、`隐患内容`、`问题描述`、`检查内容`、`描述`、`text`、`description`、`content`、`hazard` 一个都没有时，它会列出实际看到的列名（或说明一列都没有），并说明没有可用的隐患描述文本，因此检查不执行——连 `HR-001` 的未映射清单也不会被读成「通过」。 |
| 某行写的是「液氨制冷机房未设置氨气泄漏监测报警装置」，为什么没有映射到条款？ | `HR-001` 按字面匹配关键词：「这句话是不是在说氨气泄漏」属于复核人的判断，不做模糊语义匹配。含「液氨」的行只有在你的关键词表收录了这种用词时才会命中；本规则库在第十二条（industry 使用液氨制冷）下收了它。关键词表是人工归纳的检索词、不是标准原文，用词不同时请把本企业习惯用词补进 `keywords`。 |
| 某行涉及消防或特种设备，却被引了《工贸企业重大事故隐患判定标准》作为依据。 | 这正是 `HR-002` 在起作用，它不给该行定性。判定标准第二条把危险化学品、消防（火灾）、燃气、特种设备交给其他规定，所以本条引用这句原文，把该行报成「改查相应规定」，而不是映射。只有配置了本机构的 `industry` 之后，它才会另外报出「命中条款属于其他行业」；`industry` 留空时，它在 `skipped` 里说明行业归属未核对，而不是静默通过。 |
| 台账里没有 `整改措施`、`整改责任人`、`整改完成时间` 这几列。 | 配置了这几个字段名之后才轮到 `HR-003`：`requiredFields` 留空表示本条不执行，并在 `skipped` 里自报。配置之后，命中条款却缺了其中某列的行会被报出。本条只核对字段是否存在，不判断整改是否合格、是否已销号。 |
| 台账里很多行都命中第三条，其中几条看着像同一个缺陷写了两遍。 | `HR-004` 按条款归集命中，当某一条款被超过 `maxHitsPerClause` 条台账命中时报出，并列出命中行号。它是 `info` 级的提示线索：究竟是不是重复登记、是不是系统性缺陷，仍需人工判断。`maxHitsPerClause` 未配置（0）时本条不执行，并在 `skipped` 里说明。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《工贸企业重大事故隐患判定标准》 | 应急管理部令第10号 | HR-001, HR-002, HR-003, HR-004 |

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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/hidden-risk-map.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hidden-risk-map
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
