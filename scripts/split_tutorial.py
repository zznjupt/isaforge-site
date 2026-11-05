#!/usr/bin/env python3
"""Turn the tool's tutorial (docs/tutorial/README.md of ISAForge) into the
site's pages: one per step, an overview and a reference page. Diagrams
become light/dark pairs, GitHub alerts VitePress containers with Chinese
titles, and each step's subsections become the page's sections. The pages
are then edited by hand for the site, so run this only to start over.

    python3 scripts/split_tutorial.py PATH/TO/docs/tutorial/README.md docs/zh/examples/rv64
"""
import re
import sys
from pathlib import Path

ALERTS = {"NOTE": ("info", "说明"), "TIP": ("tip", "提示"), "IMPORTANT": ("warning", "重要"),
          "WARNING": ("warning", "注意"), "CAUTION": ("danger", "小心")}


def figure(m):
    alt, name = m.group(1), m.group(2)
    return (f'<div class="forge-figure">\n\n![{alt}](/tutorial/{name}-zh.svg){{.light-only}}\n'
            f'![{alt}](/tutorial/{name}-zh-dark.svg){{.dark-only}}\n\n</div>')


def alerts(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^> \[!(\w+)\]\s*$", lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        kind, title = ALERTS[m.group(1)]
        body = []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            body.append(lines[i][1:].lstrip(" ") if lines[i] != ">" else "")
            i += 1
        out += [f"::: {kind} {title}", *body, ":::"]
    return "\n".join(out)


def convert(text):
    text = re.sub(r"!\[([^\]]*)\]\(images/([\w-]+)\.svg\)", figure, text)
    text = alerts(text)
    text = re.sub(r"^#### ", "## ", text, flags=re.M)
    text = re.sub(r"\n---\n", "\n", text)
    return text.strip() + "\n"


def main(src, out):
    text = Path(src).read_text()
    parts = re.split(r"^## ", text, flags=re.M)
    head, sections = parts[0], {p.split("\n", 1)[0]: "## " + p for p in parts[1:]}
    out = Path(out)
    steps = [k for k in sections if k.startswith("第 ")]
    for n, title in enumerate(steps, 1):
        body = sections[title].split("\n", 1)[1]
        (out / f"step-{n}.md").write_text(convert(f"# {title}\n{body}"))
    index = head + sections["开始之前"] + sections["先认识一个 ISA 包"]
    (out / "index.md").write_text(convert(index))
    ref = "".join(sections[k] for k in ("常见报错", "交付前的检查清单", "下一步", "附录：命令速查"))
    (out / "reference.md").write_text(convert("# 常见报错与命令速查\n\n" + ref))
    print("wrote", len(steps), "steps, index and reference")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
