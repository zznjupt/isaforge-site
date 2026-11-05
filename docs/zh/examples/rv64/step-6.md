# 第 6 步：扩展与特性开关

> **目标**：把乘法做成可选扩展 M，体验"按扩展组合构建"。

## ① 声明扩展

在 `isa/myrv/arch.xml` 的 `<execution/>` 后面加：

```xml
  <features>
    <feature name="I">
      <description>基础整数指令。</description>
    </feature>
    <feature name="M" requires="I">
      <description>整数乘法。</description>
    </feature>
  </features>
```

## ② 加一条属于扩展的指令

新建 `isa/myrv/instructions/MUL.xml`，在 `<instruction>` 上标 `feature="M"`：

```xml
<instruction xmlns="urn:xinyu:isa:1" mnemonic="MUL" feature="M">
```

- 语义是 `write_X(d.rd, read_X(d.rs1) * read_X(d.rs2))`，完整文件见下；
- 没有标 `feature` 的元素始终存在，所以前面的指令不用改。

::: details isa/myrv/instructions/MUL.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="MUL" feature="M">
  <summary>寄存器乘</summary>
  <description>把 <op>rs1</op> 与 <op>rs2</op> 相乘，结果的低 64 位写入 <op>rd</op>。</description>
  <form id="mul" layout="R">
    <operands>
      <operand name="rd" type="X"/>
      <operand name="rs1" type="X"/>
      <operand name="rs2" type="X"/>
    </operands>
    <encoding>
      <const field="opcode" value="0b0110011"/>
      <const field="funct3" value="0b000"/>
      <const field="funct7" value="0b0000001"/>
    </encoding>
    <syntax>mul {rd}, {rs1}, {rs2}</syntax>
  </form>
  <operation>
    <execute><![CDATA[
      write_X(d.rd, read_X(d.rs1) * read_X(d.rs2));
      RETIRE_OK
    ]]></execute>
  </operation>
</instruction>
```

:::

## ③ 按扩展组合构建

构建时用 `FEATURES` 选择启用哪些扩展，不写就是全部启用。写一个程序 `work/mul.s`：

```text
addi x1, x0, 6
addi x2, x0, 7
mul x3, x1, x2
ecall
```

```sh
make ARCH=myrv sim
python3 tools/asm.py build/isa/myrv work/mul.s work/mul.hex
build/myrv/xinyu-sim work/mul.hex            # x3 = 0x2A
make ARCH=myrv FEATURES="I" sim
build/myrv/xinyu-sim work/mul.hex            # 只启用 I：MUL 不存在
```

只启用 I 时，MUL 的指令字就是非法指令，模拟器停下并以退出码 1 结束：

```text
illegal instruction at pc 0x0000000000000008
  word 0x022081B3
steps 3
PC 0x0000000000000008
reg x1 0x0000000000000006
reg x2 0x0000000000000007
```

- **被禁用就等于不存在**：译码器、汇编器、反汇编器和文档都看不到它；
- 做完后用 `make ARCH=myrv sim rsim` 恢复全部启用。
