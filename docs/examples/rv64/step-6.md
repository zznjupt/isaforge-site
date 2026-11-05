# Step 6: Extensions and feature switches

> **Goal**: make multiplication an optional extension, M, and build by combination of extensions.

## ① Declare the extensions

In `isa/myrv/arch.xml`, after `<execution/>`, add:

```xml
  <features>
    <feature name="I">
      <description>The base integer instructions.</description>
    </feature>
    <feature name="M" requires="I">
      <description>Integer multiplication.</description>
    </feature>
  </features>
```

## ② Add an instruction that belongs to the extension

Create `isa/myrv/instructions/MUL.xml`, marking `<instruction>` with `feature="M"`:

```xml
<instruction xmlns="urn:xinyu:isa:1" mnemonic="MUL" feature="M">
```

- The semantics are `write_X(d.rd, read_X(d.rs1) * read_X(d.rs2))`; the whole file is below;
- Elements without `feature` are always present, so the earlier instructions need no change.

::: details isa/myrv/instructions/MUL.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="MUL" feature="M">
  <summary>Multiply registers</summary>
  <description>Multiplies <op>rs1</op> by <op>rs2</op> and writes the low 64 bits of the product to <op>rd</op>.</description>
  <form id="mul" layout="R">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110011"/>
      <const field="funct3" value="0b000"/>
      <const field="funct7" value="0b0000001"/>
    </encoding>
    <syntax>mul {rd}, {rs1}, {rs2}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, read_X(d.rs1) * read_X(d.rs2));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

## ③ Build by combination of extensions

At build time `FEATURES` chooses the extensions to enable; without it, all are enabled. Write a program, `work/mul.s`:

```text
addi x1, x0, 6
addi x2, x0, 7
mul x3, x1, x2
ecall
```

```sh
make ARCH=myrv sim
python3 tools/asm.py build/isa/myrv work/mul.s work/mul.hex
build/myrv/xinyu-sim work/mul.hex            # x3 = 0x2A
make ARCH=myrv FEATURES="I" sim
build/myrv/xinyu-sim work/mul.hex            # only I enabled: MUL does not exist
```

With only I enabled, MUL's instruction word is an illegal instruction; the simulator stops and exits with status 1:

```text
illegal instruction at pc 0x0000000000000008
  word 0x022081B3
steps 3
PC 0x0000000000000008
reg x1 0x0000000000000006
reg x2 0x0000000000000007
```

- **Disabled means absent**: the decoder, assembler, disassembler and documentation do not see it;
- When you are done, `make ARCH=myrv sim rsim` enables everything again.
