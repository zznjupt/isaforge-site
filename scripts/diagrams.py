#!/usr/bin/env python3
"""The tutorial's diagrams for the site, in both languages and both themes.

    python3 scripts/diagrams.py

Writes docs/public/tutorial/<name>-<zh|en>[-dark].svg. Colours by role:
blue is what you write, violet the tools, green what is generated, orange
verification, rose external references, teal running and testing, gray build
copies and intermediate files. The light and dark palettes follow the site's
(brand blue, orange and teal); every label is given in Chinese and English.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "public" / "tutorial"
FONTS = {
    "zh": "'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Noto Sans CJK SC',sans-serif",
    "en": "Inter,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',sans-serif",
}
MONO = "'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": dict(
        C={
            "blue":   dict(fill="#E8EEFA", stroke="#2F56A6", text="#1F3F80"),
            "violet": dict(fill="#F1ECFE", stroke="#7C5AD9", text="#4F2FA6"),
            "green":  dict(fill="#E7F8EF", stroke="#2BA160", text="#176B3C"),
            "orange": dict(fill="#FEF1E3", stroke="#F28C28", text="#9A5000"),
            "rose":   dict(fill="#FDECEE", stroke="#DB4B5A", text="#A3283A"),
            "teal":   dict(fill="#E1F6F3", stroke="#17B3A3", text="#0B6E64"),
            "gray":   dict(fill="#F3F4F6", stroke="#9CA3AF", text="#4B5563"),
        },
        INK="#1F2937", MUTED="#6B7280", CARD="#FFFFFF", BG="#FFFFFF", BORDER="#E5E7EB",
        ONSOLID="#FFFFFF", LANE="#FAFAFB", LANE_STROKE="#E5E7EB", SHADOW=("#1F2937", 0.10),
    ),
    "dark": dict(
        C={
            "blue":   dict(fill="#1C2740", stroke="#8FB0FF", text="#C2D3FF"),
            "violet": dict(fill="#251F3B", stroke="#A78BFA", text="#D2C3FF"),
            "green":  dict(fill="#16301F", stroke="#4CC27E", text="#A6E8C0"),
            "orange": dict(fill="#3A2716", stroke="#F28C28", text="#FFC78F"),
            "rose":   dict(fill="#3A1B21", stroke="#F07380", text="#FFB9C1"),
            "teal":   dict(fill="#10302C", stroke="#2CC7B6", text="#93E8DD"),
            "gray":   dict(fill="#26262B", stroke="#6B6B73", text="#C4C4CC"),
        },
        INK="#E6E6E1", MUTED="#A0A0A8", CARD="#1B1B1F", BG="#202127", BORDER="#2E2E32",
        ONSOLID="#14161C", LANE="#26262C", LANE_STROKE="#34343B", SHADOW=("#000000", 0.40),
    ),
}

LANG = "zh"
T = THEMES["light"]
C = T["C"]
INK = MUTED = None


def use(lang, theme):
    global LANG, T, C, INK, MUTED
    LANG, T = lang, THEMES[theme]
    C, INK, MUTED = T["C"], T["INK"], T["MUTED"]


def L(zh, en):
    """The label in the current language."""
    return zh if LANG == "zh" else en


def width(s, size, mono=False):
    """An estimate of a text's width: a CJK character is one font size wide,
    others about 0.58 of it (0.62 in monospace)."""
    return sum(size if ord(ch) > 0x2E7F else size * (0.62 if mono else 0.58) for ch in s)


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.items = w, h, title, []
        self.markers = set()

    def add(self, s):
        self.items.append(s)

    def rect(self, x, y, w, h, color="gray", rx=10, fill=None, stroke=None, sw=1.6, dash=None, shadow=False):
        c = C[color]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        f = ' filter="url(#shadow)"' if shadow else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill or c["fill"]}" stroke="{stroke or c["stroke"]}" stroke-width="{sw}"{d}{f}/>')

    def text(self, x, y, s, size=14, color=None, weight=400, anchor="start", mono=False, italic=False):
        fam = MONO if mono else FONTS[LANG]
        st = ' font-style="italic"' if italic else ""
        if mono:
            s = s.replace(" ", "\u00a0")    # keeps the indentation and alignment of code
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{color or INK}" '
                 f'font-weight="{weight}" text-anchor="{anchor}"{st}>{escape(s)}</text>')

    def arrow(self, pts, color=None, sw=2, dash=None, head=True):
        color = color or MUTED
        d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#ah-{color[1:]})"' if head else ""
        self.markers.add(color)
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" '
                 f'stroke-linejoin="round"{da}{mk}/>')

    def pill(self, x, y, s, color, size=13, pad=10, h=26, mono=False, solid=False):
        """A rounded label; returns its width."""
        c = C[color]
        w = width(s, size, mono) + 2 * pad
        self.rect(x, y, w, h, color, rx=h / 2, fill=c["stroke"] if solid else T["CARD"], sw=1.4)
        self.text(x + w / 2, y + h / 2 + size * 0.36, s, size, T["ONSOLID"] if solid else c["text"],
                  600, "middle", mono)
        return w

    def panel(self, x, y, w, h, color, head, sub=None):
        """A panel with a coloured title bar."""
        c = C[color]
        self.rect(x, y, w, h, color, rx=14, shadow=True)
        self.add(f'<path d="M{x},{y + 14} a14,14 0 0 1 14,-14 h{w - 28} a14,14 0 0 1 14,14 v28 h-{w} z" '
                 f'fill="{c["stroke"]}"/>')
        self.text(x + 16, y + 28, head, 16, T["ONSOLID"], 700)
        if sub:
            self.text(x + w - 14, y + 28, sub, 13, T["ONSOLID"], 500, "end", mono=True)

    def card(self, x, y, w, h, color, title, body=None, mono_title=True, size=14):
        c = C[color]
        self.rect(x, y, w, h, color, rx=9, fill=T["CARD"], sw=1.4)
        self.add(f'<rect x="{x}" y="{y + 8}" width="4" height="{h - 16}" rx="2" fill="{c["stroke"]}"/>')
        if body:
            self.text(x + 16, y + h / 2 - 3, title, size, c["text"], 700, mono=mono_title)
            self.text(x + 16, y + h / 2 + 16, body, 12.5, MUTED)
        else:
            self.text(x + 16, y + h / 2 + 5, title, size, c["text"], 700, mono=mono_title)

    def save(self, name, theme):
        sc, so = T["SHADOW"]
        defs = ['<filter id="shadow" x="-5%" y="-5%" width="110%" height="120%">'
                f'<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="{sc}" flood-opacity="{so}"/>'
                '</filter>']
        for col in sorted(self.markers):
            defs.append(f'<marker id="ah-{col[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" '
                        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                        f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
        body = "\n  ".join(self.items)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}">\n'
               f'  <title>{escape(self.title)}</title>\n'
               f'  <defs>{"".join(defs)}</defs>\n'
               f'  <rect width="{self.w}" height="{self.h}" rx="16" fill="{T["BG"]}" stroke="{T["BORDER"]}"/>\n'
               f'  {body}\n</svg>\n')
        file = f"{name}-{LANG}{'-dark' if theme == 'dark' else ''}.svg"
        (OUT / file).write_text(svg)
        return file


def heading(s, title, sub=None):
    s.text(30, 40, title, 20, INK, 700)
    if sub:
        s.text(30 + width(title, 20) + 14, 40, sub, 14, MUTED)


# ---------------------------------------------------------------- 1. overview
def overview():
    s = Svg(1040, 560, L("你写什么，ISAForge 生成什么，怎样验证", "What you write, what ISAForge generates, how it is checked"))
    heading(s, L("你写什么，得到什么", "What you write, what you get"),
            L("一份描述，生成全部工具", "one description, every tool"))
    cols = [
        (30, "blue", L("① 你写：ISA 包", "① You write: an ISA package"), "isa/myrv/", [
            ("arch.xml", L("字长 · 执行模型 · 扩展", "length · execution model · extensions")),
            ("registers.xml", L("寄存器堆 · 内存", "register files · memory")),
            ("layouts.xml", L("共用的编码布局", "shared encoding layouts")),
            ("instructions/*.xml", L("编码 · 汇编语法 · Sail 语义", "encodings · syntax · Sail semantics")),
        ]),
        (375, "violet", L("② ISAForge：读取并生成", "② ISAForge generates"), "tools/", [
            ("check.py", L("静态检查", "static check")),
            ("gen_sail.py", L("生成 Sail 模型", "generates the Sail model")),
            ("gen_rust.py", L("生成 Rust 模型", "generates the Rust model")),
            ("asm.py · gen_docs.py", L("汇编器 · 指令手册", "assembler · manual")),
        ]),
        (720, "green", L("③ 得到：工具", "③ You get: the tools"), "build/", [
            (L("汇编器 · 反汇编器", "Assembler · disassembler"), L("汇编文本 ⇄ 指令字", "assembly text ⇄ words")),
            ("xinyu-sim", L("Sail 参考模拟器：准确", "Sail reference simulator: exact")),
            ("rsim", L("Rust 模拟器：快", "Rust simulator: fast")),
            ("docs/index.html", L("指令手册", "instruction manual")),
        ]),
    ]
    for x, color, head, sub, items in cols:
        s.panel(x, 64, 290, 318, color, head, sub if LANG == "zh" else None)
        for i, (t, b) in enumerate(items):
            mono = any(ch in t for ch in "./*") or t in ("xinyu-sim", "rsim")    # file and program names
            s.card(x + 16, 120 + i * 63, 258, 52, color, t, b, mono_title=mono)
    s.arrow([(322, 223), (371, 223)], C["violet"]["stroke"], 3)
    s.arrow([(667, 223), (716, 223)], C["green"]["stroke"], 3)
    s.panel(30, 414, 980, 118, "orange", L("④ 验证：一层层确认它是对的", "④ Verify: confirm it is right, layer by layer"),
            "make ARCH=myrv …")
    chips = [(L("静态检查", "Static check"), "check"), (L("定向测试", "Directed tests"), "sim-test"),
             (L("随机差分", "Differential"), "fuzz"), (L("等价性证明", "Equivalence"), "equiv-prove"),
             (L("外部参考", "References"), "corpus · spike"), (L("覆盖率", "Coverage"), "coverage")]
    ws = [max(width(n, 15), width(c, 12, True)) + 40 for n, c in chips]
    gap = (980 - 36 - sum(ws)) / (len(chips) - 1)
    x = 48
    for (name, cmd), w in zip(chips, ws):
        s.rect(x, 466, w, 50, "orange", rx=10, fill=T["CARD"], sw=1.4)
        s.text(x + w / 2, 487, name, 15, C["orange"]["text"], 700, "middle")
        s.text(x + w / 2, 506, cmd, 12, MUTED, 400, "middle", mono=True)
        x += w + gap
    s.arrow([(865, 414), (865, 386)], C["orange"]["stroke"], 2, dash="5 4")
    s.arrow([(520, 414), (520, 386)], C["orange"]["stroke"], 2, dash="5 4")
    return s, "overview"


# ---------------------------------------------------------------- 2. roadmap
def roadmap():
    s = Svg(1040, 250, L("教程的十个步骤，分四个阶段", "The tutorial's ten steps, in four stages"))
    heading(s, L("学习路线", "The route"), L("十步，分四个阶段", "ten steps in four stages"))
    phases = [
        ("blue", L("描述 ISA", "Describe the ISA"), [("1", L("骨架和第一条指令", "Skeleton, first instruction")),
                                                   ("2", L("让程序跑起来", "Run a program")),
                                                   ("3", L("补齐常用指令", "Common instructions"))]),
        ("teal", L("测试", "Test"), [("4", L("定向测试", "Directed tests")), ("5", L("随机差分", "Differential testing"))]),
        ("violet", L("扩展 ISA", "Extend the ISA"), [("6", L("特性开关", "Feature switches")), ("7", L("别名", "Aliases")),
                                                    ("8", L("自定义指令与等价性", "Custom instruction"))]),
        ("orange", L("验证与交付", "Verify and deliver"), [("9", L("外部参考", "External references")),
                                                         ("10", L("覆盖率与手册", "Coverage and manual"))]),
    ]
    x, w, gap = 30, 226, 25.3
    for i, (color, name, steps) in enumerate(phases):
        s.panel(x, 62, w, 166, color, name)
        for j, (n, label) in enumerate(steps):
            y = 114 + j * 36
            c = C[color]
            s.rect(x + 14, y, w - 28, 28, color, rx=14, fill=T["CARD"], sw=1.3)
            s.add(f'<circle cx="{x + 28}" cy="{y + 14}" r="11" fill="{c["stroke"]}"/>')
            s.text(x + 28, y + 18.5, n, 12, T["ONSOLID"], 700, "middle")
            s.text(x + 46, y + 19, label, 13.5, c["text"], 600)
        if i < len(phases) - 1:
            s.arrow([(x + w + 3, 145), (x + w + gap - 3, 145)], MUTED, 2.5)
        x += w + gap
    return s, "roadmap"


# ---------------------------------------------------------------- 3. anatomy
def anatomy():
    s = Svg(1040, 560, L("ADDI 的编码、语法和语义", "ADDI's encoding, syntax and semantics"))
    heading(s, L("一条指令的组成：以 ADDI 为例", "What an instruction is made of: ADDI"),
            L("addi x1, x0, 5  →  指令字 0x00500093", "addi x1, x0, 5  →  word 0x00500093"))
    x0, bw, y0 = 60, 920 / 32, 96
    fields = [  # name, high bit, low bit, colour, the example's bits, note, operand?
        ("imm", 31, 20, "blue", "000000000101", L("操作数 imm = 5", "operand imm = 5"), True),
        ("rs1", 19, 15, "teal", "00000", L("操作数 rs1 = x0", "rs1 = x0"), True),
        ("funct3", 14, 12, "gray", "000", L("常量 0b000", "0b000"), False),
        ("rd", 11, 7, "green", "00001", L("操作数 rd = x1", "rd = x1"), True),
        ("opcode", 6, 0, "gray", "0010011", L("常量 0b0010011", "constant 0b0010011"), False),
    ]
    for name, hi, lo, color, bits, note, operand in fields:
        x = x0 + (31 - hi) * bw
        w = (hi - lo + 1) * bw
        c = C[color]
        s.rect(x, y0, w, 64, color, rx=0, fill=c["fill"], stroke=c["stroke"], sw=1.6)
        s.text(x + w / 2, y0 + 26, name, 15, c["text"], 700, "middle", mono=True)
        s.text(x + w / 2, y0 + 49, bits, 14, INK, 500, "middle", mono=True)
        s.text(x + 4, y0 - 8, str(hi), 12, MUTED, 400, "start", mono=True)
        s.text(x + w - 4, y0 - 8, str(lo), 12, MUTED, 400, "end", mono=True)
        size = 12.5 if LANG == "zh" else 11.5
        pw = width(note, size) + 20
        s.rect(x + w / 2 - pw / 2, y0 + 76, pw, 24, color, rx=12,
               fill=c["stroke"] if operand else T["CARD"], sw=1.2, dash=None if operand else "4 3")
        s.text(x + w / 2, y0 + 92.5, note, size, T["ONSOLID"] if operand else c["text"], 600, "middle")
    s.add(f'<rect x="{x0}" y="{y0}" width="920" height="64" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.text(x0, y0 + 128, L("layout=\"I\" 决定位段怎么分；<encoding> 填常量；与字段同名的 <operands> 自动对应到字段。",
                           "layout=\"I\" says how the bits split; <encoding> fills the constants; operands named like a field take that field."),
           13, MUTED)
    y1 = 268
    boxes = [
        (30, "blue", L("<operands>  操作数", "<operands>  operands"),
         [("rd", L("X  寄存器编号", "X  register number")), ("rs1", L("X  寄存器编号", "X  register number")),
          ("imm", L("simm, width=12  有符号", "simm, width=12  signed"))]),
        (370, "violet", L("<syntax>  汇编语法", "<syntax>  assembly syntax"), None),
        (710, "green", L("<execute>  语义（Sail）", "<execute>  semantics (Sail)"), None),
    ]
    for x, color, head, rows in boxes:
        s.panel(x, y1, 300, 236, color, head)
    for i, (n, ty) in enumerate(boxes[0][3]):
        y = y1 + 62 + i * 52
        s.rect(46, y, 268, 40, "blue", rx=8, fill=T["CARD"], sw=1.3)
        s.text(60, y + 25, n, 15, C["blue"]["text"], 700, mono=True)
        s.text(106, y + 25, ty, 13, MUTED)
    s.text(386, y1 + 74, L("模板", "template"), 12.5, MUTED)
    s.rect(386, y1 + 82, 268, 36, "violet", rx=8, fill=T["CARD"], sw=1.3)
    s.text(400, y1 + 105, "addi {rd}, {rs1}, {imm}", 14, C["violet"]["text"], 600, mono=True)
    s.arrow([(520, y1 + 122), (520, y1 + 146)], C["violet"]["stroke"], 2)
    s.text(386, y1 + 164, L("填入操作数", "operands filled in"), 12.5, MUTED)
    s.rect(386, y1 + 172, 268, 36, "violet", rx=8, fill=T["CARD"], sw=1.3)
    s.text(400, y1 + 195, "addi x1, x0, 5", 14, INK, 600, mono=True)
    s.text(386, y1 + 226, L("汇编器和反汇编器都由它生成", "assembler and disassembler both use it"),
           12.5, C["violet"]["text"], 600)
    code = ["write_X(d.rd,", "  read_X(d.rs1) +", "  sail_sign_extend(d.imm, 64));", "RETIRE_OK"]
    s.rect(726, y1 + 58, 268, 104, "green", rx=8, fill=T["CARD"], sw=1.3)
    for i, line in enumerate(code):
        s.text(740, y1 + 82 + i * 22, line, 13, INK, 500, mono=True)
    s.text(726, y1 + 184, L("d.rd = 1，d.rs1 = 0，d.imm = 5", "d.rd = 1, d.rs1 = 0, d.imm = 5"), 13, C["green"]["text"], 600)
    s.text(726, y1 + 208, L("→ x1 = x0 + 5 = 5；RETIRE_OK：PC 前进", "→ x1 = x0 + 5 = 5; RETIRE_OK: PC moves on"), 13, MUTED)
    s.arrow([(331, y1 + 120), (366, y1 + 120)], C["violet"]["stroke"], 2.5)
    s.arrow([(331, y1 + 150), (348, y1 + 150), (348, y1 + 252), (860, y1 + 252), (860, y1 + 240)],
            C["green"]["stroke"], 2, dash="6 4")
    s.text(560, y1 + 270, L("同一组操作数，在语义里写作 d.rd、d.rs1、d.imm", "the same operands, written d.rd, d.rs1, d.imm in the semantics"),
           12.5, C["green"]["text"], 600, "middle")
    return s, "anatomy"


# ---------------------------------------------------------------- 4. files and commands
def build_flow():
    s = Svg(1040, 616, L("文件和命令怎么串起来", "How the files and commands connect"))
    heading(s, L("文件和命令怎么串起来", "How the files and commands connect"),
            L("蓝色是你写的文件，绿色是生成的模拟器", "blue is what you write, green the generated simulators"))

    def node(x, y, w, h, color, title, sub=None, mono=True, dash=None):
        c = C[color]
        s.rect(x, y, w, h, color, rx=10, sw=1.6, dash=dash, shadow=True)
        if sub:
            s.text(x + w / 2, y + h / 2 - 3, title, 14, c["text"], 700, "middle", mono)
            s.text(x + w / 2, y + h / 2 + 16, sub, 12, MUTED, 400, "middle")
        else:
            s.text(x + w / 2, y + h / 2 + 5, title, 14, c["text"], 700, "middle", mono)

    def tool(x, y, label):
        return s.pill(x, y, label, "violet", 12.5, 9, 24, mono=True)

    def lane(y, h, label, cmd):
        s.rect(20, y, 1000, h, "gray", rx=12, fill=T["LANE"], stroke=T["LANE_STROKE"], sw=1.2)
        s.text(34, y + 24, label, 14, INK, 700)
        s.text(1006, y + 24, cmd, 12.5, MUTED, 500, "end", mono=True)

    lane(60, 196, L("构建", "Build"), "make ARCH=myrv sim rsim")
    node(40, 126, 170, 56, "blue", "isa/myrv/", L("你只改这里", "edit only this"))
    s.arrow([(212, 154), (276, 154)], MUTED, 2)
    s.text(244, 144, L("make 拷贝", "copy"), 12, MUTED, 500, "middle")
    node(280, 126, 190, 56, "gray", "build/isa/myrv/", L("构建副本：不要改", "build copy: do not edit"), dash="6 4")
    s.pill(292, 192, L("报错路径指向这里", "errors point here"), "orange", 12, 9, 24)
    s.arrow([(472, 142), (520, 112), (560, 112)], MUTED, 2)
    s.arrow([(472, 166), (520, 210), (560, 210)], MUTED, 2)
    tool(564, 100, "gen_sail.py")
    tool(564, 198, "gen_rust.py")
    s.arrow([(672, 112), (730, 112)], MUTED, 2)
    s.arrow([(672, 210), (730, 210)], MUTED, 2)
    node(734, 88, 270, 48, "green", "build/myrv/xinyu-sim", None)
    node(734, 186, 270, 48, "green", "build/rsim/myrv/release/rsim", None)
    s.text(869, 162, L("两个模拟器，同一份语义", "two simulators, one semantics"), 12.5, C["green"]["text"], 600, "middle")

    lane(272, 140, L("运行一个程序", "Run a program"), "asm.py · xinyu-sim / rsim · disasm.py")
    node(40, 320, 150, 56, "blue", "work/sum.s", L("汇编文本", "assembly text"))
    s.arrow([(192, 348), (232, 348)], MUTED, 2)
    tool(236, 336, "asm.py")
    s.arrow([(308, 348), (346, 348)], MUTED, 2)
    node(350, 320, 130, 56, "gray", "sum.hex", L("指令字", "words"))
    s.arrow([(482, 348), (532, 348)], C["green"]["stroke"], 2)
    node(536, 320, 180, 56, "green", "xinyu-sim / rsim", None)
    s.arrow([(718, 348), (760, 348)], MUTED, 2)
    node(764, 310, 240, 76, "gray", "dump", "steps · PC · reg · mem", mono=True)
    s.arrow([(415, 378), (415, 398), (300, 398)], MUTED, 1.6, dash="4 3")
    s.text(296, 402, L("disasm.py → 反汇编文本", "disasm.py → disassembly"), 12, MUTED, 500, "end")

    lane(428, 168, L("定向测试", "Directed tests"), "make ARCH=myrv sim-test rsim-test")
    node(40, 472, 150, 52, "blue", "*.prog", L("form id + 字段", "form id + fields"))
    node(40, 534, 150, 48, "blue", "*.state", L("初始状态", "initial state"))
    s.arrow([(192, 498), (232, 498)], MUTED, 2)
    tool(236, 486, "encode.py")
    s.arrow([(331, 498), (366, 498)], MUTED, 2)
    node(370, 472, 110, 52, "gray", "*.hex", None)
    s.arrow([(482, 498), (532, 498)], C["green"]["stroke"], 2)
    s.arrow([(192, 558), (512, 558), (512, 512), (532, 512)], MUTED, 1.6)
    node(536, 472, 180, 52, "green", "xinyu-sim / rsim", None)
    s.arrow([(718, 498), (760, 498)], MUTED, 2)
    node(764, 468, 110, 60, "gray", L("输出", "output"), None, mono=False)
    s.text(889, 503, "⇄", 22, C["orange"]["stroke"], 700, "middle")
    node(904, 468, 100, 60, "blue", "*.expected", None)
    s.pill(764, 538, L("逐字比较：一致 pass，不一致打印 diff", "compared exactly: pass, or a diff"), "orange", 12, 10, 26)
    return s, "build-flow"


# ---------------------------------------------------------------- 5. one step, and a branch
def step_cycle():
    s = Svg(1040, 520, L("模型怎样执行一步，分支怎样跳", "How the model runs a step, and how a branch jumps"))
    heading(s, L("模型怎样执行一步", "How the model runs a step"),
            L("以及分支的立即数怎样拼出来", "and how a branch's immediate is put together"))
    steps = [
        ("blue", L("① 取指", "① Fetch"), L("从内存 M 的 PC 处读 4 字节", "4 bytes from memory M at PC")),
        ("violet", L("② 译码", "② Decode"), L("找唯一匹配的 form", "find the one matching form")),
        ("teal", "③ NEXT_PC = PC + 4", L("默认顺序执行下一条", "by default, the next instruction")),
        ("green", L("④ 执行 execute(d)", "④ Run execute(d)"), L("读写寄存器和内存，可改 NEXT_PC", "reads, writes, may change NEXT_PC")),
        ("orange", "⑤ RETIRE_OK", L("PC = NEXT_PC，回到 ①", "PC = NEXT_PC, back to ①")),
    ]
    for i, (color, title, sub) in enumerate(steps):
        y = 66 + i * 82
        s.rect(40, y, 280, 62, color, rx=12, shadow=True)
        s.text(56, y + 27, title, 15, C[color]["text"], 700, mono=title.startswith("③") or title.startswith("⑤"))
        s.text(56, y + 48, sub, 12.5, MUTED)
        if i < 4:
            s.arrow([(180, y + 62), (180, y + 80)], MUTED, 2)
    s.arrow([(40, 66 + 4 * 82 + 31), (22, 66 + 4 * 82 + 31), (22, 97), (38, 97)], C["orange"]["stroke"], 2)
    s.arrow([(320, 66 + 82 + 31), (360, 66 + 82 + 31)], C["rose"]["stroke"], 2)
    s.pill(364, 66 + 82 + 18, L("不匹配：非法指令，停下", "no match: illegal, stops"), "rose", 12.5, 10, 26)
    s.arrow([(320, 66 + 3 * 82 + 20), (360, 66 + 3 * 82 + 20)], C["rose"]["stroke"], 2)
    s.pill(364, 66 + 3 * 82 + 7, L("RETIRE_ILLEGAL：报错停下", "RETIRE_ILLEGAL: stops"), "rose", 12.5, 10, 26)
    s.arrow([(320, 66 + 3 * 82 + 46), (360, 66 + 3 * 82 + 46)], C["green"]["stroke"], 2)
    s.pill(364, 66 + 3 * 82 + 33, L("调用 halt()：正常停机", "halt(): a normal end"), "green", 12.5, 10, 26)
    X0, Y0, bw = 560, 96, 440 / 32
    s.text(X0, 78, L("BEQ / BNE 的 B 型编码（32 位）", "BEQ / BNE: the B-type encoding (32 bits)"), 14, INK, 700)
    segs = [(31, 31, "rose", "a"), (30, 25, "orange", "c"), (24, 12, "gray", "rs2 · rs1 · funct3"),
            (11, 8, "teal", "d"), (7, 7, "violet", "b"), (6, 0, "gray", "opcode")]
    pos = {}
    for hi, lo, color, label in segs:
        x = X0 + (31 - hi) * bw
        w = (hi - lo + 1) * bw
        c = C[color]
        s.rect(x, Y0, w, 40, color, rx=0, fill=c["fill"] if color == "gray" else c["stroke"], stroke=c["stroke"], sw=1.2)
        s.text(x + w / 2, Y0 + 25, label, 12 if color == "gray" else 14,
               c["text"] if color == "gray" else T["ONSOLID"], 700, "middle", mono=color != "gray")
        s.text(x + w / 2, Y0 + 56, f"{hi}" if hi == lo else f"{hi}:{lo}", 11, MUTED, 400, "middle", mono=True)
        pos[label] = x + w / 2
    s.add(f'<rect x="{X0}" y="{Y0}" width="440" height="40" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    Y1 = 214
    s.text(X0, Y1 + 60, L("按 <range> 的书写顺序从高到低拼接，得到 12 位字段值",
                          "joined high to low in <range> order: a 12-bit field value"), 13, INK, 600)
    order = [("a", "rose", "[12]", 1), ("b", "violet", "[11]", 1), ("c", "orange", "[10:5]", 6), ("d", "teal", "[4:1]", 4)]
    cw = 440 / 12
    x = X0
    for label, color, bits, n in order:
        w = n * cw
        c = C[color]
        s.rect(x, Y1, w, 40, color, rx=0, fill=c["stroke"], stroke=T["CARD"], sw=1.5)
        s.text(x + w / 2, Y1 + 25, label + bits if n > 1 else label, 13, T["ONSOLID"], 700, "middle", mono=True)
        s.arrow([(pos[label], Y0 + 62), (x + w / 2, Y1 - 2)], c["stroke"], 1.4, dash="3 3")
        x += w
    Y2 = 326
    s.arrow([(X0 + 220, Y1 + 70), (X0 + 220, Y2 - 4)], MUTED, 2)
    s.text(X0 + 232, Y1 + 92, L("× 2（scale=\"2\"，最低位补 0）", "× 2 (scale=\"2\", a 0 below)"), 13, C["violet"]["text"], 600)
    s.rect(X0, Y2, 440, 44, "blue", rx=10, shadow=True)
    s.text(X0 + 220, Y2 + 28, L("d.imm：13 位有符号字节偏移", "d.imm: a 13-bit signed byte offset"), 14, C["blue"]["text"], 700, "middle")
    s.arrow([(X0 + 220, Y2 + 48), (X0 + 220, Y2 + 74)], MUTED, 2)
    s.rect(X0, Y2 + 78, 440, 76, "green", rx=10, shadow=True)
    s.text(X0 + 16, Y2 + 104, "target = PC + sail_sign_extend(d.imm, 64)", 13, INK, 600, mono=True)
    s.text(X0 + 16, Y2 + 128, L("条件成立：NEXT_PC = target", "taken: NEXT_PC = target"), 13, INK, 600, mono=True)
    s.text(X0 + 16, Y2 + 146, L("不成立：NEXT_PC 保持 PC + 4", "not taken: NEXT_PC stays PC + 4"), 12.5, MUTED)
    return s, "step-cycle"


# ---------------------------------------------------------------- 6. the layers of verification
def verification():
    s = Svg(1040, 560, L("每一层验证比较什么、能发现什么", "What each layer of verification compares and finds"))
    heading(s, L("每一层验证比较什么、能发现什么", "What each layer compares, and what it finds"))
    cols = [(30, L("层 · 命令", "Layer · command")), (210, L("比较什么", "Compares")), (480, L("能发现什么", "Finds"))]
    for x, h in cols:
        s.text(x + 6, 76, h, 13, MUTED, 700)
    rows = [
        ("violet", L("静态检查", "Static check"), L("描述本身", "the description itself"),
         L("字段重叠、两个 form 冲突、汇编歧义、语义的类型和位宽", "overlaps, clashing forms, ambiguous syntax, types and widths"), "check"),
        ("blue", L("定向测试", "Directed tests"), L("模拟器输出 vs 你核对过的期望", "output vs expectations you checked"),
         L("语义写错（前提是期望经过你核对）", "wrong semantics (if you checked the expectations)"), "sim-test rsim-test"),
        ("teal", L("随机差分", "Differential"), L("Sail 模拟器 vs Rust 模拟器", "the Sail vs the Rust simulator"),
         L("两份生成实现不一致；查不出两边一起错", "the two generated models disagree; not both wrong"), "fuzz"),
        ("green", L("等价性", "Equivalence"), L("新指令 vs 它替换的指令序列", "new instruction vs its sequence"),
         L("自定义指令的语义或声明写错", "a custom instruction or its declaration is wrong"), "equiv equiv-prove"),
        ("rose", L("外部参考", "References"), L("你的描述 vs llvm-mc / Spike", "your description vs llvm-mc / Spike"),
         L("编码、汇编语法、执行结果与真实 ISA 不符", "encodings, syntax or results unlike the real ISA"), "corpus · spike"),
        ("orange", L("覆盖率", "Coverage"), L("测试实际执行了哪些部分", "what the tests actually ran"),
         L("没测到的 form、字段取值和语义分支", "forms, field values and branches not reached"), "coverage"),
    ]
    for i, (color, name, what, finds, cmd) in enumerate(rows):
        y = 88 + i * 70
        c = C[color]
        s.rect(30, y, 812, 58, color, rx=12, fill=c["fill"], sw=1.4)
        s.rect(30, y, 170, 58, color, rx=12, fill=c["stroke"], sw=0)
        s.text(115, y + 26, name, 16, T["ONSOLID"], 700, "middle")
        s.text(115, y + 46, cmd, 12, T["ONSOLID"], 500, "middle", mono=True)
        s.text(216, y + 35, what, 13.5 if LANG == "zh" else 13, INK, 600)
        s.text(486, y + 35, finds, 13 if LANG == "zh" else 12.5, INK)
    s.add(f'<line x1="476" y1="88" x2="476" y2="{88 + 6 * 70 - 12}" stroke="{T["BORDER"]}" stroke-width="1.2"/>')
    groups = [(0, 3, L("描述自洽", "Self-consistent"), "violet"), (4, 4, L("与真实 ISA 一致", "Like the real ISA"), "rose"),
              (5, 5, L("测得够不够", "Tested enough"), "orange")]
    for a, b, label, color in groups:
        y1, y2 = 88 + a * 70 + 4, 88 + b * 70 + 54
        c = C[color]
        s.add(f'<path d="M858,{y1} h10 v{y2 - y1} h-10" fill="none" stroke="{c["stroke"]}" stroke-width="2.5"/>')
        s.text(878, (y1 + y2) / 2 + 5, label, 14 if LANG == "zh" else 13, c["text"], 700)
    s.text(30, 538, L("前四层只能证明描述自己前后一致；描述是否等于真实的 ISA，要靠外部参考或你核对过的定向测试。",
                      "The first four layers show only that the description agrees with itself; whether it is the real ISA takes references, or directed tests you checked."),
           13 if LANG == "zh" else 12.5, MUTED)
    return s, "verification"


# ---------------------------------------------------------------- 7. equivalence
def equivalence():
    s = Svg(1040, 470, L("自定义指令与指令序列的等价性检查", "Checking a custom instruction against its sequence"))
    heading(s, L("等价性检查：新指令和它替换的序列", "Equivalence: the new instruction and the sequence it replaces"),
            "SH1ADD ≡ slli + add" if LANG == "zh" else None)
    s.rect(330, 64, 380, 56, "gray", rx=12, shadow=True)
    s.text(520, 88, L("同一个初始状态 S", "The same initial state S"), 15, INK, 700, "middle")
    s.text(520, 108, L("全部寄存器（随机，或 z3 的符号值）", "every register (random, or z3's symbols)"), 12.5, MUTED, 400, "middle")
    s.pill(726, 79, L("前提：tmp ≠ rs1，tmp ≠ rs2", "given tmp ≠ rs1, tmp ≠ rs2"), "orange", 12.5, 10, 26)
    s.arrow([(430, 122), (250, 160)], C["blue"]["stroke"], 2.2)
    s.arrow([(610, 122), (790, 160)], C["violet"]["stroke"], 2.2)
    s.panel(60, 164, 380, 132, "blue", L("新指令（1 条）", "The new instruction (1)"))
    s.rect(80, 218, 340, 40, "blue", rx=8, fill=T["CARD"], sw=1.3)
    s.text(250, 244, "sh1add rd, rs1, rs2", 15, C["blue"]["text"], 700, "middle", mono=True)
    s.text(250, 282, "rd = (rs1 << 1) + rs2", 13, MUTED, 400, "middle", mono=True)
    s.panel(600, 164, 380, 132, "violet", L("基础指令序列（2 条）", "The base sequence (2)"))
    s.rect(620, 210, 340, 34, "violet", rx=8, fill=T["CARD"], sw=1.3)
    s.text(790, 233, "slli tmp, rs1, 1", 14, C["violet"]["text"], 700, "middle", mono=True)
    s.rect(620, 252, 340, 34, "violet", rx=8, fill=T["CARD"], sw=1.3)
    s.text(790, 275, "add  rd, tmp, rs2", 14, C["violet"]["text"], 700, "middle", mono=True)
    s.arrow([(250, 298), (250, 330), (400, 330)], C["blue"]["stroke"], 2.2)
    s.arrow([(790, 298), (790, 330), (640, 330)], C["violet"]["stroke"], 2.2)
    s.rect(404, 306, 232, 50, "orange", rx=12, shadow=True)
    s.text(520, 329, L("A 与 B 完全相同？", "A exactly equals B?"), 15, C["orange"]["text"], 700, "middle")
    s.text(520, 347, L("除 tmp 外的全部寄存器", "every register but tmp"), 12, MUTED, 400, "middle")
    s.text(325, 323, L("状态 A", "state A"), 13, C["blue"]["text"], 700, "middle")
    s.text(715, 323, L("状态 B", "state B"), 13, C["violet"]["text"], 700, "middle")
    s.panel(60, 380, 440, 72, "teal", L("make equiv：差分", "make equiv: differential"))
    s.text(76, 438, L("随机抽 20 组满足前提的状态，Sail 和 Rust 各跑一遍",
                      "20 random states meeting the preconditions, run on Sail and Rust"), 12.5, INK)
    s.panel(540, 380, 440, 72, "green", L("make equiv-prove：证明", "make equiv-prove: proof"))
    s.text(556, 438, L("z3 对所有满足前提的状态证明 A = B", "z3 proves A = B for every state meeting them"), 12.5, INK)
    return s, "equivalence"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for lang in ("zh", "en"):
        for theme in ("light", "dark"):
            use(lang, theme)
            for make in (overview, roadmap, anatomy, build_flow, step_cycle, verification, equivalence):
                svg, name = make()
                written.append(svg.save(name, theme))
    print(f"wrote {len(written)} diagrams to {OUT}")
