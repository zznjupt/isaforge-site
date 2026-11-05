# 快速开始

这一页从空目录写出一个最小的 ISA 包 `myrv`：两条 RISC-V 指令，ADDI 和用来停机的 ECALL；检查它，汇编一个程序，在两个模拟器上运行。完整的十步教程见[从零写一个 RV64I](../examples/rv64/)。

## 准备

下面的命令都在 ISAForge 的根目录运行。需要：

- Python 3.10 或更新，`xmllint`；
- Sail 0.20.3（opam switch `sail`）和 z3；
- Rust（ISAForge 会自动选用合适的版本）。

先确认环境可用：

```sh
make ARCH=rv64 check
```

## 骨架

`isa/myrv/arch.xml`：32 位指令字，标量执行，两种立即数类型。

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

`isa/myrv/registers.xml`：32 个 64 位寄存器，x0 读出恒为 0；一块小端内存，程序从地址 0 取指。

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

`isa/myrv/layouts.xml`：两条指令都用 I 型的位段。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<layouts xmlns="urn:xinyu:isa:1">
  <layout name="I">
    <field name="imm"><range msb="31" lsb="20"/></field>
    <field name="rs1"><range msb="19" lsb="15"/></field>
    <field name="funct3"><range msb="14" lsb="12"/></field>
    <field name="rd"><range msb="11" lsb="7"/></field>
    <field name="opcode"><range msb="6" lsb="0"/></field>
  </layout>
</layouts>
```

## 两条指令

`isa/myrv/instructions/ADDI.xml`：

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

- 与布局字段同名的操作数自动对应到那个字段；`<encoding>` 给出固定的位；
- `<syntax>` 是汇编语法模板，汇编器和反汇编器都由它生成；
- `<execute>` 是 Sail 语义，`d.名字` 是操作数的值。

`isa/myrv/instructions/ECALL.xml`：所有位都固定，执行时让模型停下。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<instruction xmlns="urn:xinyu:isa:1" mnemonic="ECALL">
  <summary>环境调用</summary>
  <description>向执行环境请求服务；这里的模型在此停机。</description>
  <form id="ecall" layout="I">
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

## 构建配置

`mk/myrv.mk` 告诉构建系统 ISA 包在哪里：

```make
ISA := build/isa/myrv
HAND := isa/myrv
CORPUS :=
CORPUS_CHECK :=
CORPUS_NO_ALIASES :=
ASM_CHECK :=
CORPUS_FILES :=
CORPUS_ALL :=
SIM_TESTS :=
STATE_TESTS :=

MYRV_XML := $(wildcard $(HAND)/*.xml) $(wildcard $(HAND)/instructions/*.xml)

$(ISA)/arch.xml: $(FEATURES_STAMP) $(MYRV_XML)
	rm -rf $(ISA)
	mkdir -p $(ISA)/instructions
	cp $(HAND)/*.xml $(ISA)/
	cp $(HAND)/instructions/*.xml $(ISA)/instructions/
	$(WRITE_FEATURES)
```

## 检查

```sh
make ARCH=myrv check
```

和这个 ISA 包有关的几行：

```text
schema: all files valid
0 Sail bodies outside the subset
2 forms, 0 structural errors
0 pairs of decodable forms not told apart
0 ambiguous assembly texts
```

XML 符合 schema；语义都在 Rust 模型能翻译的 Sail 子集里；字段不越界、不重叠；任意两个 form 不会匹配同一个指令字；同一段汇编不会编成两个不同的字。

## 运行

写一个程序 `work/hello.s`：

```text
addi x1, x0, 5
addi x2, x1, -3
addi x3, x2, 2047
ecall
```

汇编，编译两个模拟器，运行：

```sh
make ARCH=myrv sim rsim
python3 tools/asm.py build/isa/myrv work/hello.s work/hello.hex
build/myrv/xinyu-sim work/hello.hex
build/rsim/myrv/release/rsim run work/hello.hex --arch myrv
```

`work/hello.hex` 的第一行 `00500093` 就是 RISC-V 的 `addi x1, x0, 5`。Sail 模型和 Rust 模型打印同样的结果：

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

执行了 4 条指令，停在 0x10，只列出非零的寄存器。

## 下一步

- [写一个 ISA 包](./package)：布局、别名、扩展、SIMT 的执行模型；
- [验证](./verification)：定向测试、随机差分、等价性证明、对照外部参考；
- [从零写一个 RV64I](../examples/rv64/)：十步写出 13 条指令，一直验证到和 Spike 逐字节一致。
