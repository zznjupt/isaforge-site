# Step 3: The common instructions

> **Goal**: nine more instructions, and a program with a loop, a load and a store.

## ① What the new instructions bring

| Instruction | Layout | What is new |
|---|---|---|
| ADD, SUB | R | Three constants, opcode, funct3 and funct7, tell apart instructions of one layout |
| SLLI | SHIFTI | The unsigned immediate `uimm`; `sail_shiftleft(value, unsigned(d.shamt))` |
| LUI | U | Bit concatenation: `d.imm @ sail_zeros(12)` |
| BEQ, BNE | B | An immediate made of four pieces; `scale="2"`; a jump made by writing `NEXT_PC` |
| JAL | J | A jump that also writes the return address `PC + 4` to `rd` |
| LD | I | A memory read: `read_M(address, 8)` |
| SD | S | A memory write: `write_M(address, 8, value)` |

## ② Write the files

Every one of these files has the same structure as ADDI. Their full contents are below; open each and create it. First replace `isa/myrv/layouts.xml` with the version that has every layout:

::: details isa/myrv/layouts.xml (the R, I, S, B, U, J, SHIFTI and SYSTEM types)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layouts xmlns="urn:xinyu:isa:1">
  <!-- I type: 12-bit immediate, source register, destination register -->
  <layout name="I">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <!-- SYSTEM: instructions such as ECALL, with no operands and every bit fixed -->
  <layout name="SYSTEM">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="R">
    <field name="funct7"><range msb="31" lsb="25"/></field>
    <field name="rs2"><range msb="24" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="S">
    <field name="imm"><range msb="31" lsb="25"/><range msb="11" lsb="7"/></field>
    <field name="rs2"><range msb="24" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="B">
    <field name="imm"><range msb="31" lsb="31"/><range msb="7" lsb="7"/><range msb="30" lsb="25"/><range msb="11" lsb="8"/></field>
    <field name="rs2"><range msb="24" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="U">
    <field name="imm"><range msb="31" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="J">
    <field name="imm"><range msb="31" lsb="31"/><range msb="19" lsb="12"/><range msb="20" lsb="20"/><range msb="30" lsb="21"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <layout name="SHIFTI">
    <field name="funct6"><range msb="31" lsb="26"/></field>
    <field name="shamt"><range msb="25" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
</layouts>
```

:::

Then create the nine instruction files in `isa/myrv/instructions/`:

::: details isa/myrv/instructions/ADD.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ADD">
  <summary>Add</summary>
  <description>Adds <op>rs1</op> and <op>rs2</op> and writes <op>rd</op>.</description>
  <form id="add" layout="R" operation="add">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110011"/>
      <const field="funct3" value="0b000"/>
      <const field="funct7" value="0b0000000"/>
    </encoding>
    <syntax>add {rd}, {rs1}, {rs2}</syntax>
  </form>
  <operation name="add">
    <execute><![CDATA[
      write_X(d.rd, read_X(d.rs1) + read_X(d.rs2));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/SUB.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="SUB">
  <summary>Subtract</summary>
  <description>Subtracts <op>rs2</op> from <op>rs1</op> and writes <op>rd</op>.</description>
  <form id="sub" layout="R">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110011"/>
      <const field="funct3" value="0b000"/>
      <const field="funct7" value="0b0100000"/>
    </encoding>
    <syntax>sub {rd}, {rs1}, {rs2}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, sub_bits(read_X(d.rs1), read_X(d.rs2)));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/SLLI.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="SLLI">
  <summary>Shift left logical immediate</summary>
  <description>Shifts <op>rs1</op> left by <op>shamt</op> bits and writes <op>rd</op>.</description>
  <form id="slli" layout="SHIFTI">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="shamt" type="uimm" width="6"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0010011"/>
      <const field="funct3" value="0b001"/>
      <const field="funct6" value="0b000000"/>
    </encoding>
    <syntax>slli {rd}, {rs1}, {shamt}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, sail_shiftleft(read_X(d.rs1), unsigned(d.shamt)));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/LUI.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="LUI">
  <summary>Load upper immediate</summary>
  <description>Places <op>imm</op> in bits 31:12, clears the low 12 bits and writes <op>rd</op>.</description>
  <form id="lui" layout="U">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="imm" type="uimm" width="20"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110111"/>
    </encoding>
    <syntax>lui {rd}, {imm}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, sail_sign_extend(d.imm @ sail_zeros(12), 64));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/BEQ.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="BEQ">
  <summary>Branch if equal</summary>
  <description>Adds <op>imm</op> to the PC when <op>rs1</op> equals <op>rs2</op>.</description>
  <form id="beq" layout="B">
    <operands>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
      <operand name="imm" type="simm" width="13" scale="2"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b1100011"/>
      <const field="funct3" value="0b000"/>
    </encoding>
    <syntax>beq {rs1}, {rs2}, {imm}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      let taken : bool = read_X(d.rs1) == read_X(d.rs2);
      let target : bits(64) = PC + sail_sign_extend(d.imm, 64);
      if taken & target[1] == bitone then return RETIRE_ILLEGAL;
      if taken then NEXT_PC = target;
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/BNE.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="BNE">
  <summary>Branch if not equal</summary>
  <description>Adds <op>imm</op> to the PC when <op>rs1</op> does not equal <op>rs2</op>.</description>
  <form id="bne" layout="B">
    <operands>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
      <operand name="imm" type="simm" width="13" scale="2"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b1100011"/>
      <const field="funct3" value="0b001"/>
    </encoding>
    <syntax>bne {rs1}, {rs2}, {imm}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      let taken : bool = read_X(d.rs1) != read_X(d.rs2);
      let target : bits(64) = PC + sail_sign_extend(d.imm, 64);
      if taken & target[1] == bitone then return RETIRE_ILLEGAL;
      if taken then NEXT_PC = target;
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/JAL.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="JAL">
  <summary>Jump and link</summary>
  <description>Writes the PC plus 4 to <op>rd</op>, then jumps to the PC plus <op>imm</op>.</description>
  <form id="jal" layout="J">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="imm" type="simm" width="21" scale="2"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b1101111"/>
    </encoding>
    <syntax>jal {rd}, {imm}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      let target : bits(64) = PC + sail_sign_extend(d.imm, 64);
      if target[1] == bitone then return RETIRE_ILLEGAL;
      write_X(d.rd, PC + 4);
      NEXT_PC = target;
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/LD.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="LD">
  <summary>Load doubleword</summary>
  <description>Loads eight bytes from the address <op>rs1</op> plus <op>imm</op> and writes <op>rd</op>.</description>
  <form id="ld" layout="I">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="imm" type="simm" width="12"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0000011"/>
      <const field="funct3" value="0b011"/>
    </encoding>
    <syntax>ld {rd}, {imm}({rs1})</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, read_M(read_X(d.rs1) + sail_sign_extend(d.imm, 64), 8));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

::: details isa/myrv/instructions/SD.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="SD">
  <summary>Store doubleword</summary>
  <description>Writes <op>rs2</op> to the address <op>rs1</op> plus <op>imm</op>.</description>
  <form id="sd" layout="S">
    <operands>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
      <operand name="imm" type="simm" width="12"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0100011"/>
      <const field="funct3" value="0b011"/>
    </encoding>
    <syntax>sd {rs2}, {imm}({rs1})</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_M(read_X(d.rs1) + sail_sign_extend(d.imm, 64), 8, read_X(d.rs2));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

## ③ A closer look at branches: how the model runs a step

Branches bring two new ideas: the order in which the model runs each step, and an immediate spread across the instruction word.

<div class="forge-figure">

![How the model runs a step, and how a branch's immediate is put together](/tutorial/step-cycle-en.svg){.light-only}
![How the model runs a step, and how a branch's immediate is put together](/tutorial/step-cycle-en-dark.svg){.dark-only}

</div>

The B-type layout writes the immediate in four pieces:

```xml
  <layout name="B">
    <field name="imm"><range msb="31" lsb="31"/><range msb="7" lsb="7"/><range msb="30" lsb="25"/><range msb="11" lsb="8"/></field>
    …
  </layout>
```

BEQ is written as:

```xml
  <form id="beq" layout="B">
    <operands>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
      <operand name="imm" type="simm" width="13" scale="2"/>
    </operands>
    …
  </form>
  <operation>
    <execute><![CDATA[
      let taken : bool = read_X(d.rs1) == read_X(d.rs2);
      let target : bits(64) = PC + sail_sign_extend(d.imm, 64);
      if taken & target[1] == bitone then return RETIRE_ILLEGAL;
      if taken then NEXT_PC = target;
      RETIRE_OK
    ]]></execute>
  </operation>
```

- **A field in several pieces**: when a field is written as several `<range>`s, they are concatenated in the order written, from the high bits down; here that gives a 12-bit field value.
- **`scale="2"`**: the operand's value is the field value times 2. `d.imm` is already a 13-bit byte offset, and the assembly syntax also takes a byte offset.
- **`NEXT_PC`**: before the instruction runs, ISAForge sets it to `PC + 4`; a branch writes it only when it is taken. After `RETIRE_OK` is returned, `PC = NEXT_PC`.
- **`return RETIRE_ILLEGAL`**: RV64I requires jump targets to be 4-byte aligned; when one is not, the model reports an illegal instruction and stops.

## ④ Run a loop that sums

Run a program with a loop, `work/sum.s`, which computes 1 + 2 + … + 10, writes the result to memory and reads it back:

```text
addi x1, x0, 10
addi x2, x0, 0
add x2, x2, x1
addi x1, x1, -1
bne x1, x0, -8
lui x5, 1
sd x2, 0(x5)
ld x6, 0(x5)
ecall
```

The assembler has no labels, so you work out branch offsets yourself: `bne` is at 0x10 and the loop body, `add`, at 0x08, so the offset is -8.

```sh
make ARCH=myrv sim rsim
python3 tools/asm.py build/isa/myrv work/sum.s work/sum.hex
build/myrv/xinyu-sim work/sum.hex
```

```text
steps 36
PC 0x0000000000000024
reg x2 0x0000000000000037
reg x5 0x0000000000001000
reg x6 0x0000000000000037
mem M 0x0000000000001000 0x37
```

- `x2` is 0x37, that is 55;
- `mem M 0x…1000 0x37`: the bytes of memory M changed, starting at address 0x1000;
- the dump lists only bytes that differ from the program image. The high zero bytes `sd` wrote did not change anything, so they are not listed.

## ⑤ Look at the disassembly

The disassembler is made from `<syntax>`, like the assembler, and prints each word's address, the word and its assembly text:

```sh
python3 tools/disasm.py build/isa/myrv work/sum.hex
```

```text
       0:  00a00093  addi x1, x0, 10
       4:  00000113  addi x2, x0, 0
       8:  00110133  add x2, x2, x1
       c:  fff08093  addi x1, x1, -1
      10:  fe009ce3  bne x1, x0, -8
      14:  000012b7  lui x5, 1
      18:  0022b023  sd x2, 0(x5)
      1c:  0002b303  ld x6, 0(x5)
      20:  00000073  ecall
```

A word that matches no form is printed as `(no form matches this word)`. "Machine code → assembly" on the assembler page does the same, and also shows the bits of each field.
