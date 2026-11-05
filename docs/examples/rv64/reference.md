# Errors and commands

## Common errors

::: warning Warning
The paths in `make check`'s errors point at the build copy `build/isa/myrv/…`. The line numbers are the same as in the source files; **make your changes in the files under `isa/myrv/`**, as the build copy is overwritten on the next build. `make ARCH=myrv watch` turns the paths back into source paths for you.
:::

**When checking (`make check`)**

| Error (excerpt) | Cause | Fix |
|---|---|---|
| `ADDI.xml:5: form addi: layouts.xml:6: rs1: overlaps another field` | two fields of a layout overlap | check the msb and lsb of each `<range>`. It is often followed by a few width errors it causes, which go away once the overlap is fixed |
| `ADD.xml:5: form add and SUB.xml:5: form sub can match the same word, e.g. 0x00000033` | two forms can match the same instruction word, so decoding cannot tell them apart; after `e.g.` is a word both match | see the field-by-field comparison printed right after it (below the table) |
| `AMBIGUOUS …ADD.xml:5: form add and …SUB.xml:5: form sub both assemble 'add x0, x0, x0', to different words` | the syntax templates of two forms can produce the same text | change the `<syntax>` of one of them |
| `ADD.xml:16: form add: syntax references undeclared operand rs3` | a `{name}` in the syntax template is not an operand of this form | correct the name, or declare it in `<operands>` |
| `ADD.xml:20: ADD__add: write_X argument 1: bits(32) where bits(64) is expected` | a width mismatch in the semantics: a 32-bit value written to a 64-bit register | extend it to the target width with `sail_sign_extend`/`sail_zero_extend` |
| `ADD.xml:20: ADD__add: unknown function add64` | a call to a function that does not exist | use a built-in function, or define it in `shared.xml` (see `isa/rv64/shared.xml`) |

When two forms clash, the check sets them side by side, field by field. Here is the output when SUB's funct7 is mistakenly written the same as ADD's:

```text
build/isa/myrv/instructions/ADD.xml:5: form add and build/isa/myrv/instructions/SUB.xml:5: form sub can match the same word, e.g. 0x00000033
    bits     add             sub
    31:25    funct7=0000000  funct7=0000000  same constant in both
    24:20    rs2             rs2
    19:15    rs1             rs1
    14:12    funct3=000      funct3=000      same constant in both
    11:7     rd              rd
    6:0      opcode=0110011  opcode=0110011  same constant in both
    to tell them apart: give one form a different constant in funct7 (31:25), funct3 (14:12) or opcode (6:0)
```

- `same constant in both`: both sides fix these bits to the same value, and this is where the clash is;
- `only … fixes it`: only one side fixes these bits while the other has an operand there; fixing a different constant on the other side tells them apart;
- the last line gives the fix directly.

**When running and assembling**

| Error (excerpt) | Cause | Fix |
|---|---|---|
| `illegal instruction at pc 0x… word 0x…` | the instruction word matches no enabled form | check the encoding, or whether `FEATURES` disabled it |
| `work/mul.s:3: no instruction matches 'mul x3, x1, x2'` | the assembler does not recognize the line (for example, assembling `mul` with only I enabled) | check the line against `<syntax>`, or whether `FEATURES` disabled it; the assembler does not support comments or labels |


## Checklist before delivery

```sh
make ARCH=myrv check sim-test rsim-test fuzz equiv equiv-prove
make ARCH=myrv FEATURES="I M" spike
make ARCH=myrv coverage docs
```

| Line | Verification covered |
|---|---|
| Line 1 | static check, directed tests, differential testing, equivalence |
| Line 2 | external references (if your ISA has them) |
| Line 3 | the coverage report and the instruction manual |


## Next steps

- **The full RV64I**: `isa/rv64/`, which comes with ISAForge, has all 72 forms of I, M and Zba, plus `shared.xml` (functions the semantics share, such as division), `enums.xml` (the enum operands of FENCE) and more aliases. Run the same commands with `make ARCH=rv64 …`.
- **Writing ISA packages**: [Writing an ISA package](../../guide/package) covers layouts, aliases, extensions and the execution model; `schema/isa.xsd` is the XML schema.
- **GPU / SIMT architectures**: the execution model declares the lane count, predicates and launch identity; see [Execution model](../../guide/package#execution-model).

## Appendix: commands

| Task | Command |
|---|---|
| Static check | `make ARCH=myrv check` |
| Check as you edit (check, manual, preview, assembler page) | `make ARCH=myrv watch` (`WATCH_ARGS=--once` for a single round) |
| Encoding space | `make ARCH=myrv encoding-map`, or the manual's encoding space page |
| Build both simulators | `make ARCH=myrv sim rsim` |
| Assemble | `python3 tools/asm.py build/isa/myrv PROGRAM.s PROGRAM.hex` |
| Encode a `.prog` by form | `python3 tools/encode.py build/isa/myrv PROGRAM.prog PROGRAM.hex` |
| Disassemble | `python3 tools/disasm.py build/isa/myrv PROGRAM.hex [--no-aliases]` |
| Run (Sail) | `build/myrv/xinyu-sim [--state STATEFILE] [--max-steps N] PROGRAM.hex` |
| Run (Rust) | `build/rsim/myrv/release/rsim run PROGRAM.hex --arch myrv [--state STATEFILE] [--max-steps N]` |
| Directed tests | `make ARCH=myrv sim-test rsim-test` |
| Differential testing | `make ARCH=myrv fuzz` (`FUZZ_COUNT`, `FUZZ_SEED`) |
| Equivalence | `make ARCH=myrv equiv equiv-prove` |
| Enable only some extensions | add `FEATURES="I M"` to any command |
| External references | `make ARCH=myrv corpus`, `make ARCH=myrv FEATURES="I M" spike` |
| Coverage, manual | `make ARCH=myrv coverage docs` |
