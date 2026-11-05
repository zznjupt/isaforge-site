# 写一个 ISA 包

一个 ISA 包放在 `isa/<名字>/` 下，由几种 XML 文件组成。`make check` 检查它；编辑器认得同一份 schema（`schema/isa.xsd`），写的时候就有补全和中文说明。

## form 与 operation

一个助记符一个文件。文件里有两种东西：

- **form**：一种编码变体。同一个助记符可以有寄存器版、立即数版、uniform 寄存器版……每个 form 有自己的位段、操作数和语法，`id` 在整个 ISA 包里唯一；
- **operation**：语义，用 Sail 写，可以被多个 form 共用。form 用 `operation="名字"` 指明它执行哪一个，必要时用一段纯 `<decode>` 把字段换算成 operation 的输入。

B300 SASS 的 LOP3 有三种 form，共用一个 operation，三种 form 的第二个源分别来自寄存器、uniform 寄存器和立即数：

```xml
<form id="lop3_lut__RRR_RRR" operation="lop3_lut">
  <decode><![CDATA[d.Rd = f.Rd; d.Ra = f.Ra; d.b = SrcR(f.Rb); d.Rc = f.Rc; ...]]></decode>
</form>
<form id="lop3_lut__RUR_RUR" operation="lop3_lut">
  <decode><![CDATA[d.Rd = f.Rd; d.Ra = f.Ra; d.b = SrcU(f.URb); d.Rc = f.Rc; ...]]></decode>
</form>
```

## 位段与操作数

位段可以写在 form 里，也可以引用 `layouts.xml` 里的布局。与布局字段同名的操作数自动对应到那个字段，其余的字段用 `<const>` 固定。操作数的 `type` 是：

| type | 字段里存的 | 汇编里写作 |
|---|---|---|
| 寄存器堆名，如 `X` | 寄存器编号 | 寄存器的汇编名，如 `x5` |
| `arch.xml` 里声明的立即数类型，如 `simm` | 立即数，按 `width` 做符号扩展，可以带 `scale` | 按声明：十进制、十六进制、浮点、位集 |
| `enums.xml` 里的枚举 | 枚举编码 | 枚举值的名字，如 `.EQ` |

立即数类型由 ISA 包自己声明，ISAForge 不认识任何具体的名字；操作数还可以是 PC 相对的，或者按另一个操作数的值选择类型。

## 汇编语法

`<syntax>` 是一个模板，汇编器和反汇编器都从它生成：

::: v-pre
- `{名字}` 填操作数，`{.名字}` 是取非默认值时才出现的后缀；
- `{{ … }}` 是可选段，里面的操作数都取默认值时整段省略；
- `[[ 项 | 项 ]]` 是方括号里的项，`<< 槽 | 槽 >>` 是逗号分隔的槽。
:::

SIMT 的 ISA 包里，每条指令都可以带谓词，取默认值时不打印：

```xml
<syntax>{{@{P} }}add {Rd}, {Ra}, {Rb}</syntax>
```

**别名**在条件成立时代替助记符，汇编器也接受它：

```xml
<alias mnemonic="li">
  <when>rs1 == `X@x0</when>
  <syntax>li {rd}, {imm}</syntax>
</alias>
```

## 扩展

`arch.xml` 声明扩展和它们的依赖；指令或 form 用 `feature` 标出所属的扩展。`make FEATURES="I M"` 只构建这些扩展，生成的译码器、汇编器、模拟器和手册都按启用的集合来。

```xml
<features>
  <feature name="I">
    <description>基础整数指令集 RV64I。</description>
  </feature>
  <feature name="Zmmul" requires="I">
    <description>只含乘法的 M 子集：MUL、MULH、MULHSU、MULHU、MULW。</description>
  </feature>
  <feature name="M" requires="Zmmul">
    <description>整数乘除法。</description>
  </feature>
</features>
```

```xml
<instruction mnemonic="MUL" feature="Zmmul">
```

## 执行模型

`arch.xml` 的 `<execution>` 说明模型怎么执行：

- `<execution/>`：标量，一次一条指令，由某条指令调用 `halt()` 停机；
- `lanes="32"`：SIMT，每条指令对一个 warp 的各 lane 执行，语义多一个 lane 掩码 `m`；
- `<guard operand="Pg"/>`：按谓词执行，掩码是活动 lane 与谓词的与；
- `<launch/>`：启动身份，模拟器能按 grid 和 block 启动所有 warp；
- 寄存器可以声明待生效写入的冲突和冒险规则，配合 `wait` 与钩子函数描述延迟写入的流水线。

## 语义

`<execute>` 用 Sail 的一个子集写，也就是 Rust 模型能翻译的部分：位向量运算、`let`、`if`、`match`、`foreach` 和调用共享函数。语义只通过生成的接口访问状态。LOP3 的语义：

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

`m` 是这一步的 lane 掩码，`lop3` 和 `read_Src` 是 `shared.xml` 里的共享函数。像这样只读写本 lane 的循环，Rust 模型拆成整个 warp 的运算加掩码写回，交给 LLVM 向量化。

## 检查些什么

`make check` 检查一个 ISA 包：

- 字段在指令字以内、互不重叠，引用的布局、枚举、编码表都存在；
- **任意两个可译码的 form 不会匹配同一个指令字**：每一对都有一个字段的允许值不相交。分不开时，逐字段对照两个 form 并给出改法；
- 同一段汇编文本不会被编成两个不同的指令字；
- 每个 form 的语法都写出了它的全部操作数；
- 语义都在 Sail 子集之内，类型和位宽对得上；
- 按每个 form 随机生成的指令字都能译码回来。

报错带着文件和行号。
