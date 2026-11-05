# 第 2 步：让程序跑起来

> **目标**：加一条停机指令，写一个 4 行的程序，在两个模拟器上运行并读懂输出。

先看一眼文件和命令是怎么串起来的。这一步用到前两条泳道，第三条留给第 4 步：

<div class="forge-figure">

![文件和命令怎么串起来](/tutorial/build-flow-zh.svg){.light-only}
![文件和命令怎么串起来](/tutorial/build-flow-zh-dark.svg){.dark-only}

</div>

## ① 加一条停机指令 ECALL

模型要知道什么时候停。标量模型提供 `halt()`，由你决定哪条指令调用它，这里选 ECALL。

在 `isa/myrv/layouts.xml` 的 `</layouts>` 前加一个布局：

```xml
  <!-- SYSTEM：ECALL 这类没有操作数、全部位都固定的指令 -->
  <layout name="SYSTEM">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
```

新建 `isa/myrv/instructions/ECALL.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ECALL">
  <summary>环境调用</summary>
  <description>向执行环境请求服务；本教程的模型在这里停机。</description>
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

`<operands/>` 是空的：所有位都是常量。

## ② 写一个程序

写一个程序 `work/hello.s`：

```text
addi x1, x0, 5
addi x2, x1, -3
addi x3, x2, 2047
ecall
```

## ③ 编译、汇编、运行

汇编、编译两个模拟器、运行：

```sh
make ARCH=myrv sim rsim
python3 tools/asm.py build/isa/myrv work/hello.s work/hello.hex
build/myrv/xinyu-sim work/hello.hex
build/rsim/myrv/release/rsim run work/hello.hex --arch myrv
```

`work/hello.hex` 每行一个指令字，第一行 `00500093` 就是 RISC-V 的 `addi x1, x0, 5`。开着 `make ARCH=myrv watch` 时，也可以把这几行汇编贴进「汇编/反汇编」页，直接看指令字。两个模拟器打印同样的结果：

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

## ④ 读懂输出

| 行 | 含义 |
|---|---|
| `steps 4` | 执行了几条指令 |
| `PC 0x…10` | 停下时的 PC |
| `reg x1 0x…05` | 寄存器的值；只列出非零的寄存器 |

**退出码**

| 退出码 | 含义 |
|---|---|
| 0 | 正常停机 |
| 1 | 非法指令、故障，或超过步数上限（默认 1,000,000 步，用 `--max-steps N` 改） |
| 2 | 用法错误 |

**两个模拟器**

- 由同一份 XML 生成：Sail 版是参考实现，Rust 版用来跑得快；
- rsim 另外在标准错误上打印一行统计（`rsim: 4 warp instructions in …`）。

::: warning 注意
- **改了 XML 之后，先运行 `make ARCH=myrv sim rsim`**，再汇编和运行。`tools/asm.py` 读的是构建副本 `build/isa/myrv`，模拟器是编译好的二进制，不重新 make 用的就是旧版本。
- 当前的汇编器每行只认一条指令，**不支持注释和标签**。
:::
