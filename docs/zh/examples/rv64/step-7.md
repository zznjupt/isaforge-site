# 第 7 步：别名

> **目标**：让汇编器接受、反汇编器打印 `li`、`mv`、`nop` 这些常用简写。

## ① 给 ADDI 加别名

`li`、`mv`、`nop` 其实都是 ADDI。在 `ADDI.xml` 的 `<syntax>` 后面加：

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

- `<when>`：别名的成立条件。`` `X@x0 `` 表示寄存器堆 X 里名为 x0 的寄存器；
- XML 里 `&&` 要写成 `&amp;&amp;`；
- 反汇编时按书写顺序取第一个成立的别名，所以把最具体的 `nop` 放在最前面；
- `make ARCH=myrv check` 会确认别名不会让同一段汇编文本有两种编码。

## ② 汇编并反汇编

`work/alias.s` 有五行：`li x1, 10`、`mv x7, x1`、`nop`、`addi x2, x1, 1`、`ecall`。汇编器同时接受别名和原始写法，汇编后再反汇编：

```sh
make ARCH=myrv isa
python3 tools/asm.py build/isa/myrv work/alias.s work/alias.hex
python3 tools/disasm.py build/isa/myrv work/alias.hex
```

反汇编得到：

```text
       0:  00a00093  li x1, 10
       4:  00008393  mv x7, x1
       8:  00000013  nop
       c:  00108113  addi x2, x1, 1
      10:  00000073  ecall
```

加上 `--no-aliases` 就打印原始的 `addi` 写法。
