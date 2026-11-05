# 验证

两个模拟器从同一份规格生成，它们一致只说明 ISAForge 忠实地生成了两份实现；语义本身写错时，两份会一起错。所以 ISAForge 的验证分几层，每层查前一层查不到的东西。

| 层 | 命令 | 查什么 |
|---|---|---|
| 静态检查 | `make check` | 编码、语法、语义的结构；译码唯一；汇编无歧义 |
| 定向测试 | `make sim-test rsim-test` | 写好的程序在两个模型上得到期望的状态 |
| 随机差分 | `make fuzz`、`make fuzz-launch` | 随机程序和随机初态下，Sail 模型 ≡ Rust 模型 |
| 等价性 | `make equiv`、`make equiv-prove` | 一条新指令 ≡ 它替换的指令序列，随机比对并用 z3 证明 |
| 外部参考 | `make check`（语料）、`make spike` | 反汇编、汇编对照 nvdisasm 与 llvm-mc，执行对照 Spike |
| 实机 | 实机比对 | 同样的指令字在 GPU 上和在模型里的结果逐个输入比对 |
| 覆盖率 | `make coverage` | 哪些 form、字段取值和分支从来没被测到 |

## 静态检查

`make check` 在生成任何东西之前检查规格：字段不越界、不重叠；`<decode>` 给 operation 的每个输入赋一次值；语义在 Sail 子集之内，类型和位宽对得上。

最重要的一条是**译码唯一**：检查证明任意两个可译码的 form 都有一个字段的允许值不相交，所以一个指令字最多匹配一个 form。两个 form 分不开时，逐字段对照它们：

```text
ADD.xml:5: form add and SUB.xml:5: form sub can match the same word, e.g. 0x00000033
    bits     add             sub
    31:25    funct7=0000000  funct7=0000000  same constant in both
    24:20    rs2             rs2
    19:15    rs1             rs1
    14:12    funct3=000      funct3=000      same constant in both
    11:7     rd              rd
    6:0      opcode=0110011  opcode=0110011  same constant in both
    to tell them apart: give one form a different constant in funct7 (31:25), funct3 (14:12) or opcode (6:0)
```

## 随机差分

`make fuzz` 从 ISA 包里生成随机程序：随机的 form 和字段值，覆盖每个寄存器堆的随机初态，某个寄存器值附近的一段随机内存；SIMT 的 ISA 包还随机抽 grid 和 block，跑每个格子里的每个 warp（`make fuzz-launch`）。两个模型的打印和退出码必须完全相同，不一致时保留用例并打印复现命令。

每个写了语义的 ISA 包每次跑 300 个随机程序，两个模型全部一致；RV64 的 300 个程序执行了 31097 条指令，用到了全部 71 个写了语义的 form。

## 等价性证明

设计一条融合指令时，最好的参考是它替换的那段指令。在指令里声明这个等价关系：

```xml
<equivalence>
  <sequence>
    <step form="slli" rd="tmp" rs1="rs1" shamt="1"/>
    <step form="add" rd="rd" rs1="tmp" rs2="rs2"/>
  </sequence>
  <temps><temp name="tmp" file="X"/></temps>
  <preconditions>
    <distinct a="tmp" b="rs1"/>
    <distinct a="tmp" b="rs2"/>
  </preconditions>
</equivalence>
```

`make equiv` 随机抽满足前提的操作数和完整初态，分别运行新指令和序列，比较除临时寄存器外的全部状态；`make equiv-prove` 用 Sail 的 SMT 后端和 z3 证明它对所有满足前提的操作数和状态都成立。RV64 的六条 Zba 指令各在 1.2 秒以内得证：

```text
SH1ADD: proved (0.73s, z3)
SH2ADD.UW: proved (0.73s, z3)
```

声明写错时，z3 给出反例：哪组操作数、哪些寄存器初值让两边不同。

```text
SH1ADD: NOT proved (counterexample, 0.61s)
  counterexample:
    operands: rs2 = x4, rs1 = x2, rd = x6, temp tmp = x16
    initial X: x2 (rs1) = 0x000007FFFFFFFFFF, x4 (rs2) = 0x0000000000000008, …
```


## 外部参考

- **反汇编**：每个 ISA 包可以带一份参考语料（指令字和参考工具打印的文本），`make check` 逐字比对。B300 的 SASS 对照 NVIDIA nvdisasm，12189 / 12189 一致；RV64 对照 llvm-mc，带别名 4441 / 4441、不带别名 4428 / 4428；
- **汇编往返**：语料里的文本汇编回去，必须得到同一个指令字，或者打印相同的另一种编码。RV64 的语料全部汇编回原来的指令字；B300 真实代码里的 4732 个字，都汇编成打印相同文本的指令字；
- **执行**：`make ARCH=rv64 spike` 让 21 个定向程序和 300 个随机程序（36039 条指令）在 Spike、Sail 模型、Rust 模型上运行，寄存器、PC 和每个内存字节都一致；
- **实机**：实机比对把要测的指令字改写进 ptxas 生成的 cubin，在 B300 上和在模型里用同样的输入执行，逐个比对 R、P、UR、UP 寄存器。61 个指令族、4457 种组合全部一致。

## 覆盖率

`make coverage` 在一个带计数的 Rust 模型上跑全部定向测试和随机程序，统计每个 form 的执行次数、每个操作数字段见过哪些取值（寄存器号、枚举值、立即数的边界类），以及语义里每个 `if` 和 `match` 分支是否走到：

```text
rv64: 71/71 modeled forms executed, 33/40 branches taken, 192 fields with unseen values
```

报告逐条列出没测到的东西和它在 XML 里的行号，手册的覆盖率页把它画成表。
