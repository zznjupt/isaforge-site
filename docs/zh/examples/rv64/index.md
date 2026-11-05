# 从零写一个 RV64I

> 用 XML 描述指令集，用 Sail 写指令语义，ISAForge 自动生成汇编器、反汇编器、两个功能模拟器和指令手册，并提供一整套正确性验证。这篇教程手把手带你走完一遍。

**你将完成**

- 从空目录写出一个 RV64I 子集 `myrv`：13 条指令，覆盖算术、移位、分支、跳转、访存、乘法和一条自定义指令；
- 得到它的汇编器、反汇编器、Sail 参考模拟器、Rust 快速模拟器和指令手册；
- 用六层验证确认它是对的：静态检查、定向测试、随机差分、等价性证明、外部参考（llvm-mc、Spike）、覆盖率。

**你需要**

- 约一小时动手，另有几分钟等编译和随机测试；
- 了解指令集的基本概念（寄存器、编码、立即数）。Sail 不用提前学，教程里用到的写法都会解释。

教程里的每个文件都完整给出，照着写就能得到和这里一模一样的输出。

<div class="forge-figure">

![学习路线：十步，分四个阶段](/tutorial/roadmap-zh.svg){.light-only}
![学习路线：十步，分四个阶段](/tutorial/roadmap-zh-dark.svg){.dark-only}

</div>

| 阶段 | 步骤 |
|---|---|
| 描述 ISA | [1. 骨架和第一条指令](./step-1) · [2. 让程序跑起来](./step-2) · [3. 补齐常用指令](./step-3) |
| 测试 | [4. 定向测试](./step-4) · [5. 随机差分](./step-5) |
| 扩展 ISA | [6. 扩展与特性开关](./step-6) · [7. 别名](./step-7) · [8. 自定义指令与等价性](./step-8) |
| 验证与交付 | [9. 对照外部参考](./step-9) · [10. 覆盖率与手册](./step-10) |

遇到报错，或想查一条命令，见[常见报错与命令速查](./reference)。

## 开始之前

**环境**

- 所有命令都在 ISAForge 的根目录运行；
- 需要 Python 3.10 或更新、`xmllint`、Sail 0.20.3（opam switch `sail`）和 z3、Rust；
- 第 9 步另需 llvm-mc、lld 和 Spike。

**确认环境可用**

```sh
make ARCH=rv64 check
```

最后一行是 `12/12 exact, 0 same text, 0 not encodable, 0 with no text, 0 untexted  assembler-only aliases  asm-only.tsv`，就说明环境正常。

**一个约定**

`ARCH=名字` 选择要处理的 ISA 包。本教程的 ISA 包叫 `myrv`，所以命令都带 `ARCH=myrv`。

**编辑器（推荐）**

用一个认得 XSD 的编辑器写 ISA 包：元素和属性能自动补全，鼠标悬停能看到中文说明，写错的地方当场标红。

- **VS Code**：先运行一次 `make editor`，它在本地写好 VS Code 的设置（推荐的插件和 schema 配置；之后的 `make check`、`make watch` 发现没有时也会自动写）。然后用 VS Code 打开 ISAForge 的目录，按提示安装推荐的 XML 插件（Red Hat 的 `redhat.vscode-xml`），不用再设置。你自己的 `.vscode/settings.json` 会保留，只补上缺的几项。
- **IntelliJ 系列**：Settings → Languages & Frameworks → Schemas and DTDs，添加一条：URI 填 `urn:xinyu:isa:1`，文件选 `schema/isa.xsd`。
- **其他编辑器**：支持 XML catalog 的，指向 `schema/catalog.xml` 即可。

::: info 说明
编辑器只能检查 schema 写得出的规则（元素、属性、取值）。字段重叠、编码冲突、Sail 语义这些，要靠 `make ARCH=myrv check`，或[第 1 步](./step-1)最后介绍的 `make ARCH=myrv watch`。
:::

## 先认识一个 ISA 包

<div class="forge-figure">

![你写什么，ISAForge 生成什么，怎样验证](/tutorial/overview-zh.svg){.light-only}
![你写什么，ISAForge 生成什么，怎样验证](/tutorial/overview-zh-dark.svg){.dark-only}

</div>

**做完后你会有这些文件**

```text
isa/myrv/                  ISA 包本身
  arch.xml                   指令长度、执行模型、扩展
  registers.xml              寄存器堆和内存
  layouts.xml                共用的编码布局
  instructions/ADDI.xml …    每个助记符一个文件
mk/myrv.mk                 告诉构建系统 ISA 包和测试在哪
tests/myrv/                你的定向测试
```

**贯穿全文的三个概念**

| 概念 | 写在哪 | 说明 |
|---|---|---|
| 寄存器和内存 | `registers.xml` | 语义代码只通过生成的访问函数读写它们，例如 `read_X(i)`、`write_X(i, v)`、`read_M(地址, 字节数)` |
| 一条指令 = 编码 + 语义 | `instructions/*.xml` | `<form>` 写编码（哪些位固定、哪些位是操作数）和汇编语法；`<operation>` 用 Sail 写执行语义 |
| 布局（layout） | `layouts.xml` | 多条指令共用的位段划分，比如 RISC-V 的 I 型、R 型。写一次，各条指令按名字引用 |

下一步：[骨架和第一条指令](./step-1)。
