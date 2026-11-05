# Write and see

When writing an ISA package you want to know quickly whether what you just wrote is right, and what it looks like. ISAForge puts that in the editor, the terminal and the browser.

## Editor

```sh
make editor
```

It writes VS Code's settings locally and recommends Red Hat's XML extension. Then, editing an ISA package's files:

- elements and attributes complete, with documentation on hover;
- wrong elements, attributes and values are marked as you type;
- settings you already have stay; only what is missing is added.

IntelliJ maps `urn:xinyu:isa:1` to `schema/isa.xsd` under Schemas and DTDs; other editors point at `schema/catalog.xml`.

## Checked on every save

```sh
make ARCH=myrv watch
```

```text
preview: http://127.0.0.1:8000/   assembler: http://127.0.0.1:8000/__asm/
watching isa/myrv (Ctrl-C to stop)
[10:20:31] check passed, documentation updated (1.1 s)
```

On every save of a file of the ISA package it:

- rebuilds and checks the ISA package, running only its own checks;
- when the check passes, regenerates the manual, and the preview in the browser reloads;
- when it fails, shows the errors in the terminal and at the top of the preview, with paths to the file you edit, and keeps the manual at the last version that passed.

The assembler's own checks run after the manual is updated, in the background, over the instructions you changed. For an ISA package of a thousand encodings such as the B300 SASS the manual is updated in about 18 seconds, and the preview shows which background step is running. Changes are found by content, so an editor's temporary files never start a check.

## Assembler and disassembler

The preview's top bar links to an assembler in the browser, using the last build that passed its check:

<div class="forge-figure">

[![The assembler page: each line assembled with its fields drawn on the left, the instruction lookup on the right](/screens/asm-page.png){.light-only}](/screens/asm-page.png)
[![The assembler page, dark](/screens/asm-page-dark.png){.dark-only}](/screens/asm-page-dark.png)

</div>

- One instruction per line, machine code as you type, each field's bits drawn in the manual's colours;
- switch to "machine code → assembly" and paste words, including the output of a disassembler or objdump;
- **when you forget how to write it**: the lookup on the right searches by mnemonic or description and lists each form's syntax, what each operand takes and an example that "insert" puts in. Examples are made from the template with plain values and checked by the assembler, so another ISA package needs none written by hand;
- **when a line is wrong**: if the instruction is recognised but its operands are not, its right syntax is shown, and "replace" swaps the line; a misspelled mnemonic gets the instructions spelled closest to it;
- every form in the manual has a "try it" link to this page with its example filled in, and the page's address can be shared.

## The manual

<div class="forge-figure">

[![B300 SASS's IMAD in the manual: the form overview matrix and the encoding diagram](/screens/manual-imad.png){.light-only}](/screens/manual-imad.png)
[![B300 SASS's IMAD in the manual, dark](/screens/manual-imad-dark.png){.dark-only}](/screens/manual-imad-dark.png)

</div>

B300 SASS's IMAD has 52 forms. The manual first lays them out as a matrix of variants by operand kinds, so which have semantics shows at a glance; each form's encoding diagram tells fixed bits, operands and encoding tables apart in three colours, with the fields and operands side by side.
