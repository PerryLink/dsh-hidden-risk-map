# dsh-hidden-risk-map — Cotejo de asientos de un registro de riesgos con los artículos candidatos de la norma de determinación de riesgos mayores

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hidden-risk-map` lee un registro de riesgos —una fila por riesgo registrado, con las columnas que ese registro realmente trae— y lleva cada fila a los artículos candidatos de la norma china de determinación de riesgos mayores (《工贸企业重大事故隐患判定标准》, 应急管理部令第10号) mediante coincidencia literal de palabras clave sobre el texto de campos como `隐患描述`, e informa de las carencias del propio registro, no de un juicio: las filas que no coincidieron con ningún artículo, las filas cuya coincidencia pertenece a otra industria o toca productos químicos peligrosos, incendio, gas o equipo especial que el artículo 2 remite a otras disposiciones, las filas coincidentes a las que faltan los campos de cierre de la corrección configurados por la institución, y los artículos golpeados por más filas que el tope configurado. Cada hallazgo nombra el artículo del que procede; el resultado son pistas para revisión, la tabla de palabras clave es una ayuda editorial y no texto de la norma, y la comprobación que no pudo ejecutarse expone su motivo en `skipped` en lugar de pasar en silencio.

## Cómo se ve la salida

![Terminal demo of dsh-hidden-risk-map: real output over its HR-004 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hidden-risk-map/main/docs/assets/dsh-hidden-risk-map-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `HR-004` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

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
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
