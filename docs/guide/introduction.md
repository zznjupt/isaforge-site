# What is ISAForge

ISAForge is a tool for instruction sets. You write an instruction set as one machine-readable specification: encodings, operands, legality conditions and assembly syntax in XML, and each instruction's semantics in [Sail](https://github.com/rems-project/sail). From it, ISAForge generates a decoder, an assembler, a disassembler, two functional simulators and an instruction manual, and checks them, one by one, against real tools and hardware.

## The idea

What is known about an instruction set usually lives in several places: the manual, the assembler, the disassembler, the simulator, the tests. Each is written by hand, each gets things wrong, and over time they drift apart.

ISAForge has you write it in one place. An instruction is one file, holding its bit fields, operands, syntax and semantics:

```xml
<form id="addi" layout="I">
  <operands>
    <operand name="rd" type="X"/>
    <operand name="rs1" type="X"/>
    <operand name="imm" type="simm" width="12"/>
  </operands>
  <encoding>
    <const field="opcode" value="0b0010011"/>
    <const field="funct3" value="0b000"/>
  </encoding>
  <syntax>addi {rd}, {rs1}, {imm}</syntax>
</form>
<operation>
  <execute><![CDATA[
    write_X(d.rd, read_X(d.rs1) + sail_sign_extend(d.imm, 64));
    RETIRE_OK
  ]]></execute>
</operation>
```

The assembler reads `<syntax>` to encode text and the disassembler prints with the same template; the decoder is generated from `<encoding>`, and `<execute>` is compiled into both the Sail and the Rust model. Change it once and every tool changes with it.

## The ISA package

An instruction set is written as an **ISA package** under `isa/<name>/`:

- `arch.xml`: the instruction length, the execution model (scalar, or SIMT with lanes and predicates), extensions, immediate types;
- `registers.xml`: register files and address spaces, which semantics reach through generated `read_X` and `write_X`;
- `layouts.xml`: bit layouts shared by many instructions, such as RISC-V's R, I and S types;
- `enums.xml`: named values, such as comparison conditions and modifiers;
- `instructions/*.xml`: one file per mnemonic, with its encodings (forms) and semantics (operations);
- `shared.xml`: Sail functions several instructions share.

## What you get

- **A toolchain**: a decoder, an assembler (aliases included), a disassembler, the reference simulator Sail compiles, and a much faster Rust simulator (one warp, a whole grid on many threads, or batches).
- **Verification**: a static check that proves no two encodings match the same word; random differential testing of the two simulators; proofs of equivalence for custom instructions; comparison with disassemblers, ISA simulators and hardware; coverage reports.
- **A manual**: a page per instruction with its encoding diagram, operands, syntax and semantics, and pages for the encoding space, registers, enums and shared functions.

## What it is for

- Specifying a new instruction set or a set of extensions, and having working tools right away;
- Exploring ISA design: add a fused instruction and prove it equivalent to the sequence it replaces;
- Writing an executable, checkable specification of an instruction set that exists only as binaries and a disassembler, such as a GPU's SASS;
- Providing the functional model for a cycle-level model.

ISAForge describes the instruction set, not the microarchitecture: it does not model pipeline timing and does not generate RTL.

As for kinds of processor, scalar CPUs and SIMT GPUs are supported today; NPUs and others are next.

Next: [Getting started](./getting-started).
