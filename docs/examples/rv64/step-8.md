# Step 8: A custom instruction and its equivalence

> **Goal**: add a fused instruction of your own design and prove it equivalent to the sequence of instructions it replaces.

Suppose that for hot code you have designed a fused instruction, SH1ADD: `rd = (rs1 << 1) + rs2`, to replace the two instructions `slli` and `add`. There is no hardware or existing simulator to compare it with, but it has a natural reference: the sequence of instructions it replaces.

<div class="forge-figure">

![The equivalence check: a new instruction and the sequence it replaces](/tutorial/equivalence-en.svg){.light-only}
![The equivalence check: a new instruction and the sequence it replaces](/tutorial/equivalence-en-dark.svg){.dark-only}

</div>

## ① Declare a custom extension

First give the custom instruction an extension of its own in the `<features>` of `arch.xml` (RISC-V's custom extensions are by convention named with an X):

```xml
    <feature name="Xmy" requires="I">
      <description>This tutorial's custom extension: the fused instruction SH1ADD.</description>
    </feature>
```

## ② Write the instruction and its equivalence

Create `isa/myrv/instructions/SH1ADD.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="SH1ADD" feature="Xmy">
  <summary>Shift left by one and add</summary>
  <description>Shifts <op>rs1</op> left by 1 bit, adds <op>rs2</op> and writes the result to <op>rd</op>. This is a "custom" fused instruction, declared equivalent to two base instructions.</description>
  <form id="sh1add" layout="R" operation="sh1add">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110011"/>
      <const field="funct3" value="0b010"/>
      <const field="funct7" value="0b0010000"/>
    </encoding>
    <syntax>sh1add {rd}, {rs1}, {rs2}</syntax>
  </form>
  <operation name="sh1add">
    <execute><![CDATA[
      write_X(d.rd, sail_shiftleft(read_X(d.rs1), 1) + read_X(d.rs2));
      RETIRE_OK
    ]]></execute>
    <equivalence>
      <description>Equivalent to slli tmp, rs1, 1; add rd, tmp, rs2, provided tmp differs from both rs1 and rs2.</description>
      <sequence>
        <step form="slli" rd="tmp" rs1="rs1" shamt="1"/>
        <step form="add" rd="rd" rs1="tmp" rs2="rs2"/>
      </sequence>
      <temps>
        <temp name="tmp" file="X"/>
      </temps>
      <preconditions>
        <distinct a="tmp" b="rs1"/>
        <distinct a="tmp" b="rs2"/>
      </preconditions>
    </equivalence>
  </operation>
</instruction>
```

| Element | What it does |
|---|---|
| `<sequence>` | the sequence of base instructions. The attributes of each `<step>` say what each operand is bound to: an operand of the new instruction, a temporary, or an immediate |
| `<temps>` | the temporary registers the sequence uses. The sequence overwrites them, so they are left out when the results are compared |
| `<preconditions>` | what the sequence needs to hold. `tmp` must differ from both `rs1` and `rs2`, or `slli` would change a value `add` still has to read; leave one out and the formal check finds a counterexample |

## ③ Run both checks

Run both checks:

```sh
make ARCH=myrv equiv equiv-prove
```

```text
SH1ADD: 20 cases agree (rsim batch and Sail funcsim)
SH1ADD: proved (0.75s, z3)
```

| Check | How | What it covers |
|---|---|---|
| `equiv` (differential) | draws operands and whole initial states that meet the preconditions, runs the new instruction and the sequence, and compares all state but the temporaries; once on each simulator | 20 random cases |
| `equiv-prove` (proof) | solved with Sail's SMT back end and z3 | every operand and state that meets the preconditions |

## ④ What a wrong declaration looks like

Write `shamt="2"` instead of `shamt="1"` and both checks fail. The differential check, `make ARCH=myrv equiv`:

```text
SH1ADD: case 0 differs, new instruction vs sequence: x30 0xAF6E1A3FC673A066 vs 0xBA6ECD2BA0D2B418
  state    build/equiv/myrv/differential/SH1ADD__sh1add/case-0000/state
  custom   build/myrv/xinyu-sim --state … --max-steps 1 …/custom.hex
  sequence build/myrv/xinyu-sim --state … --max-steps 2 …/sequence.hex
  …
```

- `new instruction vs sequence`: the new instruction and the sequence give different results; the first value is the new instruction's;
- Run the `custom` and `sequence` lines yourself to see the whole state of each.

The proof, `make ARCH=myrv equiv-prove`:

```text
SH1ADD: NOT proved (counterexample, 0.61s); see build/equiv/myrv/proof/SH1ADD__sh1add/check.log
  counterexample:
    operands: rs2 = x4, rs1 = x2, rd = x6, temp tmp = x16
    initial X: x2 (rs1) = 0x000007FFFFFFFFFF, x4 (rs2) = 0x0000000000000008, x6 (rd) = 0x1100000800008000, x16 (tmp) = 0x0000000000000000, 18 other registers nonzero
    initial PC = 0x0
    initial HALTED = false
    every nonzero register: build/equiv/myrv/proof/SH1ADD__sh1add/counterexample.txt
```

- z3 gives operands and initial values that make the two differ: when `rs1` is nonzero, shifting left by 1 and by 2 give different results;
- Only the registers the operands name are listed on screen; the other nonzero registers (values the solver filled in arbitrarily) are in `counterexample.txt`;
- Change it back to `shamt="1"` and both checks pass again.
