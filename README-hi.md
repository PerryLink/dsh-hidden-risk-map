# dsh-hidden-risk-map — सुरक्षा-जोखिम रजिस्टर की प्रविष्टियों का बृहत् दुर्घटना-जोखिम निर्धारण मानक के संभावित अनुच्छेदों से मिलान

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-hidden-risk-map` एक सुरक्षा-जोखिम रजिस्टर पढ़ता है — हर दर्ज जोखिम की एक पंक्ति, उन स्तंभों के साथ जो वह रजिस्टर वास्तव में रखता है — और `隐患描述` जैसे क्षेत्रों के पाठ पर शब्दशः कीवर्ड मिलान द्वारा हर पंक्ति को चीनी बृहत् दुर्घटना-जोखिम निर्धारण मानक (《工贸企业重大事故隐患判定标准》, 应急管理部令第10号) के संभावित अनुच्छेदों तक ले जाता है, और किसी निर्णय के बजाय रजिस्टर की अपनी कमियाँ दर्ज करता है: वे पंक्तियाँ जो किसी अनुच्छेद से मेल नहीं खाईं, वे मिलान-पंक्तियाँ जिनका अनुच्छेद किसी दूसरे उद्योग का है या खतरनाक रसायन, अग्नि, गैस या विशेष उपकरण से जुड़ा है जिन्हें अनुच्छेद 2 अन्य प्रावधानों को सौंपता है, वे मिलान-पंक्तियाँ जिनमें संस्था द्वारा कॉन्फ़िगर किए गए सुधार-समापन क्षेत्र नहीं हैं, और वे अनुच्छेद जिन्हें कॉन्फ़िगर की गई सीमा से अधिक पंक्तियाँ छूती हैं। हर निष्कर्ष उस अनुच्छेद का नाम लेता है जिससे वह आया; परिणाम समीक्षा के लिए सुराग हैं, कीवर्ड तालिका एक संपादकीय सहायता है मानक का पाठ नहीं, और जो जाँच चल नहीं सकी वह चुपचाप पास होने के बजाय `skipped` में अपना कारण बताती है।

## आउटपुट कैसा दिखता है

![Terminal demo of dsh-hidden-risk-map: real output over its HR-004 fixture](https://raw.githubusercontent.com/PerryLink/dsh-hidden-risk-map/main/docs/assets/dsh-hidden-risk-map-demo.png)

इस प्लगइन का अपने ही `HR-004` टेस्ट फ़िक्स्चर पर वास्तविक आउटपुट — कोई नकली चित्र नहीं। नियम-पैक उद्धरण नहीं गढ़ता, इसलिए हर निष्कर्ष लागू किए गए खंड का नाम और यह भी बताता है कि उसका मूल पाठ इस बार प्राप्त नहीं हुआ।

## यह किन सवालों का जवाब देता है

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
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-hidden-risk-map
dsh --profile <name> --dump-config | grep 'dsh-hidden-risk-map'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-hidden-risk-map contributors.
