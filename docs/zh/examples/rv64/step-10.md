# 第 10 步：覆盖率与手册

> **目标**：找出测试没覆盖到的地方，并生成指令手册。

## ① 覆盖率

```sh
make ARCH=myrv coverage
```

它在一个带计数的 Rust 模拟器上跑全部定向测试和随机程序，统计哪些 form、字段取值和语义分支被执行过。最后打印一行汇总，详细报告写在 `build/coverage/myrv/report.txt`：

```text
myrv: 13/13 modeled forms executed, 2/5 branches taken, 11 fields with unseen values -> build/coverage/myrv/report.txt
```

报告的主要部分（节选）：

```text
forms with semantics executed: 13/13
semantic branches taken: 2/5 (40.0%)

forms with semantics never executed (0):

operand field values never seen (11 fields):
  field:beq:imm: zero, negative minimum, negative
  field:bne:rs1: x16, x18, x20, x22, x23, x27
  field:lui:imm: high bit only, all below the high bit
  …
semantic branches never taken (3):
  build/isa/myrv/instructions/BEQ.xml:21  BEQ  then
  build/isa/myrv/instructions/BNE.xml:21  BNE  then
  build/isa/myrv/instructions/JAL.xml:18  JAL  then
```

| 部分 | 含义 | 怎么处理 |
|---|---|---|
| forms with semantics never executed | 有语义却从没执行过的 form | 应该为空 |
| operand field values never seen | 寄存器字段列出没出现过的寄存器；立即数字段按边界类（0、1、全 1、最小负数、最大正数等）列出没覆盖到的类，只列这个字段取得到的类（分支偏移是 2 的倍数，所以没有 1 和全 1；无符号字段用 `high bit only` 等名字） | 为重要的边界值补定向测试 |
| semantic branches never taken | 语义里从没走到的分支，带 XML 行号 | 上面三个都是"跳转目标不对齐"那一支，需要一个定向测试专门覆盖 |

::: info 说明
报告里的路径指向构建副本 `build/isa/myrv/…`，改的时候改 `isa/myrv/` 里的源文件，行号相同。
:::

## ② 指令手册

```sh
make ARCH=myrv docs
open build/myrv/docs/index.html
```

首页先给几个数字（指令、form、有语义的比例），下面是按特性分组的指令表：说明、语法，以及“语义”一列——绿色 ✓ 表示写了 `<execute>`，“无语义”表示模拟器执行到它会停下。顶部的导航栏通到编码空间、枚举、共享 Sail 定义和覆盖率几页。

每条指令一页，包括：

- 有多个 form 时，先是一张“form 一览”，哪些有语义一眼可见；
- 每个 form 一张卡片：汇编语法、编码图（蓝色是固定位，绿色是操作数，橙色是编码表或表达式）、字段表和操作数表、语义代码和你写的说明；
- 语义代码里用到的共享函数可以点进「共享 Sail 定义」页。

跑过 `coverage` 之后，「覆盖率」页给出每条指令、每个 form 的执行、字段取值和分支覆盖。

## ③ 编码空间

加新指令之前，先看编码空间里哪里还空着：

```sh
make ARCH=myrv encoding-map
```

```text
myrv: 13 forms, 32-bit words; 2.1% of the encoding space is used
every form fixes 1:0 = 11; the 75% of the space where these bits differ is free
first level 6:2: 32 cells, 2 full, 6 partly used, 24 free
  free: 6:0=0000111 … 6:0=0001111 (3 cells); 6:0=0010111 … 6:0=0011111 (3 cells); 6:0=0100111 … 6:0=0101111 (3 cells); 6:0=0111011 … 6:0=1011111 (10 cells); 6:0=1100111 … 6:0=1101011 (2 cells); 6:0=1110111 … 6:0=1111111 (3 cells)
  6:0=0000011    12% used  ld
  6:0=0010011    13% used  addi slli
  6:0=0100011    12% used  sd
  6:0=0110011  0.39% used  add mul sh1add sub
  6:0=0110111   100% used  lui
  6:0=1100011    25% used  beq bne
  6:0=1101111   100% used  jal
  6:0=1110011  <0.01% used  ecall
```

| 行 | 含义 |
|---|---|
| `2.1% of the encoding space is used` | 13 个 form 一共占了整个 32 位编码空间的 2.1% |
| `every form fixes 1:0 = 11` | 所有指令的 1:0 都是 11；这两位取其他值的 3/4 空间完全空闲（RISC-V 的压缩指令就用这一部分） |
| `first level 6:2` | 第一层是"所有 form 都固定、但取值不全相同的位"，这里正好是 RISC-V 规范里那张 opcode 表 |
| `free: …` | 完全空闲的格，按 6:0 的完整取值列出 |
| 后面每行 | 一个已用的格：已用比例和其中的指令。比如 `0110011` 里 ADD、SUB、MUL、SH1ADD 只用了 0.39%，靠 funct3 和 funct7 区分，还有大量空位 |

手册里的「编码空间」页面（`encoding.html`）是同一张图的网格版：行、列各是第一层的几位，颜色越深的格被占得越满，空白格完全空闲；鼠标停在格子上看占用比例和全部指令，点格子能看到每个 form 在第一层之外还固定了哪些常量。
