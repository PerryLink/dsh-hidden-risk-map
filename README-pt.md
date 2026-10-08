# dsh-hidden-risk-map — Correspondência entre linhas de um registo de riscos e os artigos candidatos da norma de determinação de riscos maiores

`dsh-hidden-risk-map` lê um registo de riscos —uma linha por risco registado, com as colunas que esse registo realmente traz— e encaminha cada linha para os artigos candidatos da norma chinesa de determinação de riscos maiores (《工贸企业重大事故隐患判定标准》, 应急管理部令第10号) através de correspondência literal de palavras-chave sobre o texto de campos como `隐患描述`, e reporta as lacunas do próprio registo, não um juízo: as linhas que não corresponderam a artigo nenhum, as linhas cuja correspondência pertence a outra indústria ou toca produtos químicos perigosos, incêndio, gás ou equipamento especial que o artigo 2 remete para outras disposições, as linhas correspondidas às quais faltam os campos de fecho da correção configurados pela instituição, e os artigos atingidos por mais linhas do que o limite configurado. Cada achado nomeia o artigo de onde veio; o resultado são pistas para revisão, a tabela de palavras-chave é um auxiliar editorial e não texto da norma, e a verificação que não pôde ser executada declara o motivo em `skipped` em vez de passar em silêncio.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| O registo foi executado e nenhum artigo foi assinalado — isso significa que não há riscos maiores? | Não. O número principal da ferramenta é a contagem de linhas que não conseguiu mapear, não um veredicto de zero riscos. `HR-001` lista cada linha cujo texto não correspondeu a nenhuma palavra-chave: um artigo de outra indústria, um tipo de risco regido por outras disposições, ou uma redação que a tabela de palavras-chave ainda não cobre. Apenas informa que não foi possível localizar artigo algum, e não decide se essa linha constitui ou não um risco maior. |
| A exportação traz um número de série e uma data, mas nenhuma coluna chamada `隐患描述`. | O leitor recusa o material em vez de adivinhar; nunca promove o campo mais longo a texto do risco. Se não estiver nenhuma de `隐患描述`, `隐患内容`, `问题描述`, `检查内容`, `描述`, `text`, `description`, `content` ou `hazard`, nomeia as colunas que viu (ou indica que não havia nenhuma) e declara que não existe texto de descrição utilizável, pelo que a verificação não é executada e nada — nem a lista de não mapeados de `HR-001` — é lido como aprovação. |
| A linha diz 液氨制冷机房未设置氨气泄漏监测报警装置 — porque não é mapeada? | `HR-001` compara palavras-chave de forma literal, porque decidir se uma frase fala de fuga de amoníaco cabe ao revisor e não a um juízo difuso do texto. Uma linha sobre 液氨 só é mapeada quando a sua tabela de palavras-chave contém essa redação; esta tabela inclui-a em 第十二条 (industry 使用液氨制冷). As listas de palavras-chave são um auxiliar editorial escrito para este complemento, não texto da norma: acrescente a `keywords` o vocabulário da sua instalação quando a redação diferir. |
| Uma linha menciona 消防 ou 特种设备, e citam-me a norma como seu fundamento. | Isso é o `HR-002` a funcionar, e não classifica a linha. O artigo 2 remete os produtos químicos perigosos, o incêndio, o gás e o equipamento especial para outras disposições, por isso a regra cita essa frase e reporta a linha como «consulte a disposição correspondente» em vez de a mapear. Só quando o `industry` desta instalação está configurado assinala também um artigo correspondido que pertence a outra indústria; se `industry` estiver vazio, diz em `skipped` que a pertença setorial não foi verificada em vez de passar em silêncio. |
| As linhas do registo não trazem colunas `整改措施`, `整改责任人` nem `整改完成时间`. | Isso só diz respeito ao `HR-003` depois de configurar esses nomes: `requiredFields` vazio significa que a verificação não é executada e a regra declara-se em `skipped`. Uma vez configurada, cada linha correspondida à qual falte uma dessas colunas é reportada. A regra verifica que as colunas existem: não julga se a correção é adequada nem se o assunto foi encerrado. |
| Muitas linhas do registo atingem 第三条, e várias parecem o mesmo defeito escrito duas vezes. | `HR-004` agrupa as correspondências por artigo e reporta quando um artigo recebe mais linhas do que `maxHitsPerClause` permite, com a lista dos números de linha. É uma pista de nível `info` para revisão humana: decidir se isso é um registo duplicado ou um defeito sistemático continua a ser do revisor. Um `maxHitsPerClause` não configurado (0) significa que a regra não é executada, e di-lo em `skipped`. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/hidden-risk-map.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hidden-risk-map
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
