# RV64I from scratch

> Describe the instruction set in XML and the semantics of each instruction in Sail; ISAForge generates the assembler, the disassembler, two functional simulators and the manual, and gives you a whole set of checks that they are right. This tutorial walks you through it once, step by step.

**What you will build**

- An RV64I subset, `myrv`, written from an empty directory: 13 instructions covering arithmetic, shifts, branches, jumps, loads and stores, multiplication and one custom instruction;
- its assembler, disassembler, Sail reference simulator, fast Rust simulator and manual;
- six layers of verification that it is right: the static check, directed tests, differential testing, a proof of equivalence, external references (llvm-mc, Spike) and coverage.

**What you need**

- About an hour of work, plus a few minutes waiting for builds and random tests;
- the basic ideas of an instruction set (registers, encodings, immediates). You do not need to learn Sail first; every construct the tutorial uses is explained.

Every file in the tutorial is given in full; follow along and you get exactly the output shown here.

<div class="forge-figure">

![The route: ten steps in four stages](/tutorial/roadmap-en.svg){.light-only}
![The route: ten steps in four stages](/tutorial/roadmap-en-dark.svg){.dark-only}

</div>

| Stage | Steps |
|---|---|
| Describe the ISA | [1. The skeleton and a first instruction](./step-1) · [2. Running a program](./step-2) · [3. The common instructions](./step-3) |
| Test | [4. Directed tests](./step-4) · [5. Differential testing](./step-5) |
| Extend the ISA | [6. Extensions and feature switches](./step-6) · [7. Aliases](./step-7) · [8. A custom instruction and its equivalence](./step-8) |
| Verify and deliver | [9. Checking against external references](./step-9) · [10. Coverage and the manual](./step-10) |

If you hit an error, or want to look up a command, see [Errors and commands](./reference).

## Before you start

**Setup**

- Run every command at the root of ISAForge;
- you need Python 3.10 or newer, `xmllint`, Sail 0.20.3 (opam switch `sail`), z3 and Rust;
- step 9 also needs llvm-mc, lld and Spike.

**Check the setup**

```sh
make ARCH=rv64 check
```

If the last line is `12/12 exact, 0 same text, 0 not encodable, 0 with no text, 0 untexted  assembler-only aliases  asm-only.tsv`, the setup works.

**A convention**

`ARCH=name` selects the ISA package to work on. This tutorial's ISA package is called `myrv`, so every command carries `ARCH=myrv`.

**Editor (recommended)**

Write the ISA package in an editor that understands XSD: elements and attributes complete, hovering shows their documentation, and mistakes are marked as you type.

- **VS Code**: run `make editor` once. It writes VS Code's settings locally (the recommended extension and the schema configuration; `make check` and `make watch` also write them when they are missing). Then open the ISAForge directory in VS Code and install the recommended XML extension when asked (Red Hat's `redhat.vscode-xml`); nothing else needs setting. Your own `.vscode/settings.json` is kept, and only the missing entries are added.
- **IntelliJ IDEs**: under Settings → Languages & Frameworks → Schemas and DTDs, add an entry with URI `urn:xinyu:isa:1` and file `schema/isa.xsd`.
- **Other editors**: if they support XML catalogs, point them at `schema/catalog.xml`.

::: info Note
An editor can only check the rules a schema can express (elements, attributes, values). Overlapping fields, encoding conflicts and Sail semantics need `make ARCH=myrv check`, or `make ARCH=myrv watch`, introduced at the end of [step 1](./step-1).
:::

## A first look at an ISA package

<div class="forge-figure">

![What you write, what ISAForge generates, and how it is verified](/tutorial/overview-en.svg){.light-only}
![What you write, what ISAForge generates, and how it is verified](/tutorial/overview-en-dark.svg){.dark-only}

</div>

**The files you will have at the end**

```text
isa/myrv/                  the ISA package itself
  arch.xml                   instruction length, execution model, extensions
  registers.xml              register files and memory
  layouts.xml                shared encoding layouts
  instructions/ADDI.xml …    one file per mnemonic
mk/myrv.mk                 tells the build where the ISA package and tests are
tests/myrv/                your directed tests
```

**Three ideas used throughout**

| Idea | Where it is written | What it is |
|---|---|---|
| Registers and memory | `registers.xml` | Semantics read and write them only through generated access functions, such as `read_X(i)`, `write_X(i, v)` and `read_M(address, bytes)` |
| An instruction = encoding + semantics | `instructions/*.xml` | `<form>` gives the encoding (which bits are fixed, which are operands) and the assembly syntax; `<operation>` gives the semantics in Sail |
| Layout | `layouts.xml` | A division into fields that several instructions share, such as RISC-V's I and R types. Written once, referred to by name |

Next: [The skeleton and a first instruction](./step-1).
