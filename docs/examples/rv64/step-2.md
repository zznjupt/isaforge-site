# Step 2: Running a program

> **Goal**: add an instruction that stops the model, write a four-line program, run it on both simulators and read the output.

First, a look at how the files and commands fit together. This step uses the first two lanes; the third is for step 4:

<div class="forge-figure">

![How the files and commands fit together](/tutorial/build-flow-en.svg){.light-only}
![How the files and commands fit together](/tutorial/build-flow-en-dark.svg){.dark-only}

</div>

## ① Add an instruction that stops the model: ECALL

The model needs to know when to stop. The scalar model provides `halt()`, and you decide which instruction calls it; here it is ECALL.

In `isa/myrv/layouts.xml`, add a layout before `</layouts>`:

```xml
  <!-- SYSTEM: instructions such as ECALL, with no operands and every bit fixed -->
  <layout name="SYSTEM">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
```

Create `isa/myrv/instructions/ECALL.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ECALL">
  <summary>Environment call</summary>
  <description>Requests a service from the execution environment; the tutorial's model stops here.</description>
  <form id="ecall" layout="SYSTEM">
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

`<operands/>` is empty: every bit is a constant.

## ② Write a program

Write a program, `work/hello.s`:

```text
addi x1, x0, 5
addi x2, x1, -3
addi x3, x2, 2047
ecall
```

## ③ Build, assemble, run

Build both simulators, assemble and run:

```sh
make ARCH=myrv sim rsim
python3 tools/asm.py build/isa/myrv work/hello.s work/hello.hex
build/myrv/xinyu-sim work/hello.hex
build/rsim/myrv/release/rsim run work/hello.hex --arch myrv
```

`work/hello.hex` holds one instruction word per line; the first, `00500093`, is RISC-V's `addi x1, x0, 5`. With `make ARCH=myrv watch` running, you can also paste these lines into the assembler page and see the words directly. Both simulators print the same:

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

## ④ Read the output

| Line | Meaning |
|---|---|
| `steps 4` | How many instructions ran |
| `PC 0x…10` | The PC where the model stopped |
| `reg x1 0x…05` | A register's value; only registers that are not zero are listed |

**Exit codes**

| Exit code | Meaning |
|---|---|
| 0 | Stopped normally |
| 1 | An illegal instruction, a fault, or the step limit reached (1,000,000 steps by default; change it with `--max-steps N`) |
| 2 | A usage error |

**The two simulators**

- Both are generated from the same XML: the Sail one is the reference, the Rust one is for speed;
- rsim also prints a line of statistics on standard error (`rsim: 4 warp instructions in …`).

::: warning Warning
- **After changing the XML, run `make ARCH=myrv sim rsim` first**, then assemble and run. `tools/asm.py` reads the build copy `build/isa/myrv`, and the simulators are compiled binaries; without a new make they are the old versions.
- The assembler takes one instruction per line and **supports neither comments nor labels**.
:::
