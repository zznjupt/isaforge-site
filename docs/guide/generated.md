# What is generated

From one ISA package, `make` generates the following. They all read the same specification, so a change shows up in every tool at once.

| Product | Command | Where |
|---|---|---|
| Assembler | `python3 tools/asm.py build/isa/<name> in.s out.hex` | assembles by `<syntax>` and aliases; errors name the file and line |
| Disassembler | `python3 tools/disasm.py build/isa/<name> prog.hex` | prints each word's address, word and text; `--no-aliases` without aliases |
| Sail reference model | `make ARCH=<arch> sim` | `build/<arch>/xinyu-sim` |
| Rust fast model | `make ARCH=<arch> rsim` | `build/rsim/<arch>/release/rsim` |
| Instruction manual | `make ARCH=<arch> docs` | `build/<arch>/docs/index.html` |
| Encoding space | `make ARCH=<arch> encoding-map` | a summary in the terminal; a grid in the manual |

## Two simulators

**The Sail reference model**: ISAForge writes the registers, the execution model and each instruction's semantics as Sail, which Sail compiles to C. It is the reference: it runs the semantics as they are written.

**The Rust fast model**: ISAForge translates the same semantics into Rust: bit vectors as `u64`, integers as `i64` or `i128` by the range it works out, per-lane loops as whole-warp operations. It is there to be fast, and to check the Sail model against.

Both read and write the same state text: the state printed at the end of a run can be loaded back with `--state` as it is.

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

The Rust model can also launch a whole kernel by grid and block on many threads, or run a batch of cases:

```sh
rsim run PROGRAM.hex --arch <name> --grid X,Y,Z --block X,Y,Z --threads N
rsim batch MANIFEST --arch <name> --threads N
rsim decode PROGRAM.hex --arch <name>
```

On one thread the Rust model runs about 170 times as fast as the Sail reference model, and over 600 times as fast on many.

## The manual

`make docs` writes a page per instruction: its summary and description, an overview of its forms (and which have semantics), and for each form its syntax, encoding diagram, fields, operands, legality conditions and semantics. Other pages:

- **Index**: grouped by extension or initial letter, filterable, marking the instructions without semantics yet;
- **Encoding space**: a grid of the first-level encoding bits, darker where fuller; empty cells are free for new instructions;
- **Registers, enums, shared Sail**: every register file, every enum (codes against assembly text, and who uses it), every shared function (signature, description, callers);
- **Coverage**: after `make coverage`, what each instruction and form executed, which field values and branches were reached.

## Encoding space

Before adding an instruction, see what is free. The tutorial's ISA package of 13 instructions:

```text
myrv: 13 forms, 32-bit words; 2.1% of the encoding space is used
every form fixes 1:0 = 11; the 75% of the space where these bits differ is free
first level 6:2: 32 cells, 2 full, 6 partly used, 24 free
  6:0=0110011  0.39% used  add mul sh1add sub
  6:0=1100011    25% used  beq bne
  …
```

The first level is the bits every form fixes but not all to one value, so RV64I gets the opcode map of the RISC-V specification by itself. The check has already proved forms never overlap, so each cell's use is an exact sum over its forms.

The manual draws the same map as a grid. For the full RV64 ISA package the rows and columns are opcode bits 6:5 and 4:2, darker where fuller:

<div class="forge-figure">

[![rv64's encoding space: 13 cells hold instructions, 19 are free](/screens/encoding-rv64.png){.light-only}](/screens/encoding-rv64.png)
[![rv64's encoding space, dark](/screens/encoding-rv64-dark.png){.dark-only}](/screens/encoding-rv64-dark.png)

</div>
