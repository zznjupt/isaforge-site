# 第 8 步：自定义指令与等价性

> **目标**：加一条自己设计的融合指令，并证明它与被替换的指令序列等价。

设想你为热点代码设计了一条融合指令 SH1ADD：`rd = (rs1 << 1) + rs2`，用来替换 `slli` 加 `add` 两条指令。这条指令没有硬件或现成模拟器可以对照，但它有一个天然的参考：被它替换的那段指令序列。

<div class="forge-figure">

![等价性检查：新指令和它替换的序列](/tutorial/equivalence-zh.svg){.light-only}
![等价性检查：新指令和它替换的序列](/tutorial/equivalence-zh-dark.svg){.dark-only}

</div>

## ① 声明自定义扩展

先在 `arch.xml` 的 `<features>` 里给自定义指令开一个扩展（RISC-V 习惯用 X 开头命名自定义扩展）：

```xml
    <feature name="Xmy" requires="I">
      <description>本教程的自定义扩展：融合指令 SH1ADD。</description>
    </feature>
```

## ② 写指令和等价声明

新建 `isa/myrv/instructions/SH1ADD.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="SH1ADD" feature="Xmy">
  <summary>左移一位后加</summary>
  <description>把 <op>rs1</op> 左移 1 位再加 <op>rs2</op>，结果写入 <op>rd</op>；这是一条“自定义”融合指令，声明它与两条基础指令等价。</description>
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
      <description>等价于 slli tmp, rs1, 1; add rd, tmp, rs2，要求 tmp 与 rs1、rs2 都不同。</description>
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

| 元素 | 作用 |
|---|---|
| `<sequence>` | 基础指令序列。`<step>` 的属性给出每个操作数绑定到什么：新指令的操作数名、临时寄存器名，或者立即数 |
| `<temps>` | 序列用到的临时寄存器。它会被序列改写，所以比较结果时不算它 |
| `<preconditions>` | 让序列成立的前提。`tmp` 必须与 `rs1`、`rs2` 都不同，否则 `slli` 会先改掉 `add` 还要读的值；少写一条，形式化检查就会找到反例 |

## ③ 运行两种检查

运行两种检查：

```sh
make ARCH=myrv equiv equiv-prove
```

```text
SH1ADD: 20 cases agree (rsim batch and Sail funcsim)
SH1ADD: proved (0.75s, z3)
```

| 检查 | 做法 | 覆盖范围 |
|---|---|---|
| `equiv`（差分） | 随机抽满足前提的操作数和完整初始状态，分别运行新指令和序列，比较除临时寄存器外的全部状态；两个模拟器各跑一遍 | 20 个随机用例 |
| `equiv-prove`（证明） | 用 Sail 的 SMT 后端和 z3 求解 | 所有满足前提的操作数和状态 |

## ④ 声明写错时会看到什么

把 `shamt="1"` 写成 `shamt="2"`，两个检查都会失败。差分 `make ARCH=myrv equiv`：

```text
SH1ADD: case 0 differs, new instruction vs sequence: x30 0xAF6E1A3FC673A066 vs 0xBA6ECD2BA0D2B418
  state    build/equiv/myrv/differential/SH1ADD__sh1add/case-0000/state
  custom   build/myrv/xinyu-sim --state … --max-steps 1 …/custom.hex
  sequence build/myrv/xinyu-sim --state … --max-steps 2 …/sequence.hex
  …
```

- `new instruction vs sequence`：新指令与序列的结果不同，前一个值是新指令的；
- 直接运行 `custom` 和 `sequence` 两行，就能看到两边的完整状态。

证明 `make ARCH=myrv equiv-prove`：

```text
SH1ADD: NOT proved (counterexample, 0.61s); see build/equiv/myrv/proof/SH1ADD__sh1add/check.log
  counterexample:
    operands: rs2 = x4, rs1 = x2, rd = x6, temp tmp = x16
    initial X: x2 (rs1) = 0x000007FFFFFFFFFF, x4 (rs2) = 0x0000000000000008, x6 (rd) = 0x1100000800008000, x16 (tmp) = 0x0000000000000000, 18 other registers nonzero
    initial PC = 0x0
    initial HALTED = false
    every nonzero register: build/equiv/myrv/proof/SH1ADD__sh1add/counterexample.txt
```

- z3 给出一组让两边不同的操作数和初值：`rs1` 非零时，左移 1 位和左移 2 位的结果不同；
- 屏幕上只列出操作数指向的寄存器，其余非零寄存器（求解器随手填的值）在 `counterexample.txt` 里；
- 改回 `shamt="1"` 后两个检查重新通过。
