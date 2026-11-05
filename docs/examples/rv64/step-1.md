# Step 1: The skeleton and a first instruction

> **Goal**: the smallest ISA package that passes the check: four XML files, one instruction and a build configuration.

## ① Write `arch.xml`: instruction length and execution model

Create `isa/myrv/arch.xml`:

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

- `length="32"`: instruction words are 32 bits long;
- `<execution/>`: the scalar execution model, one instruction at a time. SIMT architectures such as GPUs give the number of lanes and the predicates here; see [Writing an ISA package](../../guide/package#execution-model);
- `<immediates>`: the immediate types the ISA package uses. Two are declared here: `uimm` unsigned and `simm` signed, both decimal in assembly and disassembly. An operand's `type` names one of them, and its width is given on the operand (`width`). Other ISAs can declare immediates printed in hex, or floating-point ones; see [Writing an ISA package](../../guide/package#fields-and-operands).

## ② Write `registers.xml`: registers and memory

Create `isa/myrv/registers.xml`:

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

- **`X`**: 32 registers of 64 bits, named `x0` to `x31` in assembly. The name `X` is used in three places later:
  - the operand type: `type="X"`;
  - the access functions: `read_X`, `write_X`;
  - the assembly names: `{n}` in `asm="x{n}"` is replaced by the number.
- **`<reg index="0" … />`**: x0 always reads 0 and writes to it are discarded, so semantics need no special case for it.
- **`M`**: a little-endian memory. `fetch="true"` means the program is loaded at address 0 of this memory and fetched from it.

## ③ Write `layouts.xml`: encoding layouts

Create `isa/myrv/layouts.xml`, with only the I type for now:

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
</layouts>
```

## ④ Write the first instruction, ADDI

Create `isa/myrv/instructions/ADDI.xml`:

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

The figure maps the parts of this file to the instruction word:

<div class="forge-figure">

![The parts of an instruction, using ADDI](/tutorial/anatomy-en.svg){.light-only}
![The parts of an instruction, using ADDI](/tutorial/anatomy-en-dark.svg){.dark-only}

</div>

| Part | What it does |
|---|---|
| `<form id="addi" layout="I">` | One encoding. The `id` is unique in the ISA package, and the fields come from the I-type layout |
| `<operands>` | An operand with the same name as a layout field takes that field. `type="X"` is a register number; `simm` is a signed immediate, and `width` its width in bits |
| `<encoding>` | The fixed bits, here opcode and funct3 |
| `<syntax>` | The assembly template; `{name}` places an operand. Both the assembler and the disassembler are made from it |
| `<description>` | Goes into the manual. `<op>name</op>` refers to an operand, so after a rename the check finds references that no longer resolve |
| `<execute>` | The semantics, in Sail. `d.name` is the value of an operand; returning `RETIRE_OK` means the instruction completed normally and the PC moves to the next one |

::: tip Tip
Semantics can use only a subset of Sail: the part the Rust simulator can translate. The most common pieces are the ones here: `read_X`/`write_X`, `+` and `sail_sign_extend`. For more, see [Writing an ISA package](../../guide/package#semantics).
:::

## ⑤ Write the build configuration, `mk/myrv.mk`

It tells the build that the ISA package is in `isa/myrv` and is copied to `build/isa/myrv` before building.

Create `mk/myrv.mk`:

```make
# myrv: the RV64I subset written from scratch in the tutorial. Select it with make ARCH=myrv ...

ISA := build/isa/myrv
HAND := isa/myrv
# No reference corpus yet.
CORPUS :=
CORPUS_CHECK :=
CORPUS_NO_ALIASES :=
ASM_CHECK :=
CORPUS_FILES :=
CORPUS_ALL :=
# No directed tests yet.
SIM_TESTS :=
STATE_TESTS :=

MYRV_XML := $(wildcard $(HAND)/*.xml) $(wildcard $(HAND)/instructions/*.xml)

# No importer: copy the hand-written ISA package into the build directory as it is.
$(ISA)/arch.xml: $(FEATURES_STAMP) $(MYRV_XML)
	rm -rf $(ISA)
	mkdir -p $(ISA)/instructions
	cp $(HAND)/*.xml $(ISA)/
	cp $(HAND)/instructions/*.xml $(ISA)/instructions/
	$(WRITE_FEATURES)
```

::: warning Warning
Recipe lines must start with a tab, not spaces.
:::

## ⑥ Run the check

```sh
make ARCH=myrv check
```

The output is long, and part of it is ISAForge's own tests. The lines about your ISA package are these:

```text
schema: all files valid
0 Sail bodies outside the subset
1 forms, 0 structural errors
0 pairs of decodable forms not told apart
0 ambiguous assembly texts
pass 4545 generated words decode (ISA myrv, seed 1); dropped forms: none
```

| Output | What was checked |
|---|---|
| `schema: all files valid` | The XML follows the schema |
| `0 Sail bodies outside the subset` | The semantics stay within the Sail subset, with matching types and widths |
| `1 forms, 0 structural errors` | Fields fit the word and do not overlap, and everything they name exists |
| `0 pairs of decodable forms not told apart` | No two forms match the same word, so decoding is unique |
| `0 ambiguous assembly texts` | No assembly text encodes to two different words |
| `pass … generated words decode` | Words generated at random from each form decode back to it |

::: warning Important
- If the command ends with `make: *** … Error 1`, something is wrong. Look further up for the line with a file name and line number, and fix it using [Common errors](./reference#common-errors).
- `instructions/` must hold at least one file; otherwise the copy fails with `cp: isa/myrv/instructions/*.xml: No such file or directory`.
:::

## ⑦ Check as you edit (recommended)

From here on, you can keep this running in another terminal:

```sh
make ARCH=myrv watch
```

```text
preview: http://127.0.0.1:8000/   assembler: http://127.0.0.1:8000/__asm/
watching isa/myrv (Ctrl-C to stop)
[10:20:31] check passed, documentation updated (1.1 s)
```

Every time you save a file in `isa/myrv/`, it:

- copies the ISA package again and checks it. It runs only the ISA package's own checks, so it is faster than `make check`;
- when the check passes, regenerates the manual, and the preview open in the browser reloads;
- when it fails, shows the errors in the terminal and at the top of the preview, with paths to the source files you edit in `isa/myrv/…`; the manual stays at the last version that passed.

The assembler's checks (the assembly round trip, and whether any text assembles to two words) run after the manual is updated, in the background, and only over the instructions you changed. For a small ISA package like myrv they finish at once and print nothing more; for an ISA package of a thousand instructions the terminal prints the time of each stage, a blue bar at the top of the preview shows which one is running, and it turns red when a problem is found.

The assembler page, linked at the top of the preview, is there to try things: write one instruction per line and see its word and the bits of each field at once; switch to "machine code → assembly" and paste words to see the form they decode to and their assembly text. When you do not remember how to write something:

- the instruction lookup on the right searches by mnemonic or description, and each instruction lists its syntax, what each operand can take, and an example that "insert" puts in;
- for the line you are writing, its syntax and operand ranges are shown below the editor;
- a wrong line gets the right syntax for its instruction (or instructions spelled close to it), and "replace" swaps it in.

Every form in the manual also has a "try it" link, which opens this page with its example filled in. The page never changes your ISA package.

::: tip Tip
`make ARCH=myrv watch WATCH_ARGS=--once` runs once and exits; `WATCH_ARGS=--no-serve` starts no preview; `WATCH_ARGS="--port 9000"` changes the port.
:::
