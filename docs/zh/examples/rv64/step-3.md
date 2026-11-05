# 第 3 步：补齐常用指令

> **目标**：再加 9 条指令，写一个带循环和访存的程序。

## ① 新指令带来的新写法

| 指令 | 布局 | 新写法 |
|---|---|---|
| ADD、SUB | R | 用 opcode、funct3、funct7 三个常量区分同一布局下的指令 |
| SLLI | SHIFTI | `uimm` 无符号立即数；`sail_shiftleft(值, unsigned(d.shamt))` |
| LUI | U | 位拼接：`d.imm @ sail_zeros(12)` |
| BEQ、BNE | B | 立即数由四段位拼成；`scale="2"`；改写 `NEXT_PC` 实现跳转 |
| JAL | J | 跳转，同时把返回地址 `PC + 4` 写入 `rd` |
| LD | I | 读内存：`read_M(地址, 8)` |
| SD | S | 写内存：`write_M(地址, 8, 值)` |

## ② 写出这些文件

这些文件的结构都和 ADDI 一样，下面给出完整内容，点开后逐个新建即可。先把 `isa/myrv/layouts.xml` 换成含全部布局的版本：

::: details isa/myrv/layouts.xml（R、I、S、B、U、J、SHIFTI 和 SYSTEM 型）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layouts xmlns="urn:xinyu:isa:1">
  <!-- I 型：12 位立即数、源寄存器、目的寄存器 -->
  <layout name="I">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
  <!-- SYSTEM：ECALL 这类没有操作数、全部位都固定的指令 -->
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

再在 `isa/myrv/instructions/` 下新建九个指令文件：

::: details isa/myrv/instructions/ADD.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ADD">
  <summary>寄存器加</summary>
  <description>把 <op>rs1</op> 与 <op>rs2</op> 相加，结果写入 <op>rd</op>。</description>
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
  <summary>寄存器减</summary>
  <description>把 <op>rs2</op> 从 <op>rs1</op> 中减去，结果写入 <op>rd</op>。</description>
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
  <summary>立即数逻辑左移</summary>
  <description>把 <op>rs1</op> 左移 <op>shamt</op> 位，结果写入 <op>rd</op>。</description>
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
  <summary>载入高位立即数</summary>
  <description>把 <op>imm</op> 放到第 31:12 位、低 12 位清零，结果写入 <op>rd</op>。</description>
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
  <summary>相等跳转</summary>
  <description><op>rs1</op> 等于 <op>rs2</op> 时，把 <op>imm</op> 加到 PC。</description>
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
  <summary>不等跳转</summary>
  <description><op>rs1</op> 不等于 <op>rs2</op> 时，把 <op>imm</op> 加到 PC。</description>
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
  <summary>跳转并链接</summary>
  <description>把 PC 加 4 写入 <op>rd</op>，然后跳转到 PC 加 <op>imm</op>。</description>
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
  <summary>载入双字</summary>
  <description>从 <op>rs1</op> 加 <op>imm</op> 的地址载入八个字节，写入 <op>rd</op>。</description>
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
  <summary>存储双字</summary>
  <description>把 <op>rs2</op> 写到 <op>rs1</op> 加 <op>imm</op> 的地址。</description>
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

## ③ 细看分支：模型怎样执行一步

分支涉及两个新概念：模型每一步的执行顺序，以及分散在指令字各处的立即数。

<div class="forge-figure">

![模型怎样执行一步，分支的立即数怎样拼出来](/tutorial/step-cycle-zh.svg){.light-only}
![模型怎样执行一步，分支的立即数怎样拼出来](/tutorial/step-cycle-zh-dark.svg){.dark-only}

</div>

B 型布局把立即数写成四段：

```xml
  <layout name="B">
    <field name="imm"><range msb="31" lsb="31"/><range msb="7" lsb="7"/><range msb="30" lsb="25"/><range msb="11" lsb="8"/></field>
    …
  </layout>
```

BEQ 的写法：

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

- **多段字段**：一个字段写成多个 `<range>` 时，按书写顺序从高位往低位拼接，这里得到 12 位的字段值。
- **`scale="2"`**：字段值乘以 2 才是操作数的值。`d.imm` 已经是 13 位的字节偏移，汇编语法里写的也是字节偏移。
- **`NEXT_PC`**：执行前 ISAForge 先把它设成 `PC + 4`，分支只在跳转时改写它；返回 `RETIRE_OK` 后，`PC = NEXT_PC`。
- **`return RETIRE_ILLEGAL`**：RV64I 要求跳转目标 4 字节对齐，不对齐时模型报非法指令并停下。

## ④ 运行一个循环求和程序

运行一个循环求和程序 `work/sum.s`，算 1 + 2 + … + 10，把结果写进内存再读回来：

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

汇编器没有标签，分支偏移要自己算：`bne` 在地址 0x10，循环体 `add` 在 0x08，所以偏移是 -8。

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

- `x2` 是 0x37，也就是 55；
- `mem M 0x…1000 0x37`：内存 M 从地址 0x1000 起被改写的字节；
- dump 只列出与程序映像不同的字节，`sd` 写进的高位 0 字节没有变化，所以不列出。

## ⑤ 看反汇编

反汇编器和汇编器一样由 `<syntax>` 生成，逐条打印地址、指令字和汇编文本：

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

不匹配任何 form 的字打印成 `(no form matches this word)`。「汇编/反汇编」页的“机器码 → 汇编”做的是同一件事，还会把每个字段的位拆开显示。
