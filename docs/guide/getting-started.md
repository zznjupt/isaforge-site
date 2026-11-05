# Getting started

This page writes the smallest ISA package, `myrv`, from an empty directory: two RISC-V instructions, ADDI and an ECALL that stops the model. It checks it, assembles a program and runs it on both simulators. The full ten-step tutorial is [RV64I from scratch](../examples/rv64/).

## Setup

Run every command below at the root of ISAForge. You need:

- Python 3.10 or newer, and `xmllint`;
- Sail 0.20.3 (opam switch `sail`) and z3;
- Rust (ISAForge picks a suitable version by itself).

Check the setup first:

```sh
make ARCH=rv64 check
```

## The skeleton

`isa/myrv/arch.xml`: 32-bit words, scalar execution, two immediate types.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<arch xmlns="urn:xinyu:isa:1" name="myrv" length="32">
  <description>The tutorial's RV64I subset: 64-bit integer registers, scalar execution.</description>
  <execution/>
  <immediates>
    <immediate name="uimm" print="decimal"/>
    <immediate name="simm" signed="true" print="decimal"/>
  </immediates>
</arch>
```

`isa/myrv/registers.xml`: 32 registers of 64 bits, x0 always reading 0; a little-endian memory the program is fetched from.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<registers xmlns="urn:xinyu:isa:1">
  <file name="X" count="32" width="64" asm="x{n}">
    <description>32 general registers of 64 bits. x0 reads 0 and ignores writes.</description>
    <reg index="0" read="0" write="discard"/>
  </file>
  <memory name="M" address-width="64" endian="little" fetch="true">
    <description>Byte-addressed little-endian memory; the program is fetched from here.</description>
  </memory>
</registers>
```

`isa/myrv/layouts.xml`: both instructions use the I-type fields.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layouts xmlns="urn:xinyu:isa:1">
  <layout name="I">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
</layouts>
```

## Two instructions

`isa/myrv/instructions/ADDI.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ADDI">
  <summary>Add immediate</summary>
  <description>Adds <op>rs1</op> and the sign-extended <op>imm</op> and writes <op>rd</op>.</description>
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
</instruction>
```

- An operand with the same name as a layout field takes that field; `<encoding>` fixes the rest;
- `<syntax>` is the assembly template that both the assembler and the disassembler are made from;
- `<execute>` is the semantics in Sail, `d.name` the value of an operand.

`isa/myrv/instructions/ECALL.xml`: every bit fixed, and running it stops the model.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ECALL">
  <summary>Environment call</summary>
  <description>Requests a service from the execution environment; this model stops here.</description>
  <form id="ecall" layout="I">
    <operands/>
    <encoding>
      <const field="opcode" value="0b1110011"/>
      <const field="funct3" value="0b000"/>
      <const field="imm" value="0b000000000000"/>
      <const field="rs1" value="0b00000"/>
      <const field="rd" value="0b00000"/>
    </encoding>
    <syntax>ecall</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      halt();
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

## The build

`mk/myrv.mk` tells the build where the ISA package is:

```make
ISA := build/isa/myrv
HAND := isa/myrv
CORPUS :=
CORPUS_CHECK :=
CORPUS_NO_ALIASES :=
ASM_CHECK :=
CORPUS_FILES :=
CORPUS_ALL :=
SIM_TESTS :=
STATE_TESTS :=

MYRV_XML := $(wildcard $(HAND)/*.xml) $(wildcard $(HAND)/instructions/*.xml)

$(ISA)/arch.xml: $(FEATURES_STAMP) $(MYRV_XML)
	rm -rf $(ISA)
	mkdir -p $(ISA)/instructions
	cp $(HAND)/*.xml $(ISA)/
	cp $(HAND)/instructions/*.xml $(ISA)/instructions/
	$(WRITE_FEATURES)
```

## Check

```sh
make ARCH=myrv check
```

The lines about this ISA package:

```text
schema: all files valid
0 Sail bodies outside the subset
2 forms, 0 structural errors
0 pairs of decodable forms not told apart
0 ambiguous assembly texts
```

The XML follows the schema; the semantics stay within the Sail subset the Rust model translates; fields fit the word and do not overlap; no two forms match the same word; no assembly text encodes to two different words.

## Run

Write a program, `work/hello.s`:

```text
addi x1, x0, 5
addi x2, x1, -3
addi x3, x2, 2047
ecall
```

Assemble it, build both simulators and run:

```sh
make ARCH=myrv sim rsim
python3 tools/asm.py build/isa/myrv work/hello.s work/hello.hex
build/myrv/xinyu-sim work/hello.hex
build/rsim/myrv/release/rsim run work/hello.hex --arch myrv
```

The first line of `work/hello.hex`, `00500093`, is RISC-V's `addi x1, x0, 5`. The Sail and the Rust model print the same:

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

Four instructions ran, the model stopped at 0x10, and only the registers that are not zero are listed.

## Next

- [Writing an ISA package](./package): layouts, aliases, extensions, the SIMT execution model;
- [Verification](./verification): directed tests, differential testing, proofs, external references;
- [RV64I from scratch](../examples/rv64/): ten steps to 13 instructions, verified down to the byte against Spike.
