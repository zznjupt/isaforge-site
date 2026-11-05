# ISAForge 是什么

ISAForge 是一套指令集工具：你把指令集写成一份机器可读的规格，编码、操作数、合法性条件和汇编语法写成 XML，每条指令的执行语义写成 [Sail](https://github.com/rems-project/sail)；ISAForge 从这一份规格生成译码器、汇编器、反汇编器、两个功能模拟器和指令手册，再把它们对照真实的工具和硬件逐项验证。

## 思路

一套指令集的知识通常散在好几处：手册、汇编器、反汇编器、模拟器、测试。它们各自手写，各自出错，时间一长就彼此走样。

ISAForge 只让人写一处。一条指令写成一个文件，它的位段、操作数、语法和语义都在里面：

```xml
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
```

汇编器读 `<syntax>` 把文本编码成指令字，反汇编器用同一个模板打印回来；译码器由 `<encoding>` 生成，`<execute>` 同时编进 Sail 模型和 Rust 模型。改一处，所有工具一起变。

## ISA 包

一套指令集写成一个 **ISA 包**，放在 `isa/<名字>/` 下：

- `arch.xml`：指令长度、执行模型（标量，或带 lane 和谓词的 SIMT）、扩展、立即数类型；
- `registers.xml`：寄存器堆和地址空间，语义通过生成的 `read_X`、`write_X` 访问它们；
- `layouts.xml`：多条指令共用的位段划分，如 RISC-V 的 R、I、S 型；
- `enums.xml`：命名的取值，如比较条件、修饰符；
- `instructions/*.xml`：每个助记符一个文件，内有若干编码变体（form）和语义（operation）；
- `shared.xml`：多条指令共用的 Sail 函数。

## 能得到什么

- **工具链**：译码器、汇编器（支持别名）、反汇编器，Sail 编出的参考模拟器，以及快得多的 Rust 模拟器（单 warp、整个 grid 的多线程启动、批量运行）。
- **验证**：静态检查证明任意两种编码不会匹配同一个指令字；两个模拟器的随机差分；自定义指令的等价性证明；与反汇编器、ISA 模拟器和实机的对照；覆盖率报告。
- **手册**：每条指令一页，有编码图、操作数表、语法和语义；还有编码空间、寄存器、枚举和共享函数各一页。

## 适合什么

- 给一套新指令集或一组扩展写规格，并马上得到能跑的工具；
- 做指令集设计探索：加一条融合指令，证明它等价于被替换的指令序列；
- 给只有二进制和反汇编器的指令集（例如 GPU 的 SASS）写一份可执行、可检验的规格；
- 给周期级模型提供功能模型。

ISAForge 描述的是指令集，不是微架构：它不描述流水线的时序，也不生成 RTL。

处理器类型上，标量 CPU 和 SIMT GPU 都已支持；后续将支持 NPU 等更多类型的处理器。

下一页：[快速开始](./getting-started)。
