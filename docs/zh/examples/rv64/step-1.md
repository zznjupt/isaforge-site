# 第 1 步：骨架和第一条指令

> **目标**：写出能通过检查的最小 ISA 包，包含 4 个 XML 文件、1 条指令和一个构建配置。

## ① 写 `arch.xml`：指令长度和执行模型

新建 `isa/myrv/arch.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<arch xmlns="urn:xinyu:isa:1" name="myrv" length="32">
  <description>教程用的 RV64I 子集：64 位整数寄存器，标量执行。</description>
  <execution/>
  <immediates>
    <immediate name="uimm" print="decimal"/>
    <immediate name="simm" signed="true" print="decimal"/>
  </immediates>
</arch>
```

- `length="32"`：指令字长 32 位；
- `<execution/>`：标量执行模型，一次执行一条指令。GPU 这类 SIMT 架构在这里写 lane 数和谓词，见[写一个 ISA 包](../../guide/package#执行模型)；
- `<immediates>`：ISA 包里用到的立即数类型。这里声明两种：`uimm` 无符号、`simm` 有符号，汇编和反汇编都用十进制。操作数的 `type` 写这两个名字，位宽在操作数上写（`width`）。别的 ISA 可以声明按十六进制打印的、浮点的立即数，见[写一个 ISA 包](../../guide/package#位段与操作数)。

## ② 写 `registers.xml`：寄存器和内存

新建 `isa/myrv/registers.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<registers xmlns="urn:xinyu:isa:1">
  <file name="X" count="32" width="64" asm="x{n}">
    <description>32 个 64 位通用寄存器。x0 读出恒为 0，写入被丢弃。</description>
    <reg index="0" read="0" write="discard"/>
  </file>
  <memory name="M" address-width="64" endian="little" fetch="true">
    <description>按字节寻址的小端内存，程序也从这里取指。</description>
  </memory>
</registers>
```

- **`X`**：32 个 64 位寄存器，汇编名 `x0` 到 `x31`。`X` 这个名字后面有三处用到：
  - 操作数类型：`type="X"`；
  - 访问函数：`read_X`、`write_X`；
  - 汇编名：`asm="x{n}"` 里的 `{n}` 换成编号。
- **`<reg index="0" … />`**：x0 读出恒为 0、写入被丢弃，语义里不用为它特判。
- **`M`**：一块小端内存。`fetch="true"` 表示程序装在这块内存的地址 0，并从这里取指。

## ③ 写 `layouts.xml`：编码布局

新建 `isa/myrv/layouts.xml`，先只放 I 型：

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
</layouts>
```

## ④ 写第一条指令 ADDI

新建 `isa/myrv/instructions/ADDI.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ADDI">
  <summary>立即数加</summary>
  <description>把 <op>rs1</op> 与符号扩展的 <op>imm</op> 相加，结果写入 <op>rd</op>。</description>
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

下图把这个文件的各部分和指令字对应起来：

<div class="forge-figure">

![一条指令的组成：以 ADDI 为例](/tutorial/anatomy-zh.svg){.light-only}
![一条指令的组成：以 ADDI 为例](/tutorial/anatomy-zh-dark.svg){.dark-only}

</div>

| 部分 | 作用 |
|---|---|
| `<form id="addi" layout="I">` | 一种编码变体。`id` 在整个 ISA 包里唯一，位段取自 I 型布局 |
| `<operands>` | 与布局字段同名的操作数自动对应到那个字段。`type="X"` 是寄存器编号；`simm` 是有符号立即数，`width` 是位宽 |
| `<encoding>` | 固定的位，这里是 opcode 和 funct3 |
| `<syntax>` | 汇编语法模板，`{名字}` 处填操作数。汇编器和反汇编器都由它生成 |
| `<description>` | 写进指令手册。`<op>名字</op>` 引用操作数，改名后检查会发现失效的引用 |
| `<execute>` | 语义，用 Sail 写。`d.名字` 是操作数的值；返回 `RETIRE_OK` 表示正常完成，PC 前进到下一条 |

::: tip 提示
语义只能用 Sail 的一个子集，也就是 Rust 模拟器能翻译的部分。最常用的就是这里出现的 `read_X`/`write_X`、`+`、`sail_sign_extend`。更多写法见[写一个 ISA 包](../../guide/package#语义)。
:::

## ⑤ 写构建配置 `mk/myrv.mk`

它告诉构建系统：ISA 包在 `isa/myrv`，构建前拷贝到 `build/isa/myrv`。

新建 `mk/myrv.mk`：

```make
# myrv：教程里从零编写的 RV64I 子集。用 make ARCH=myrv ... 选中。

ISA := build/isa/myrv
HAND := isa/myrv
# 还没有参考语料。
CORPUS :=
CORPUS_CHECK :=
CORPUS_NO_ALIASES :=
ASM_CHECK :=
CORPUS_FILES :=
CORPUS_ALL :=
# 还没有定向测试。
SIM_TESTS :=
STATE_TESTS :=

MYRV_XML := $(wildcard $(HAND)/*.xml) $(wildcard $(HAND)/instructions/*.xml)

# 没有导入器：把手写的 ISA 包原样拷进构建目录。
$(ISA)/arch.xml: $(FEATURES_STAMP) $(MYRV_XML)
	rm -rf $(ISA)
	mkdir -p $(ISA)/instructions
	cp $(HAND)/*.xml $(ISA)/
	cp $(HAND)/instructions/*.xml $(ISA)/instructions/
	$(WRITE_FEATURES)
```

::: warning 注意
规则行首必须是制表符，不能是空格。
:::

## ⑥ 运行检查

```sh
make ARCH=myrv check
```

输出比较长，其中一部分是 ISAForge 自己的测试。和你的 ISA 包有关的是这几行：

```text
schema: all files valid
0 Sail bodies outside the subset
1 forms, 0 structural errors
0 pairs of decodable forms not told apart
0 ambiguous assembly texts
pass 4545 generated words decode (ISA myrv, seed 1); dropped forms: none
```

| 输出 | 检查了什么 |
|---|---|
| `schema: all files valid` | XML 符合 schema |
| `0 Sail bodies outside the subset` | 语义都在 Sail 子集之内，类型和位宽都对得上 |
| `1 forms, 0 structural errors` | 字段不越界、不重叠，引用的东西都存在 |
| `0 pairs of decodable forms not told apart` | 任意两个 form 不会匹配同一个指令字，译码结果唯一 |
| `0 ambiguous assembly texts` | 同一段汇编文本不会被汇编成两个不同的指令字 |
| `pass … generated words decode` | 按每个 form 随机生成的指令字都能译码回来 |

::: warning 重要
- 命令以 `make: *** … Error 1` 结束就说明有错，往上找带文件名和行号的那一行，对照[常见报错](./reference#常见报错)修改。
- `instructions/` 里至少要有一个文件，否则拷贝一步会报 `cp: isa/myrv/instructions/*.xml: No such file or directory`。
:::

## ⑦ 边改边看（推荐）

从这里开始，可以在另一个终端里一直开着：

```sh
make ARCH=myrv watch
```

```text
preview: http://127.0.0.1:8000/   assembler: http://127.0.0.1:8000/__asm/
watching isa/myrv (Ctrl-C to stop)
[10:20:31] check passed, documentation updated (1.1 s)
```

每次保存 `isa/myrv/` 里的文件，它都会：

- 重新拷贝 ISA 包并检查。只跑它自己的检查，比 `make check` 快；
- 检查通过：重新生成指令手册，浏览器里打开的预览页自动刷新；
- 检查不通过：终端和预览页顶部都显示报错，路径指向你编辑的 `isa/myrv/…` 源文件；手册保持在上一次通过时的版本。

汇编器的检查（汇编往返、有没有一段文本能汇编成两种字）放在手册更新之后、在后台跑，只查你改到的指令。myrv 这样的小 ISA 包一眼就跑完，什么也不多打印；指令上千的 ISA 包会在终端里逐步打印用时，预览页顶部的蓝条显示正在跑哪一步，发现问题时变成红条。

预览页顶部的「汇编/反汇编」可以随手试：每行写一条汇编，马上看到指令字和每个字段的位；切到“机器码 → 汇编”粘贴指令字，看译码出的 form 和汇编文本。不记得怎么写时：

- 右边的指令速查可以按助记符或说明搜索，每条指令列出写法、每个操作数能取什么，以及一条点“插入”就能用的例子；
- 正在写的那一行，编辑框下面会提示它的写法和操作数范围；
- 写错的一行会给出这条指令的正确写法（或拼写相近的指令），点“换成这个”直接替换。

手册里每个 form 旁边也有“试一试”，点开就是填好例子的这一页。这一页不会改动你的 ISA 包。

::: tip 提示
`make ARCH=myrv watch WATCH_ARGS=--once` 只跑一轮就退出；`WATCH_ARGS=--no-serve` 不开预览；`WATCH_ARGS="--port 9000"` 换端口。
:::
