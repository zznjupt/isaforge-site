# Verification

The two simulators are generated from the same specification, so their agreeing shows only that ISAForge generated both faithfully; semantics written wrong are wrong in both. ISAForge's verification therefore has layers, each finding what the one before cannot.

| Layer | Command | What it checks |
|---|---|---|
| Static check | `make check` | the structure of encodings, syntax and semantics; unique decoding; unambiguous assembly |
| Directed tests | `make sim-test rsim-test` | written programs reach their expected state on both models |
| Differential testing | `make fuzz`, `make fuzz-launch` | random programs from random states: Sail model ≡ Rust model |
| Equivalence | `make equiv`, `make equiv-prove` | a new instruction ≡ the sequence it replaces, compared at random and proved with z3 |
| External references | `make check` (corpora), `make spike` | disassembly and assembly against nvdisasm and llvm-mc, execution against Spike |
| Hardware | hardware comparison | the same words on a GPU and in the model, compared input by input |
| Coverage | `make coverage` | the forms, field values and branches no test ever reached |

## Static check

`make check` checks the specification before anything is generated: fields fit the word and do not overlap; each `<decode>` assigns every input of its operation once; semantics stay within the Sail subset, with matching types and widths.

The most important property is **unique decoding**: the check proves that any two decodable forms have a field whose allowed values are disjoint, so a word matches at most one form. When two forms cannot be told apart, they are compared field by field:

```text
ADD.xml:5: form add and SUB.xml:5: form sub can match the same word, e.g. 0x00000033
    bits     add             sub
    31:25    funct7=0000000  funct7=0000000  same constant in both
    24:20    rs2             rs2
    19:15    rs1             rs1
    14:12    funct3=000      funct3=000      same constant in both
    11:7     rd              rd
    6:0      opcode=0110011  opcode=0110011  same constant in both
    to tell them apart: give one form a different constant in funct7 (31:25), funct3 (14:12) or opcode (6:0)
```

## Differential testing

`make fuzz` generates random programs from the ISA package: random forms and field values, a random initial state over every register file, a random stretch of memory near a register's value; for a SIMT ISA package it also draws grids and blocks and runs every warp of every cell (`make fuzz-launch`). The two models must print exactly the same and exit the same way; when they do not, the case is kept with the command to reproduce it.

Every ISA package with semantics runs 300 random programs each time, the two models always agreeing; RV64's 300 programs execute 31097 instructions and use all 71 forms that have semantics.

## Proving equivalence

When you design a fused instruction, the best reference is the sequence it replaces. Declare the equivalence in the instruction:

```xml
<equivalence>
  <sequence>
    <step form="slli" rd="tmp" rs1="rs1" shamt="1"/>
    <step form="add" rd="rd" rs1="tmp" rs2="rs2"/>
  </sequence>
  <temps><temp name="tmp" file="X"/></temps>
  <preconditions>
    <distinct a="tmp" b="rs1"/>
    <distinct a="tmp" b="rs2"/>
  </preconditions>
</equivalence>
```

`make equiv` draws operands and whole initial states that meet the preconditions, runs the new instruction and the sequence, and compares all state but the temporaries; `make equiv-prove` uses Sail's SMT back end and z3 to prove it holds for every operand and state that meets them. RV64's six Zba instructions are each proved in under 1.2 seconds:

```text
SH1ADD: proved (0.73s, z3)
SH2ADD.UW: proved (0.73s, z3)
```

When a declaration is wrong, z3 gives a counterexample: the operands and initial register values that make the two differ.

```text
SH1ADD: NOT proved (counterexample, 0.61s)
  counterexample:
    operands: rs2 = x4, rs1 = x2, rd = x6, temp tmp = x16
    initial X: x2 (rs1) = 0x000007FFFFFFFFFF, x4 (rs2) = 0x0000000000000008, …
```


## External references

- **Disassembly**: an ISA package can carry reference corpora (words and the text a reference tool prints for them), compared word for word by `make check`. The B300 SASS against NVIDIA's nvdisasm: 12189 / 12189; RV64 against llvm-mc: 4441 / 4441 with aliases, 4428 / 4428 without;
- **Assembly round trip**: each text of a corpus must assemble back to the same word, or to another encoding that prints the same. RV64's corpora all assemble back to their original words; the 4732 words of real B300 code all assemble to words that print the same text;
- **Execution**: `make ARCH=rv64 spike` runs 21 directed and 300 random programs (36039 instructions) on Spike, the Sail model and the Rust model; registers, PC and every byte of memory agree;
- **Hardware**: the hardware comparison rewrites the instruction words under test into a cubin ptxas generated, runs them on a B300 and in the model on the same inputs, and compares the R, P, UR and UP registers one by one. 61 instruction families, 4457 combinations, all agree.

## Coverage

`make coverage` runs every directed test and random program on a counting build of the Rust model and records how often each form ran, which values each operand field took (register numbers, enum values, boundary classes of immediates), and whether each `if` and `match` branch in the semantics was taken:

```text
rv64: 71/71 modeled forms executed, 33/40 branches taken, 192 fields with unseen values
```

The report lists everything not reached with its line in the XML, and the manual's coverage page draws it as tables.
