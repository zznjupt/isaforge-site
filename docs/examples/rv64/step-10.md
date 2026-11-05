# Step 10: Coverage and the manual

> **Goal**: find what the tests have not reached, and generate the instruction manual.

## ① Coverage

```sh
make ARCH=myrv coverage
```

It runs every directed test and random program on a counting build of the Rust model, and records which forms, field values and semantic branches were executed. It prints a one-line summary at the end and writes the full report to `build/coverage/myrv/report.txt`:

```text
myrv: 13/13 modeled forms executed, 2/5 branches taken, 11 fields with unseen values -> build/coverage/myrv/report.txt
```

The main part of the report (excerpt):

```text
forms with semantics executed: 13/13
semantic branches taken: 2/5 (40.0%)

forms with semantics never executed (0):

operand field values never seen (11 fields):
  field:beq:imm: zero, negative minimum, negative
  field:bne:rs1: x16, x18, x20, x22, x23, x27
  field:lui:imm: high bit only, all below the high bit
  …
semantic branches never taken (3):
  build/isa/myrv/instructions/BEQ.xml:21  BEQ  then
  build/isa/myrv/instructions/BNE.xml:21  BNE  then
  build/isa/myrv/instructions/JAL.xml:18  JAL  then
```

| Part | Meaning | What to do |
|---|---|---|
| forms with semantics never executed | forms that have semantics but never ran | should be empty |
| operand field values never seen | for register fields, the registers that never appeared; for immediate fields, the boundary classes not reached (0, 1, all ones, the most negative, the most positive and so on), listing only classes the field can take (branch offsets are multiples of 2, so there is no 1 and no all ones; unsigned fields use names such as `high bit only`) | add directed tests for the boundary values that matter |
| semantic branches never taken | branches in the semantics never reached, with their line in the XML | all three above are the "misaligned jump target" branch, which needs a directed test of its own |

::: info Note
The paths in the report point at the build copy `build/isa/myrv/…`. Make your changes in the source files under `isa/myrv/`; the line numbers are the same.
:::

## ② The instruction manual

```sh
make ARCH=myrv docs
open build/myrv/docs/index.html
```

The index page opens with a few numbers (instructions, forms, the share with semantics), followed by the instructions grouped by feature: description, syntax, and a semantics column, where a green ✓ means an `<execute>` is written and "no semantics" means the simulators stop when they reach it. The navigation bar at the top leads to the encoding space, enums, shared Sail definitions and coverage pages.

Each instruction has a page with:

- when it has several forms, an overview of its forms first, so which have semantics is plain at a glance;
- a card for each form: assembly syntax, encoding diagram (blue for fixed bits, green for operands, orange for encoding tables or expressions), field and operand tables, the semantics code and the description you wrote;
- shared functions used in the semantics, which link to the shared Sail definitions page.

After a `coverage` run, the coverage page shows what each instruction and form executed, and which field values and branches were reached.

## ③ The encoding space

Before adding instructions, see where the encoding space is still free:

```sh
make ARCH=myrv encoding-map
```

```text
myrv: 13 forms, 32-bit words; 2.1% of the encoding space is used
every form fixes 1:0 = 11; the 75% of the space where these bits differ is free
first level 6:2: 32 cells, 2 full, 6 partly used, 24 free
  free: 6:0=0000111 … 6:0=0001111 (3 cells); 6:0=0010111 … 6:0=0011111 (3 cells); 6:0=0100111 … 6:0=0101111 (3 cells); 6:0=0111011 … 6:0=1011111 (10 cells); 6:0=1100111 … 6:0=1101011 (2 cells); 6:0=1110111 … 6:0=1111111 (3 cells)
  6:0=0000011    12% used  ld
  6:0=0010011    13% used  addi slli
  6:0=0100011    12% used  sd
  6:0=0110011  0.39% used  add mul sh1add sub
  6:0=0110111   100% used  lui
  6:0=1100011    25% used  beq bne
  6:0=1101111   100% used  jal
  6:0=1110011  <0.01% used  ecall
```

| Line | Meaning |
|---|---|
| `2.1% of the encoding space is used` | the 13 forms together take 2.1% of the whole 32-bit encoding space |
| `every form fixes 1:0 = 11` | bits 1:0 are 11 in every instruction; the 3/4 of the space where these two bits take other values is entirely free (RISC-V's compressed instructions use this part) |
| `first level 6:2` | the first level is "the bits every form fixes but not all to one value", which here is exactly the opcode map of the RISC-V specification |
| `free: …` | the cells that are entirely free, listed by their full value of 6:0 |
| each line after | a cell in use: the share used and the instructions in it. In `0110011`, for example, ADD, SUB, MUL and SH1ADD use only 0.39%, told apart by funct3 and funct7, with plenty of room left |

The manual's encoding space page (`encoding.html`) draws the same map as a grid: the rows and columns are bits of the first level, darker cells are fuller, and blank cells are entirely free. Hover over a cell to see its share used and all its instructions; click it to see which constants each form fixes beyond the first level.
