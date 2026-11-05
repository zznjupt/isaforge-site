# Step 7: Aliases

> **Goal**: have the assembler accept, and the disassembler print, the common shorthands `li`, `mv` and `nop`.

## ① Give ADDI its aliases

`li`, `mv` and `nop` are all really ADDI. In `ADDI.xml`, after `<syntax>`, add:

```xml
    <alias mnemonic="nop">
      <when>rd == `X@x0 &amp;&amp; rs1 == `X@x0 &amp;&amp; imm == 0</when>
      <syntax>nop</syntax>
    </alias>
    <alias mnemonic="li">
      <when>rs1 == `X@x0</when>
      <syntax>li {rd}, {imm}</syntax>
    </alias>
    <alias mnemonic="mv">
      <when>imm == 0</when>
      <syntax>mv {rd}, {rs1}</syntax>
    </alias>
```

- `<when>`: the condition under which the alias holds. `` `X@x0 `` is the register named x0 in register file X;
- In XML, `&&` is written `&amp;&amp;`;
- The disassembler takes the first alias that holds, in the order written, so the most specific, `nop`, goes first;
- `make ARCH=myrv check` makes sure no alias gives one assembly text two encodings.

## ② Assemble and disassemble

`work/alias.s` has five lines: `li x1, 10`, `mv x7, x1`, `nop`, `addi x2, x1, 1`, `ecall`. The assembler accepts both the aliases and the plain forms. Assemble, then disassemble:

```sh
make ARCH=myrv isa
python3 tools/asm.py build/isa/myrv work/alias.s work/alias.hex
python3 tools/disasm.py build/isa/myrv work/alias.hex
```

The disassembly is:

```text
       0:  00a00093  li x1, 10
       4:  00008393  mv x7, x1
       8:  00000013  nop
       c:  00108113  addi x2, x1, 1
      10:  00000073  ecall
```

With `--no-aliases`, it prints the plain `addi` form instead.
