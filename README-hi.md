# dsh-hidden-risk-map — सुरक्षा-जोखिम रजिस्टर की प्रविष्टियों का बृहत् दुर्घटना-जोखिम निर्धारण मानक के संभावित अनुच्छेदों से मिलान

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
```


[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-hidden-risk-map?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-hidden-risk-map?ref=badge)

`dsh-hidden-risk-map` एक सुरक्षा-जोखिम रजिस्टर पढ़ता है — हर दर्ज जोखिम की एक पंक्ति, उन स्तंभों के साथ जो वह रजिस्टर वास्तव में रखता है — और `隐患描述` जैसे क्षेत्रों के पाठ पर शब्दशः कीवर्ड मिलान द्वारा हर पंक्ति को चीनी बृहत् दुर्घटना-जोखिम निर्धारण मानक (《工贸企业重大事故隐患判定标准》, 应急管理部令第10号) के संभावित अनुच्छेदों तक ले जाता है, और किसी निर्णय के बजाय रजिस्टर की अपनी कमियाँ दर्ज करता है: वे पंक्तियाँ जो किसी अनुच्छेद से मेल नहीं खाईं, वे मिलान-पंक्तियाँ जिनका अनुच्छेद किसी दूसरे उद्योग का है या खतरनाक रसायन, अग्नि, गैस या विशेष उपकरण से जुड़ा है जिन्हें अनुच्छेद 2 अन्य प्रावधानों को सौंपता है, वे मिलान-पंक्तियाँ जिनमें संस्था द्वारा कॉन्फ़िगर किए गए सुधार-समापन क्षेत्र नहीं हैं, और वे अनुच्छेद जिन्हें कॉन्फ़िगर की गई सीमा से अधिक पंक्तियाँ छूती हैं। हर निष्कर्ष उस अनुच्छेद का नाम लेता है जिससे वह आया; परिणाम समीक्षा के लिए सुराग हैं, कीवर्ड तालिका एक संपादकीय सहायता है मानक का पाठ नहीं, और जो जाँच चल नहीं सकी वह चुपचाप पास होने के बजाय `skipped` में अपना कारण बताती है।

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

## आउटपुट कैसा दिखता है

![dsh-hidden-risk-map कार्यप्रवाह आरेख: कॉल → प्लगइन → परिणाम।](docs/assets/dsh-hidden-risk-map-flow.svg)

*कार्यप्रवाह: कॉल → प्लगइन → परिणाम। नीचे के उदाहरण वास्तविक कमांड सतह का उपयोग करते हैं।*


इस प्लगइन का अपने ही `HR-004` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

### उदाहरण

नीचे दी गई तालिका उदाहरण-समुच्चय है: पहली पंक्ति विस्तृत केस है, बाकी संक्षिप्त केस हैं।

#### विस्तृत आउटपुट

**उपकरण** `hidden_risk_map`

**इनपुट**

~~~json
{"entries":[{"row":1,"隐患描述":"车间地面有一处油污未及时清理"}]}
~~~
 
**आउटपुट**

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

*स्रोत `tests/fixtures/HR-001/HR-001-unsafe.json (cases.json expects HR-001 count 1); run via lib/index.mjs rules/hidden-risk-map.yaml`*

| आपका सवाल | इसका जवाब |
|---|---|
| रजिस्टर चलाया गया और कोई अनुच्छेद चिह्नित नहीं हुआ — क्या इसका मतलब है कि कोई बृहत् दुर्घटना-जोखिम नहीं है? | नहीं। इस उपकरण का मुख्य आँकड़ा उन पंक्तियों की गिनती है जिन्हें वह मैप नहीं कर सका, «शून्य जोखिम» का निर्णय नहीं। `HR-001` हर उस पंक्ति को सूचीबद्ध करता है जिसका पाठ किसी अनुच्छेद-कीवर्ड से मेल नहीं खाया: किसी दूसरे उद्योग का अनुच्छेद, अन्य प्रावधानों में आने वाला जोखिम-प्रकार, या ऐसी शब्दावली जो कीवर्ड तालिका में अभी नहीं है। यह केवल यह बताता है कि कोई अनुच्छेद नहीं खोजा जा सका, और यह तय नहीं करता कि वह पंक्ति बृहत् दुर्घटना-जोखिम है या नहीं। |
| निर्यात में क्रमांक और दिनांक हैं, पर `隐患描述` नाम का कोई स्तंभ नहीं। | पाठक सामग्री को अस्वीकार कर देता है, अंदाज़ा नहीं लगाता; वह सबसे लंबे क्षेत्र को कभी जोखिम-पाठ नहीं मान लेता। `隐患描述`, `隐患内容`, `问题描述`, `检查内容`, `描述`, `text`, `description`, `content` या `hazard` — इनमें से कोई न हो तो वह देखे गए स्तंभों के नाम बताता है (या बताता है कि कोई नहीं था) और कहता है कि कोई उपयोगी जोखिम-विवरण पाठ नहीं है, इसलिए जाँच नहीं चलती और कुछ भी — `HR-001` की अमैप्ड सूची भी नहीं — पास के रूप में नहीं पढ़ा जाता। |
| पंक्ति में लिखा है 液氨制冷机房未设置氨气泄漏监测报警装置 — यह मैप क्यों नहीं हुई? | `HR-001` कीवर्ड का शब्दशः मिलान करता है, क्योंकि «यह वाक्य अमोनिया रिसाव के बारे में है या नहीं» यह समीक्षक का निर्णय है, पाठ का धुँधला आकलन नहीं। 液氨 वाली पंक्ति तभी मैप होती है जब आपकी कीवर्ड तालिका में वह शब्दावली हो; यह नियम-पैक उसे 第十二条 (industry 使用液氨制冷) के अंतर्गत रखता है। कीवर्ड सूचियाँ इस प्लगइन के लिए लिखी गई संपादकीय सहायता हैं, मानक का पाठ नहीं, इसलिए शब्दावली भिन्न हो तो अपने संस्थान के शब्द `keywords` में जोड़ें। |
| एक पंक्ति में 消防 या 特种设备 का उल्लेख है, और मुझे आधार के रूप में यही मानक उद्धृत किया जा रहा है। | यह `HR-002` का काम है, और यह उस पंक्ति का वर्गीकरण नहीं करता। अनुच्छेद 2 खतरनाक रसायन, अग्नि, गैस और विशेष उपकरण को अन्य प्रावधानों को सौंपता है, इसलिए यह नियम वह वाक्य उद्धृत करता है और पंक्ति को मैप करने के बजाय «संबंधित प्रावधान देखें» के रूप में दर्ज करता है। इस परिनियोजन का `industry` कॉन्फ़िगर होने पर ही यह अलग से बताता है कि मिला अनुच्छेद किसी और उद्योग का है; `industry` खाली हो तो यह `skipped` में कहता है कि उद्योग-संबद्धता की जाँच नहीं हुई, चुपचाप पास होने के बजाय। |
| रजिस्टर की पंक्तियों में `整改措施`, `整改责任人` या `整改完成时间` स्तंभ नहीं हैं। | ये नाम कॉन्फ़िगर करने के बाद ही `HR-003` लागू होता है: `requiredFields` खाली हो तो यह जाँच नहीं चलती और नियम स्वयं को `skipped` में दर्ज करता है। कॉन्फ़िगर होने पर, जिस मिलान-पंक्ति में इनमें से कोई स्तंभ न हो, वह दर्ज होती है। नियम यह देखता है कि स्तंभ मौजूद हैं — यह नहीं आँकता कि सुधार पर्याप्त है या मामला बंद हो चुका है। |
| रजिस्टर की बहुत सी पंक्तियाँ 第三条 से टकराती हैं, और कुछ तो एक ही दोष दो बार लिखा हुआ लगती हैं। | `HR-004` मिलानों को अनुच्छेद के अनुसार समूहित करता है और तब दर्ज करता है जब किसी अनुच्छेद से `maxHitsPerClause` की अनुमति से अधिक पंक्तियाँ टकराएँ, साथ में पंक्ति-संख्याएँ भी। यह मानवीय समीक्षा के लिए `info` स्तर का सुराग है: यह दोहरा प्रवेश है या व्यवस्थागत दोष, यह तय करना समीक्षक का ही काम है। `maxHitsPerClause` कॉन्फ़िगर न हो (0) तो नियम नहीं चलता, और यह `skipped` में बताता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-rc.2` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` `>=0.2.1-0 <0.3.0` के रूप में घोषित है** और 0.2.1 से होस्ट इसे लागू करता है |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native` और `ptc` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/hidden-risk-map.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-hidden-risk-map
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## PerryLink DSH Plugin Family

यह प्रोजेक्ट [PerryLink](https://github.com/PerryLink) के DeepSeek Harness प्लगइन परिवार का हिस्सा है। पूरी सूची नीचे संक्षिप्त रखी गई है ताकि हर README की पहली स्क्रीन छोटी रहे; हर पंक्ति और उसकी स्थिति देखने के लिए इसे खोलें।

<details>
<summary>सभी प्लगइन खोलें</summary>

| प्लगइन | स्थिति |
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
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 फ़्रोज़न — रिपॉज़िटरी README देखें |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 फ़्रोज़न — रिपॉज़िटरी README देखें |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 फ़्रोज़न — रिपॉज़िटरी README देखें |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 फ़्रोज़न — रिपॉज़िटरी README देखें |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 फ़्रोज़न — रिपॉज़िटरी README देखें |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 सेवानिवृत्त — रिपॉज़िटरी README देखें |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 सेवानिवृत्त — रिपॉज़िटरी README देखें |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 सेवानिवृत्त — रिपॉज़िटरी README देखें |

</details>

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
