#!/usr/bin/env python3
"""README visuals for dsh-hidden-risk-map, derived from the shipped pipeline.

Every figure is tied to this repository, not to a generic checker template:

  src/index.ts   registers the `hidden_risk_map` tool; reads `file` or inline
                 `material`, resolves the packaged `rules/hidden-risk-map.yaml`
                 (config `rulesFile`), then runs parseMaterial -> runCheck ->
                 buildView with `disabledRules` / `onlyRules` / `skipNotes`.
  src/parse.ts   accepts JSON or YAML `entries[]`; the hazard text comes only
                 from the known description columns (隐患描述, 隐患内容, ...).
                 A ledger with no recognized description column is refused.
  src/check.ts   HR-001 maps each row by the first literal keyword hit in the
                 rule pack's clause table; unmatched rows become findings.
                 HR-002 reroutes rows touching the four regimes article 2 hands
                 to other provisions (危险化学品 / 消防 / 燃气 / 特种设备)
                 and checks the matched clause's industry. HR-003 checks the
                 configured remediation fields, HR-004 the per-clause hit
                 ceiling. HR-003/HR-004 are off by default and say so in
                 `skipped`.
  src/view.ts    the report has exactly two exits: `issues[]` (found / expected
                 / fix / basis) and `skipped[]` (why the check did not run);
                 the wording guard keeps the output non-adjudicating.

Outputs (idempotent overwrite):

  docs/assets/dsh-hidden-risk-map-hero-{zh,en}-{light,dark}.webp
      1440x576 Pillow banners. Left: kicker / wordmark / two value lines /
      two-line subtitle / meta / footer. Right: the real row-to-clause map as
      a seven-row ledger card. Row 03 is deliberately unmapped (HR-001), row 05
      is matched to 第十二条 and then rerouted by article 2 (HR-002). These are
      the same seven cases the flow matrix draws.

  docs/assets/dsh-hidden-risk-map-flow-v5-{light,dark}.svg
      1100x660 hand-written SVG. Grammar: a ROW-TO-CLAUSE MATRIX with two
      boundary exits, then a rule-state rail and a two-exit report ledger — not
      a row of five boxes. One pair carries the literal tokens shared by the
      five README languages.

Older single-skin assets (flow.svg, flow-light/dark.svg, hero.png, demo.*,
quickstart.png) stay untouched for external deep links. Run:

    python scripts/gen-readme-assets.py

Requires Pillow (bundled with the DSH primary runtime) and the Windows fonts
msyh.ttc / msyhbd.ttc / consola.ttf / consolab.ttf.
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-hidden-risk-map"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

SANS = "Microsoft YaHei, Noto Sans SC, PingFang SC, Segoe UI, sans-serif"
MONO = "Consolas, SFMono-Regular, ui-monospace, monospace"

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card2="#fbfafe", band="#f5f2fb",
        row="#faf9fd", row2="#f7f5fc",
        edge="#e4dfef", line="#e9e4f2",
        text="#14151c", sub="#4d5261", faint="#7f8496",
        accent="#4B67B4", accent_soft="#eceaf9", accent_border="#b9c2e8",
        amber="#b45309", amber_soft="#fdf4e6", amber_border="#e5c89f",
        skip="#7d8290", skip_soft="#f1eff6",
        shadow=(43, 32, 74), shadow_alpha=16, glow=40,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1a2130", card2="#1e2636", band="#202839",
        row="#202838", row2="#1d2534",
        edge="#2e374b", line="#2a3346",
        text="#f0f3f9", sub="#a8b1c4", faint="#7b8396",
        accent="#8496f5", accent_soft="#242d42", accent_border="#46527a",
        amber="#d9a441", amber_soft="#2b2316", amber_border="#5a4726",
        skip="#8a92a4", skip_soft="#222a3a",
        shadow=(0, 0, 0), shadow_alpha=105, glow=48,
    ),
}


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(round(size)))


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.5:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size >= minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


# --------------------------------------------------------------------------- #
# Pillow kit
# --------------------------------------------------------------------------- #


def gradient(w: int, h: int, c0: str, c1: str) -> Image.Image:
    a, b = hx(c0), hx(c1)
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)],
               fill=tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return img


def glow(img: Image.Image, cx: int, cy: int, rx: int, ry: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
              fill=hx(color) + (max(0, min(255, alpha)),))
    layer = layer.filter(ImageFilter.GaussianBlur(70))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def add_shadows(img: Image.Image, boxes: list[tuple[tuple[int, int, int, int], int]],
                s: dict) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for box, radius in boxes:
        d.rounded_rectangle(box, radius=radius,
                            fill=s["shadow"] + (s["shadow_alpha"],))
    layer = layer.filter(ImageFilter.GaussianBlur(16))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def dashed_round_rect(d: ImageDraw.ImageDraw, box: tuple[float, float, float, float],
                      color: str, radius: int = 10, width: int = 2,
                      dash: int = 7, gap: int = 5) -> None:
    x0, y0, x1, y1 = box
    xa, xb = x0 + radius, x1 - radius
    for x in range(int(xa), int(xb), dash + gap):
        xe = min(x + dash, xb)
        d.line([(x, y0), (xe, y0)], fill=hx(color), width=width)
        d.line([(x, y1), (xe, y1)], fill=hx(color), width=width)
    ya, yb = y0 + radius, y1 - radius
    for y in range(int(ya), int(yb), dash + gap):
        ye = min(y + dash, yb)
        d.line([(x0, y), (x0, ye)], fill=hx(color), width=width)
        d.line([(x1, y), (x1, ye)], fill=hx(color), width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold", pad: int = 16) -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + pad * 2, y + h], radius=h / 2,
                        fill=hx(bg or s["accent_soft"]))
    d.text((x + pad, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + pad * 2)


# --------------------------------------------------------------------------- #
# hero content
# --------------------------------------------------------------------------- #
# The seven rows are exactly the cases the flow matrix draws: six map to the
# first clause whose literal keyword occurs, row 03 matches nothing, and row 05
# matches 第十二条 but mentions 消防, which article 2 hands to other provisions.

HERO = {
    "zh": dict(
        kicker="DEEPSEEK HARNESS 插件 · 隐患台账 → 条款候选 · 只读",
        value=["逐行对到判定条款", "对不上的行，留在表上"],
        sub=["读一份安全隐患台账，按随包规则包做字面关键词映射；",
             "报出哪一行、差哪一条、为什么——不判合规，结论留给审核人。"],
        meta="hidden_risk_map · HR-001…HR-004 · issues[] + skipped[]",
        foot="Apache-2.0 · 纯本地只读 · 不联网 · 不调用模型 · 只列差异",
        card_head="示例台账 7 行 → 候选条款",
        card_sub="字面关键词 · 命中即止 · 不判合规",
        cols=["行 / 台账描述 / 映射"],
        rows=[
            ("01", "液氨机房未设泄漏报警", "第十二条", "hit", ""),
            ("02", "炼钢连铸未设事故钢水罐", "第四条", "hit", ""),
            ("03", "车间地面油污未清理", "无条款", "gap", "任何关键词都没命中"),
            ("04", "有限空间未执行作业审批", "第十三条", "hit", ""),
            ("05", "液氨罐区消防设施缺失", "第十二条", "regime", "第二条 → 改查相应规定"),
            ("06", "铝镁粉尘除尘未泄爆", "第十一条", "hit", ""),
            ("07", "承包单位未统一协调", "第三条", "hit", ""),
        ],
        foot1="1 行未映射 · issues[] 2 warn · skipped[] 3",
        foot2="只列线索供复核 · 不判定是否构成重大隐患",
    ),
    "en": dict(
        kicker="DEEPSEEK HARNESS PLUGIN · HAZARD LEDGER → CLAUSE CANDIDATES · READ-ONLY",
        value=["Map every ledger row", "and keep the misses visible"],
        sub=["Reads a hazard ledger and applies the packaged literal-keyword map;",
             "reports which row misses which clause — the reviewer decides."],
        meta="hidden_risk_map · HR-001…HR-004 · issues[] + skipped[]",
        foot="Apache-2.0 · local read-only · no network · no model call · differences only",
        card_head="7 sample rows → candidate clauses",
        card_sub="literal keyword · first hit only · no verdict",
        cols=["ROW / LEDGER TEXT / MAPPED TO"],
        rows=[
            ("01", "Ammonia plant: no leak alarm", "Art. 12", "hit", ""),
            ("02", "Steel caster: no emergency ladle", "Art. 4", "hit", ""),
            ("03", "Workshop floor: oil spill", "no clause", "gap", "no keyword matched"),
            ("04", "Confined space: no work permit", "Art. 13", "hit", ""),
            ("05", "Ammonia tank: fire gear missing", "Art. 12", "regime", "Art. 2 → other provisions"),
            ("06", "Al dust: no explosion venting", "Art. 11", "hit", ""),
            ("07", "Contractor: no coordination", "Art. 3", "hit", ""),
        ],
        foot1="1 row unmapped · issues[] 2 warn · skipped[] 3",
        foot2="Leads for review only · never a verdict",
    ),
}

HERO_W, HERO_H = 1440, 576
LEFT_X, LEFT_W = 56, 860
CARD = (944, 48, 1384, 528)
CARD_IN_L = 968
CARD_IN_R = 1360
ROW_TOP, ROW_H, ROW_GAP = 142, 42, 4


def hero(lang: str, skin: str) -> Image.Image:
    s = SKIN[skin]
    h = HERO[lang]
    img = gradient(HERO_W, HERO_H, s["bg_from"], s["bg_to"])
    img = glow(img, 1190, 230, 330, 270, s["accent"], s["glow"])
    img = glow(img, 190, 570, 300, 160, s["accent"], max(8, s["glow"] // 3))
    img = add_shadows(img, [(CARD, 22)], s)
    d = ImageDraw.Draw(img)

    # ---- left column -------------------------------------------------------
    right = pill(img, (LEFT_X, 42), h["kicker"], s, size=16)
    if right > LEFT_X + LEFT_W:
        raise SystemExit(f"FATAL: hero kicker overflows ({right - LEFT_X}px)")
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", LEFT_W, 80, 78)
    require_w(NAME, title_size, "mono_bold", LEFT_W, "hero title")
    d.text((LEFT_X, 186), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]), anchor="ls")

    value_size = fit_lines(h["value"], "cjk_bold", LEFT_W, 42, 40)
    for i, line in enumerate(h["value"]):
        require_w(line, value_size, "cjk_bold", LEFT_W, "hero value line")
        d.text((LEFT_X, 252 + i * 50), line,
               font=font(value_size, "cjk_bold"), fill=hx(s["text"]),
               anchor="ls")

    sub_size = fit_lines(h["sub"], "cjk", LEFT_W, 26, 25)
    for i, line in enumerate(h["sub"]):
        require_w(line, sub_size, "cjk", LEFT_W, "hero subtitle")
        d.text((LEFT_X, 356 + i * 33), line, font=font(sub_size, "cjk"),
               fill=hx(s["sub"]), anchor="ls")

    require_w(h["meta"], 20, "mono", LEFT_W, "hero meta")
    d.text((LEFT_X, 444), h["meta"], font=font(20, "mono"),
           fill=hx(s["faint"]), anchor="ls")

    d.line([LEFT_X, 470, LEFT_X + LEFT_W - 22, 470], fill=hx(s["line"]),
           width=2)
    require_w(h["foot"], 17, "cjk", LEFT_W, "hero footer")
    d.text((LEFT_X, 500), h["foot"], font=font(17, "cjk"), fill=hx(s["faint"]),
           anchor="ls")

    # ---- right: the ledger-to-clause card ---------------------------------
    x0, y0, x1, y1 = CARD
    d.rounded_rectangle(CARD, radius=22, fill=hx(s["card"]),
                        outline=hx(s["edge"]), width=2)

    head_size = 16
    require_w(h["card_head"], head_size, "cjk_bold",
              CARD_IN_R - CARD_IN_L, "hero card head")
    d.text((CARD_IN_L, 84), h["card_head"],
           font=font(head_size, "cjk_bold"), fill=hx(s["text"]), anchor="ls")
    d.text((CARD_IN_L, 104), h["card_sub"], font=font(11, "cjk"),
           fill=hx(s["faint"]), anchor="ls")
    d.text((CARD_IN_L, 126), h["cols"][0],
           font=font(11, "cjk" if lang == "zh" else "mono"),
           fill=hx(s["faint"]), anchor="ls")
    d.line([CARD_IN_L, 134, CARD_IN_R, 134], fill=hx(s["line"]), width=1)

    for i, (num, text, tag, style, sub) in enumerate(h["rows"]):
        top = ROW_TOP + i * (ROW_H + ROW_GAP)
        box = (CARD_IN_L, top, CARD_IN_R, top + ROW_H)
        if style == "gap":
            d.rounded_rectangle(box, radius=11, fill=hx(s["amber_soft"]))
            dashed_round_rect(d, box, s["amber_border"], radius=11, width=2,
                              dash=7, gap=5)
            d.rounded_rectangle([CARD_IN_L, top + 7, CARD_IN_L + 3,
                                 top + ROW_H - 7], radius=2,
                                fill=hx(s["amber"]))
        elif style == "regime":
            d.rounded_rectangle(box, radius=11, fill=hx(s["card2"]),
                                outline=hx(s["amber_border"]), width=1)
            d.rounded_rectangle([CARD_IN_L, top + 7, CARD_IN_L + 3,
                                 top + ROW_H - 7], radius=2,
                                fill=hx(s["amber"]))
        else:
            d.rounded_rectangle(box, radius=11,
                                fill=hx(s["row"] if i % 2 == 0 else s["row2"]))

        d.text((CARD_IN_L + 14, top + 25), num, font=font(11, "mono"),
               fill=hx(s["faint"]), anchor="ls")
        desc_kind = "cjk"
        desc_size = 14.5
        tag_size = 11
        tag_width = measure(tag, tag_size, "cjk_bold" if lang == "zh" else "mono_bold")
        tag_x1 = CARD_IN_R - 10
        tag_x0 = tag_x1 - tag_width - 18
        max_desc = tag_x0 - 12 - (CARD_IN_L + 42)
        require_w(text, desc_size, desc_kind, max_desc, "hero card row")
        d.text((CARD_IN_L + 42, top + 24), text,
               font=font(desc_size, desc_kind), fill=hx(s["text"]),
               anchor="ls")
        if sub != "":
            require_w(sub, 10, "cjk", CARD_IN_R - 12 - (CARD_IN_L + 42),
                      "hero card row note")
            note_fill = s["amber"] if style in ("gap", "regime") else s["faint"]
            d.text((CARD_IN_L + 42, top + 37), sub, font=font(10, "cjk"),
                   fill=hx(note_fill), anchor="ls")

        tag_fg = s["amber"] if style in ("gap", "regime") else s["accent"]
        tag_bg = s["amber_soft"] if style in ("gap", "regime") else s["accent_soft"]
        tag_y = top + 21
        if sub != "":
            tag_y = top + 18
        d.rounded_rectangle([tag_x0, tag_y - 14, tag_x1, tag_y + 7],
                            radius=10, fill=hx(tag_bg))
        d.text((tag_x0 + 9, tag_y - 3), tag,
               font=font(tag_size, "cjk_bold" if lang == "zh" else "mono_bold"),
               fill=hx(tag_fg), anchor="ls")

    d.line([CARD_IN_L, 474, CARD_IN_R, 474], fill=hx(s["line"]), width=1)
    require_w(h["foot1"], 11.5, "cjk", CARD_IN_R - CARD_IN_L,
              "hero card footer")
    d.text((CARD_IN_L, 494), h["foot1"], font=font(11.5, "cjk"),
           fill=hx(s["sub"]), anchor="ls")
    d.text((CARD_IN_L, 510), h["foot2"], font=font(10.5, "cjk"),
           fill=hx(s["faint"]), anchor="ls")

    return img


# --------------------------------------------------------------------------- #
# SVG kit
# --------------------------------------------------------------------------- #


def tw(text: str, size: float, kind: str = "cjk") -> float:
    return measure(text, size, kind)


def check(text: str, size: float, kind: str, max_w: float, what: str) -> None:
    got = tw(text, size, kind)
    if got > max_w + 0.5:
        raise SystemExit(f"FATAL: SVG {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def text_el(x: float, y: float, text: str, size: float, fill: str, *,
            weight: int = 400, anchor: str = "start", mono: bool = False,
            opacity: float = 1.0, spacing: float | None = None,
            extra: str = "") -> str:
    attrs = [
        f'x="{x:g}"', f'y="{y:g}"', f'font-family="{MONO if mono else SANS}"',
        f'font-size="{size:g}"', f'fill="{fill}"', f'font-weight="{weight}"',
        f'text-anchor="{anchor}"',
    ]
    if opacity != 1.0:
        attrs.append(f'opacity="{opacity:g}"')
    if spacing is not None:
        attrs.append(f'letter-spacing="{spacing:g}"')
    if extra:
        attrs.append(extra)
    return f'<text {" ".join(attrs)}>{escape(text)}</text>'


def rect_el(x: float, y: float, w: float, h: float, fill: str, *,
            rx: float = 0, stroke: str | None = None, sw: float = 1,
            dash: str | None = None, opacity: float | None = None,
            extra: str = "") -> str:
    attrs = [f'x="{x:g}"', f'y="{y:g}"', f'width="{w:g}"', f'height="{h:g}"',
             f'fill="{fill}"']
    if rx:
        attrs.append(f'rx="{rx:g}"')
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw:g}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity:g}"')
    if extra:
        attrs.append(extra)
    return f'<rect {" ".join(attrs)}/>'


def circle_el(cx: float, cy: float, r: float, fill: str, *,
              stroke: str | None = None, sw: float = 1,
              dash: str | None = None) -> str:
    attrs = [f'cx="{cx:g}"', f'cy="{cy:g}"', f'r="{r:g}"', f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw:g}"')
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f'<circle {" ".join(attrs)}/>'


# --------------------------------------------------------------------------- #
# flow-v5: a row-to-clause matrix with two boundary exits
# --------------------------------------------------------------------------- #

FLOW_ROWS = [
    ("01", "液氨机房未设泄漏报警", 3),
    ("02", "炼钢连铸未设事故钢水罐", 1),
    ("03", "车间地面油污未清理", 6),
    ("04", "有限空间未执行作业审批", 4),
    ("05", "液氨罐区消防设施缺失", 3),
    ("06", "铝镁粉尘除尘未泄爆", 2),
    ("07", "承包单位未统一协调", 0),
]

FLOW_COLS = [
    ("第三条", "通用"),
    ("第四条", "冶金"),
    ("第十一条", "粉尘涉爆"),
    ("第十二条", "液氨制冷"),
    ("第十三条", "有限空间"),
    ("第二条", "其他规定"),
    ("无条款", "GAP · HR-001"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    W, H = 1100, 660
    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-labelledby="title desc">',
        f'<title id="title">{NAME} — ledger rows to candidate clauses</title>',
        f'<desc id="desc">Seven ledger rows against seven outcomes. Rows map '
        f'through literal keywords to industry clauses; article 2 reroutes '
        f'regime rows; unmatched rows stay in the gap column as HR-001 '
        f'findings. The rule-state rail and the two report exits follow.</desc>',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>',
        f'<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{s["accent"]}" stop-opacity="0.20"/>'
        f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/>'
        f'</radialGradient>',
        f'<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="7" stdDeviation="11" '
        f'flood-color="{s["shadow"]}" flood-opacity="0.16"/></filter>',
        f'<pattern id="dots" width="26" height="26" '
        f'patternUnits="userSpaceOnUse">'
        f'<circle cx="1.4" cy="1.4" r="1.1" fill="{s["accent"]}" '
        f'opacity="0.13"/></pattern>',
        "</defs>",
        rect_el(0, 0, W, H, "url(#bg)", rx=22),
        rect_el(0, 0, W, 430, "url(#halo)", opacity=0.75),
        rect_el(0, 0, W, H, "url(#dots)", rx=22, opacity=0.55),
    ]

    # ---- header ------------------------------------------------------------
    kicker = "STRUCTURE · LEDGER-TO-CLAUSE MATRIX"
    title = "Rows map to clauses; the unmapped stay visible"
    sub = ("dsh-hidden-risk-map · entries[] · literal keyword gate · "
           "article-2 boundary · issues[] / skipped[] · human review")
    check(kicker, 11, "cjk_bold", 800, "kicker")
    check(title, 25, "cjk_bold", 810, "title")
    check(sub, 11.5, "cjk", 820, "subtitle")
    out.append(text_el(40, 40, kicker, 11, s["accent"], weight=700,
                       spacing=1.5))
    out.append(text_el(40, 76, title, 25, s["text"], weight=700))
    out.append(text_el(40, 99, sub, 11.5, s["sub"]))
    out.append(rect_el(882, 34, 176, 30, s["accent_soft"], rx=15,
                       stroke=s["accent_border"], sw=1))
    out.append(text_el(970, 53, "ruleset 2026.1 · 4 rules", 11, s["accent"],
                       mono=True, anchor="middle"))
    out.append(f'<line x1="40" y1="112" x2="1060" y2="112" '
               f'stroke="{s["line"]}" stroke-width="1"/>')

    # ---- matrix card -------------------------------------------------------
    out.append(rect_el(40, 118, 1020, 328, s["card"], rx=20,
                       stroke=s["edge"], sw=1.5,
                       extra='filter="url(#shadow)"'))
    out.append(text_el(62, 146, "MAPPING MATRIX", 13, s["text"], weight=700,
                       spacing=0.8))
    out.append(text_el(190, 146,
                       "7 ledger rows × 7 outcomes · first keyword hit wins",
                       11, s["faint"]))
    out.append(text_el(1038, 146, "read-only · no verdict", 11, s["faint"],
                       anchor="end"))
    out.append(rect_el(52, 156, 996, 42, s["band"], rx=9))
    out.append(text_el(62, 182, "ROW · 台账条目", 11, s["sub"], weight=700,
                       mono=False))
    out.append(f'<line x1="302" y1="156" x2="302" y2="426" '
               f'stroke="{s["line"]}" stroke-width="1"/>')

    for i in range(1, 7):
        x = 310 + i * 100
        out.append(f'<line x1="{x}" y1="198" x2="{x}" y2="426" '
                   f'stroke="{s["line"]}" stroke-width="1"/>')
    # article-2 boundary and the HR-001 gap boundary
    for x, color in ((810, s["amber_border"]), (910, s["amber_border"])):
        out.append(f'<line x1="{x}" y1="158" x2="{x}" y2="428" '
                   f'stroke="{color}" stroke-width="1.5" '
                   f'stroke-dasharray="5 5" opacity="0.9"/>')
    out.append(rect_el(812, 160, 96, 34, s["amber_soft"], rx=7))
    out.append(rect_el(912, 160, 96, 34, s["amber_soft"], rx=7))

    for ci, (main, small) in enumerate(FLOW_COLS):
        cx = 310 + ci * 100 + 50
        color = s["amber"] if ci >= 5 else s["text"]
        check(main, 13, "cjk_bold", 92, f"column {ci} label")
        check(small, 11, "cjk", 92, f"column {ci} sub")
        out.append(text_el(cx, 175, main, 13, color, weight=700,
                           anchor="middle"))
        out.append(text_el(cx, 192, small, 11,
                           s["amber"] if ci >= 5 else s["faint"],
                           anchor="middle"))

    # rows
    for i, (num, label, col) in enumerate(FLOW_ROWS):
        y = 202 + i * 32
        cy = y + 16
        if i == 2:
            out.append(rect_el(52, y + 1, 996, 30, s["amber_soft"], rx=7,
                               opacity=0.55))
        elif i % 2 == 1:
            out.append(rect_el(52, y + 1, 996, 30, s["row2"], rx=7,
                               opacity=0.65))
        check(label, 13, "cjk", 208, f"row {num} label")
        out.append(text_el(62, y + 21, num, 11, s["faint"], mono=True))
        out.append(text_el(86, y + 21, label, 13, s["text"]))
        cx = 310 + col * 100 + 50
        if col == 6:
            out.append(circle_el(cx, cy, 6, "none", stroke=s["amber"], sw=2,
                                 dash="3 2"))
        elif i == 4 and col == 3:
            # matched to 第十二条, then handed off by article 2
            out.append(circle_el(cx, cy, 5, s["card"], stroke=s["accent"],
                                 sw=2))
            out.append(f'<path d="M{cx + 7} {cy} C {cx + 55} {cy - 12}, '
                       f'{810 - 50} {cy - 12}, {858} {cy - 2}" fill="none" '
                       f'stroke="{s["amber"]}" stroke-width="1.6" '
                       f'stroke-dasharray="4 3"/>')
            out.append(f'<path d="M{858} {cy - 2} l-7 -4 l1 8 z" '
                       f'fill="{s["amber"]}"/>')
            out.append(circle_el(860, cy, 5, s["amber"]))
            out.append(text_el(760, cy + 14, "HR-002", 11, s["amber"],
                               weight=700, anchor="middle"))
        else:
            out.append(circle_el(cx, cy, 5, s["accent"]))

    legend = ("● clause hit    ○ art. 2 source → amber exit    "
              "◌ no keyword hit → GAP (HR-001)    "
              "keyword table is an editorial aid, not standard text")
    check(legend, 11, "cjk", 970, "legend")
    out.append(text_el(62, 440, legend, 11, s["faint"]))

    # ---- rule-state rail ---------------------------------------------------
    out.append(text_el(40, 477, "RULE STATES", 10.5, s["faint"], weight=700,
                       spacing=0.8))
    states = [
        ("HR-001 · warn · 1 gap", True),
        ("HR-002 · warn · 1 reroute", True),
        ("HR-003 · skipped · unset", False),
        ("HR-004 · skipped · 0", False),
    ]
    for i, (label, fired) in enumerate(states):
        x = 124 + i * 228
        check(label, 11, "cjk", 200, f"rule state {i}")
        if fired:
            out.append(rect_el(x, 459, 220, 30, s["accent_soft"], rx=9,
                               stroke=s["accent_border"], sw=1))
            fg = s["accent"]
        else:
            out.append(rect_el(x, 459, 220, 30, s["card2"], rx=9,
                               stroke=s["line"], sw=1, dash="4 3"))
            fg = s["skip"]
        out.append(circle_el(x + 15, 474, 3, fg))
        out.append(text_el(x + 26, 478, label, 11, fg, mono=True))

    # ---- report: two exits, one reviewer -----------------------------------
    out.append(rect_el(40, 502, 1020, 128, s["card"], rx=18,
                       stroke=s["edge"], sw=1.5,
                       extra='filter="url(#shadow)"'))
    out.append(text_el(62, 526, "REPORT · two exits, one reviewer", 13,
                       s["text"], weight=700))
    out.append(text_el(1038, 526, "mapping ≠ verdict", 11, s["amber"],
                       weight=700, anchor="end"))
    out.append(rect_el(62, 540, 3, 80, s["accent"], rx=1.5))
    out.append(text_el(76, 558, "issues[] · 2 warn", 13, s["accent"],
                       weight=700))
    out.append(text_el(76, 577,
                       "HR-001  row 03  no keyword hit — unmapped row", 11,
                       s["sub"], mono=False))
    out.append(text_el(76, 594,
                       "HR-002  row 05  article 2 — other provisions", 11,
                       s["sub"]))
    out.append(text_el(76, 611,
                       "every issue: found · expected · fix · basis", 11,
                       s["faint"]))
    out.append(f'<line x1="554" y1="540" x2="554" y2="620" '
               f'stroke="{s["line"]}" stroke-width="1"/>')
    out.append(text_el(572, 558, "skipped[] · 3", 13, s["text"], weight=700))
    out.append(text_el(572, 577,
                       "HR-002  industry unset — industry check not run", 11,
                       s["sub"]))
    out.append(text_el(572, 594,
                       "HR-003  requiredFields empty — rule off", 11,
                       s["sub"]))
    out.append(text_el(572, 611,
                       "HR-004  maxHitsPerClause 0 — rule off", 11,
                       s["sub"]))

    flow_foot = ("literal keywords are an editorial aid, not standard text · "
                 "excerpts must be verbatim · the verdict stays with the reviewer")
    check(flow_foot, 11, "cjk", 1020, "flow footer")
    out.append(text_el(40, 648, flow_foot, 11, s["faint"]))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main() -> None:
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            img = hero(lang, skin)
            path = os.path.join(
                OUT, f"{NAME}-hero-{lang}-{skin}.webp")
            img.save(path, "WEBP", quality=92, method=6)
            print("wrote", os.path.relpath(path, ROOT))
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
