# 生成什么

从一个 ISA 包，`make` 生成下面这些东西。它们读的是同一份规格，所以一处改动会同时出现在所有工具里。

| 产物 | 命令 | 在哪里 |
|---|---|---|
| 汇编器 | `python3 tools/asm.py build/isa/<名字> in.s out.hex` | 按 `<syntax>` 和别名汇编，出错时报出文件和行号 |
| 反汇编器 | `python3 tools/disasm.py build/isa/<名字> prog.hex` | 逐条打印地址、指令字和文本；`--no-aliases` 不用别名 |
| Sail 参考模型 | `make ARCH=<arch> sim` | `build/<arch>/xinyu-sim` |
| Rust 快速模型 | `make ARCH=<arch> rsim` | `build/rsim/<arch>/release/rsim` |
| 指令手册 | `make ARCH=<arch> docs` | `build/<arch>/docs/index.html` |
| 编码空间 | `make ARCH=<arch> encoding-map` | 终端摘要；手册里是网格版 |

## 两个模拟器

**Sail 参考模型**：ISAForge 把寄存器、执行模型和每条指令的语义写成 Sail，再由 Sail 编译成 C。它是参考实现：语义怎么写，它就怎么执行。

**Rust 快速模型**：ISAForge 把同一份语义翻译成 Rust：位向量用 `u64`，整数按推出的值域用 `i64` 或 `i128`，逐 lane 的循环拆成整 warp 的运算。它用来跑得快，也用来和 Sail 模型互相印证。

两个模型读写同一种状态文本：结束时打印的状态，下一次可以用 `--state` 原样装回去。

```text
steps 4
PC 0x0000000000000010
reg x1 0x0000000000000005
reg x2 0x0000000000000002
reg x3 0x0000000000000801
```

Rust 模型还能按 grid 和 block 启动整个 kernel，在多个线程上运行，或者批量跑一组用例：

```sh
rsim run PROGRAM.hex --arch <名字> --grid X,Y,Z --block X,Y,Z --threads N
rsim batch MANIFEST --arch <名字> --threads N
rsim decode PROGRAM.hex --arch <名字>
```

Rust 模型单线程比 Sail 参考模型快约 170 倍，多线程时超过 600 倍。

## 手册

`make docs` 为每条指令生成一页：概括与说明，form 一览（哪些已经写了语义），每个 form 的语法、编码图、字段表、操作数表、合法性条件和语义。另有几页：

- **索引**：按扩展或首字母分组，可筛选，标出哪些指令还没写语义；
- **编码空间**：第一层编码位的网格，颜色越深占得越满，空格子可以直接分给新指令；
- **寄存器、枚举、共享 Sail 定义**：每个寄存器堆、每个枚举（编码与汇编文本的对照、谁在用）、每个共享函数（签名、说明、调用关系）；
- **覆盖率**：跑过 `make coverage` 之后，每条指令和每个 form 的执行、字段取值和分支覆盖。

## 编码空间

加新指令之前，先看哪里还空着。教程里 13 条指令的 ISA 包：

```text
myrv: 13 forms, 32-bit words; 2.1% of the encoding space is used
every form fixes 1:0 = 11; the 75% of the space where these bits differ is free
first level 6:2: 32 cells, 2 full, 6 partly used, 24 free
  6:0=0110011  0.39% used  add mul sh1add sub
  6:0=1100011    25% used  beq bne
  …
```

第一层取所有 form 都固定、但取值不全相同的位，所以 RV64I 自动得到 RISC-V 规范里的 opcode 表。检查已经证明 form 两两不重叠，每格的占用按 form 精确求和。

手册里是同一张图的网格版。完整的 RV64 ISA 包，行和列是 opcode 的 6:5 位和 4:2 位，颜色越深占得越满：

<div class="forge-figure">

[![rv64 的编码空间：13 个格子有指令，19 个完全空闲](/screens/encoding-rv64.png){.light-only}](/screens/encoding-rv64.png)
[![rv64 的编码空间，深色模式](/screens/encoding-rv64-dark.png){.dark-only}](/screens/encoding-rv64-dark.png)

</div>
