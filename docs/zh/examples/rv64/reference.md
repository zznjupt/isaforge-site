# 常见报错与命令速查

## 常见报错

::: warning 注意
`make check` 的报错路径指向构建副本 `build/isa/myrv/…`。行号与源文件相同，**改的时候改 `isa/myrv/` 里的文件**，构建副本下次构建就会被覆盖。`make ARCH=myrv watch` 会自动把路径换回源文件。
:::

**检查时（`make check`）**

| 报错（节选） | 原因 | 怎么改 |
|---|---|---|
| `ADDI.xml:5: form addi: layouts.xml:6: rs1: overlaps another field` | 布局里两个字段的位段重叠 | 检查 `<range>` 的 msb 和 lsb。它后面常跟着几条由它引起的位宽错误，修好重叠它们就消失 |
| `ADD.xml:5: form add and SUB.xml:5: form sub can match the same word, e.g. 0x00000033` | 两个 form 能匹配同一个指令字，译码无法区分；`e.g.` 后面是两者都匹配的一个字 | 看紧跟在后面的逐字段对照（见表下） |
| `AMBIGUOUS …ADD.xml:5: form add and …SUB.xml:5: form sub both assemble 'add x0, x0, x0', to different words` | 两个 form 的语法模板能写出同一段文本 | 修改其中一个的 `<syntax>` |
| `ADD.xml:16: form add: syntax references undeclared operand rs3` | 语法模板里的 `{名字}` 不是这个 form 的操作数 | 改正名字，或在 `<operands>` 里声明 |
| `ADD.xml:20: ADD__add: write_X argument 1: bits(32) where bits(64) is expected` | 语义里的位宽不匹配：把 32 位的值写进 64 位寄存器 | 用 `sail_sign_extend`/`sail_zero_extend` 扩展到目标宽度 |
| `ADD.xml:20: ADD__add: unknown function add64` | 调用了不存在的函数 | 改用内置函数，或在 `shared.xml` 里定义它（见 `isa/rv64/shared.xml`） |

两个 form 冲突时，检查会把它们逐字段并排对照。下面是把 SUB 的 funct7 误写成和 ADD 一样时的输出：

```text
build/isa/myrv/instructions/ADD.xml:5: form add and build/isa/myrv/instructions/SUB.xml:5: form sub can match the same word, e.g. 0x00000033
    bits     add             sub
    31:25    funct7=0000000  funct7=0000000  same constant in both
    24:20    rs2             rs2
    19:15    rs1             rs1
    14:12    funct3=000      funct3=000      same constant in both
    11:7     rd              rd
    6:0      opcode=0110011  opcode=0110011  same constant in both
    to tell them apart: give one form a different constant in funct7 (31:25), funct3 (14:12) or opcode (6:0)
```

- `same constant in both`：两边都把这些位固定成了同一个值，冲突就出在这里；
- `only … fixes it`：只有一边固定了这些位，另一边放的是操作数，在那一边也固定一个不同的常量，就能把它们分开；
- 最后一行直接给出改法。

**运行和汇编时**

| 报错（节选） | 原因 | 怎么改 |
|---|---|---|
| `illegal instruction at pc 0x… word 0x…` | 这个指令字不匹配任何启用的 form | 检查编码，或者是不是用 `FEATURES` 禁用了它 |
| `work/mul.s:3: no instruction matches 'mul x3, x1, x2'` | 汇编器认不出这一行（例如只启用 I 时汇编 `mul`） | 对照 `<syntax>` 检查写法，或者是不是用 `FEATURES` 禁用了它；汇编器不支持注释和标签 |


## 交付前的检查清单

```sh
make ARCH=myrv check sim-test rsim-test fuzz equiv equiv-prove
make ARCH=myrv FEATURES="I M" spike
make ARCH=myrv coverage docs
```

| 行 | 覆盖的验证 |
|---|---|
| 第 1 行 | 静态检查、定向测试、随机差分、等价性 |
| 第 2 行 | 外部参考（如果你的 ISA 有） |
| 第 3 行 | 覆盖率报告和指令手册 |


## 下一步

- **完整的 RV64I**：ISAForge 自带的 `isa/rv64/` 有 I、M、Zba 的全部 72 个 form，另有 `shared.xml`（语义共用的函数，如除法）、`enums.xml`（FENCE 的枚举操作数）和更多别名。用 `make ARCH=rv64 …` 运行同样的命令。
- **ISA 包的写法**：[写一个 ISA 包](../../guide/package)讲布局、别名、扩展和执行模型；`schema/isa.xsd` 是 XML 的 schema。
- **GPU / SIMT 架构**：执行模型写 lane 数、谓词和启动身份，见[执行模型](../../guide/package#执行模型)。

## 附录：命令速查

| 做什么 | 命令 |
|---|---|
| 静态检查 | `make ARCH=myrv check` |
| 边改边看（检查、手册、预览、汇编/反汇编页） | `make ARCH=myrv watch`（`WATCH_ARGS=--once` 只跑一轮） |
| 编码空间 | `make ARCH=myrv encoding-map`，或手册里的「编码空间」页 |
| 编译两个模拟器 | `make ARCH=myrv sim rsim` |
| 汇编 | `python3 tools/asm.py build/isa/myrv 程序.s 程序.hex` |
| 按 form 编码 `.prog` | `python3 tools/encode.py build/isa/myrv 程序.prog 程序.hex` |
| 反汇编 | `python3 tools/disasm.py build/isa/myrv 程序.hex [--no-aliases]` |
| 运行（Sail） | `build/myrv/xinyu-sim [--state 状态文件] [--max-steps N] 程序.hex` |
| 运行（Rust） | `build/rsim/myrv/release/rsim run 程序.hex --arch myrv [--state 状态文件] [--max-steps N]` |
| 定向测试 | `make ARCH=myrv sim-test rsim-test` |
| 随机差分 | `make ARCH=myrv fuzz`（`FUZZ_COUNT`、`FUZZ_SEED`） |
| 等价性 | `make ARCH=myrv equiv equiv-prove` |
| 只启用部分扩展 | 任意命令加 `FEATURES="I M"` |
| 外部参考 | `make ARCH=myrv corpus`、`make ARCH=myrv FEATURES="I M" spike` |
| 覆盖率、手册 | `make ARCH=myrv coverage docs` |
