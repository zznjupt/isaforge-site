# Writing an ISA package

An ISA package lives under `isa/<name>/` and is made of a few kinds of XML file. `make check` checks it; editors read the same schema (`schema/isa.xsd`), so completion and documentation come while you write.

## Forms and operations

One file per mnemonic, holding two kinds of thing:

- **forms**: encodings. One mnemonic can have a register form, an immediate form, a uniform-register form and so on, each with its own bit fields, operands and syntax, and an `id` unique in the ISA package;
- **operations**: semantics in Sail, which several forms can share. A form names its operation with `operation="name"` and, where needed, a pure `<decode>` turns its fields into the operation's inputs.

B300 SASS's LOP3 has three forms sharing one operation; their second source comes from a register, a uniform register and an immediate:

```xml
<form id="lop3_lut__RRR_RRR" operation="lop3_lut">
  <decode><![CDATA[d.Rd = f.Rd; d.Ra = f.Ra; d.b = SrcR(f.Rb); d.Rc = f.Rc; ...]]></decode>
</form>
<form id="lop3_lut__RUR_RUR" operation="lop3_lut">
  <decode><![CDATA[d.Rd = f.Rd; d.Ra = f.Ra; d.b = SrcU(f.URb); d.Rc = f.Rc; ...]]></decode>
</form>
```

## Fields and operands

A form writes its bit fields itself or takes a layout from `layouts.xml`. An operand named like a layout field takes that field, and `<const>` fixes the others. An operand's `type` is:

| type | The field holds | Written in assembly as |
|---|---|---|
| a register file, such as `X` | a register number | the register's name, such as `x5` |
| an immediate type declared in `arch.xml`, such as `simm` | an immediate, sign-extended from `width`, possibly with a `scale` | as declared: decimal, hex, float, bit set |
| an enum from `enums.xml` | an enum code | the value's name, such as `.EQ` |

Immediate types are declared by the ISA package; ISAForge knows no names of its own. An operand can also be PC-relative, or take its type from the value of another operand.

## Assembly syntax

`<syntax>` is a template both the assembler and the disassembler are made from:

::: v-pre
- `{name}` places an operand, `{.name}` a suffix that appears only at a value other than the default;
- `{{ … }}` is an optional part, left out when every operand in it takes its default;
- `[[ term | term ]]` are the terms in brackets, `<< slot | slot >>` comma-separated slots.
:::

In a SIMT ISA package every instruction can carry a predicate, not printed at its default:

```xml
<syntax>{{@{P} }}add {Rd}, {Ra}, {Rb}</syntax>
```

An **alias** replaces the mnemonic when its condition holds, and the assembler accepts it:

```xml
<alias mnemonic="li">
  <when>rs1 == `X@x0</when>
  <syntax>li {rd}, {imm}</syntax>
</alias>
```

## Extensions

`arch.xml` declares extensions and what they require; an instruction or a form names its extension with `feature`. `make FEATURES="I M"` builds only those, and the decoder, assembler, simulators and manual follow the enabled set.

```xml
<features>
  <feature name="I">
    <description>The base integer instruction set RV64I.</description>
  </feature>
  <feature name="Zmmul" requires="I">
    <description>The multiplication subset of M: MUL, MULH, MULHSU, MULHU, MULW.</description>
  </feature>
  <feature name="M" requires="Zmmul">
    <description>Integer multiplication and division.</description>
  </feature>
</features>
```

```xml
<instruction mnemonic="MUL" feature="Zmmul">
```

## Execution model

`<execution>` in `arch.xml` says how the model runs:

- `<execution/>`: scalar, one instruction at a time, stopped by an instruction that calls `halt()`;
- `lanes="32"`: SIMT, each instruction running on a warp's lanes, the semantics taking a lane mask `m`;
- `<guard operand="Pg"/>`: predicated execution, the mask being the active lanes and the predicate;
- `<launch/>`: launch identities, so the simulator can start every warp of a grid and its blocks;
- register files can declare rules for conflicting and early reads of pending writes, which with `wait` and hook functions describe pipelines with delayed writes.

## Semantics

`<execute>` is written in a subset of Sail, the part the Rust model translates: bit-vector arithmetic, `let`, `if`, `match`, `foreach` and calls to shared functions. Semantics reach state only through the generated interface. LOP3's:

```sail
foreach (l from 0 to 31) {
  if m[l] == bitone then {
    let b = read_Src(l, d.b);
    let v = lop3(read_R(l, d.Ra), b, read_R(l, d.Rc), d.imm8);
    let nz = v != sail_zeros(32);
    let p = read_P(l, d.Pp) != (d.Pp_not == 0b1);
    write_R(l, d.Rd, v);
    write_P(l, d.Pu, if d.pop == 0b0 then nz | p else nz & p)
  }
};
RETIRE_OK
```

`m` is this step's lane mask; `lop3` and `read_Src` are shared functions in `shared.xml`. A loop like this one, reading and writing only its own lane, becomes whole-warp operations with a masked write-back in the Rust model, which LLVM vectorises.

## What is checked

`make check` checks that:

- fields fit the word and do not overlap, and the layouts, enums and encoding tables they name exist;
- **no two decodable forms match the same word**: every pair has a field whose allowed values are disjoint. When two forms cannot be told apart, they are compared field by field with a suggested fix;
- no assembly text encodes to two different words;
- each form's syntax shows every one of its operands;
- semantics stay within the Sail subset, with matching types and widths;
- random words generated from each form decode back to it.

Errors come with their file and line.
