# dsh-hidden-risk-map — Cotejo de asientos de un registro de riesgos con los artículos candidatos de la norma de determinación de riesgos mayores

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
```


[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-hidden-risk-map?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-hidden-risk-map?ref=badge)

`dsh-hidden-risk-map` lee un registro de riesgos —una fila por riesgo registrado, con las columnas que ese registro realmente trae— y lleva cada fila a los artículos candidatos de la norma china de determinación de riesgos mayores (《工贸企业重大事故隐患判定标准》, 应急管理部令第10号) mediante coincidencia literal de palabras clave sobre el texto de campos como `隐患描述`, e informa de las carencias del propio registro, no de un juicio: las filas que no coincidieron con ningún artículo, las filas cuya coincidencia pertenece a otra industria o toca productos químicos peligrosos, incendio, gas o equipo especial que el artículo 2 remite a otras disposiciones, las filas coincidentes a las que faltan los campos de cierre de la corrección configurados por la institución, y los artículos golpeados por más filas que el tope configurado. Cada hallazgo nombra el artículo del que procede; el resultado son pistas para revisión, la tabla de palabras clave es una ayuda editorial y no texto de la norma, y la comprobación que no pudo ejecutarse expone su motivo en `skipped` en lugar de pasar en silencio.

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

## Cómo se ve la salida

![Diagrama de flujo de dsh-hidden-risk-map: llamada → plugin → resultado.](docs/assets/dsh-hidden-risk-map-flow.svg)

*Resumen del flujo: llamada → plugin → resultado. Los ejemplos siguientes usan la superficie de comandos real.*


Salida real de este plugin sobre su propio fixture de prueba `HR-004` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

### Ejemplos

La tabla siguiente es el conjunto de ejemplos: la primera fila es el caso detallado y las demás son casos breves.

#### Salida detallada

**Herramienta** `hidden_risk_map`

**Entrada**

~~~json
{"entries":[{"row":1,"隐患描述":"车间地面有一处油污未及时清理"}]}
~~~
 
**Salida**

~~~json
{
  "id": "dsh-hidden-risk-map.HR-001.e26f24c6",
  "ruleId": "HR-001",
  "severity": "warn",
  "locator": {
    "column": "隐患描述",
    "row": 1
  },
  "found": "台账条目「车间地面有一处油污未及时清理」未能匹配到判定标准的任何条款关键词",
  "expected": "台账条目应能对应到判定标准的具体条款，或确认不属于该标准的适用范围",
  "fix": "人工核对：可能属于其他行业条款、属于危化品/消防/燃气/特种设备等另有规定的情形，或表述与条款用词差异较大（可在 keywords 中补充本企业习惯用词）"
}
~~~

*Observado en `tests/fixtures/HR-001/HR-001-unsafe.json (cases.json expects HR-001 count 1); run via lib/index.mjs rules/hidden-risk-map.yaml`*

| Usted pregunta | Qué responde |
|---|---|
| Se ejecutó el registro y no se marcó ningún artículo, ¿significa que no hay riesgos mayores? | No. La cifra principal de la herramienta es el número de filas que no pudo mapear, no un veredicto de cero riesgos. `HR-001` enumera cada fila cuyo texto no coincidió con ninguna palabra clave: un artículo de otra industria, un tipo de riesgo regido por otras disposiciones, o una redacción que la tabla de palabras clave aún no recoge. Solo informa de que no se pudo localizar ningún artículo, y no decide si esa fila constituye o no un riesgo mayor. |
| La exportación trae un número de serie y una fecha, pero ninguna columna llamada `隐患描述`. | El lector rechaza el material en vez de adivinar; nunca promueve el campo más largo a texto del riesgo. Si no está ninguna de `隐患描述`, `隐患内容`, `问题描述`, `检查内容`, `描述`, `text`, `description`, `content` o `hazard`, nombra las columnas que sí vio (o indica que no había ninguna) y declara que no hay texto de descripción utilizable, así que la comprobación no se ejecuta y nada —ni siquiera la lista de no mapeados de `HR-001`— se lee como aprobado. |
| La fila dice 液氨制冷机房未设置氨气泄漏监测报警装置 — ¿por qué no queda mapeada? | `HR-001` compara palabras clave de forma literal, porque decidir si una frase trata de una fuga de amoníaco corresponde al revisor y no a un juicio difuso del texto. Una fila sobre 液氨 solo se mapea cuando su tabla de palabras clave recoge esa redacción; esta tabla la incluye bajo 第十二条 (industry 使用液氨制冷). Las listas de palabras clave son una ayuda editorial escrita para este complemento, no texto de la norma: añada a `keywords` el vocabulario propio de su planta cuando la redacción difiera. |
| Una fila menciona 消防 o 特种设备, y se me cita la norma como su fundamento. | Eso es `HR-002` funcionando, y no clasifica la fila. El artículo 2 remite los productos químicos peligrosos, el incendio, el gas y el equipo especial a otras disposiciones, así que la regla cita esa frase e informa de la fila como «consulte la disposición correspondiente» en lugar de mapearla. Solo cuando el `industry` de esta instalación está configurado señala además un artículo coincidente que pertenece a otra industria; si `industry` está vacío, dice en `skipped` que no se comprobó la pertenencia sectorial en lugar de pasar en silencio. |
| Las filas del registro no traen columnas `整改措施`, `整改责任人` ni `整改完成时间`. | Eso atañe a `HR-003` solo después de configurar esos nombres: `requiredFields` vacío significa que la comprobación no se ejecuta y la regla se declara en `skipped`. Una vez configurada, se informa de toda fila coincidente a la que falte una de esas columnas. La regla comprueba que las columnas existan: no juzga si la corrección es adecuada ni si el asunto se ha cerrado. |
| Muchas filas del registro golpean 第三条, y varias parecen el mismo defecto escrito dos veces. | `HR-004` agrupa las coincidencias por artículo e informa cuando un artículo recibe más filas de las que permite `maxHitsPerClause`, con la lista de números de fila. Es una pista de nivel `info` para revisión humana: decidir si eso es un registro duplicado o un defecto sistemático sigue siendo del revisor. Un `maxHitsPerClause` sin configurar (0) significa que la regla no se ejecuta, y lo dice en `skipped`. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-rc.2`. **`engines.dsh` se declara como `>=0.2.1-0 <0.3.0`** y el host lo aplica desde 0.2.1 |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native` y `ptc`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/hidden-risk-map.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hidden-risk-map
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## PerryLink DSH Plugin Family

Este proyecto forma parte de la familia de plugins de DeepSeek Harness de [PerryLink](https://github.com/PerryLink). El registro permanece plegado abajo para que cada README conserve una primera pantalla corta; expándelo para ver cada fila y su estado.

<details>
<summary>Expandir todos los plugins</summary>

| Plugin | Estado |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 CONGELADO — ver el README del repositorio |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRADO — ver el README del repositorio |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRADO — ver el README del repositorio |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRADO — ver el README del repositorio |

</details>

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
