# 第 4 步：定向测试

> **目标**：把程序和期望输出固定下来，以后每次修改都自动在两个模拟器上回归。

测试和验证分好几层，每层回答的问题不同。第 4 到第 10 步会逐层用到：

<div class="forge-figure">

![每一层验证比较什么、能发现什么](/tutorial/verification-zh.svg){.light-only}
![每一层验证比较什么、能发现什么](/tutorial/verification-zh-dark.svg){.dark-only}

</div>

## ① 写测试程序

测试程序用 `.prog` 格式：每行写 form id 和字段值，不经过汇编语法。

新建 `tests/myrv/sum.prog`：

```text
# 1 + 2 + ... + 10，结果写到内存 0x1000 再读回。
addi  rd=x1 rs1=x0 imm=10
addi  rd=x2 rs1=x0 imm=0
add   rd=x2 rs1=x2 rs2=x1          # 循环体：sum += n
addi  rd=x1 rs1=x1 imm=-1          # n -= 1
bne   rs1=x1 rs2=x0 imm=-8         # n != 0 时回到循环体（向前 8 字节）
lui   rd=x5 imm=1                  # x5 = 0x1000
sd    rs1=x5 rs2=x2 imm=0
ld    rd=x6 rs1=x5 imm=0
ecall
```

- `#` 之后是注释；
- 程序从全零的初始状态开始运行。

## ② 写带初始状态的测试

第二个测试从状态文件读入寄存器和内存的初值。状态文件的格式和 dump 相同。新建 `tests/myrv/start.state`：

```text
PC 0x0000000000000000
reg x10 0x00000000000000FF
reg x11 0x0000000000000001
mem M 0x0000000000002000 0x1122334455667788
```

`mem` 行的第一个字节放在最低地址，所以从 0x2000 读出的小端 8 字节值是 0x8877665544332211。再新建 `tests/myrv/state.prog`：

```text
# args: --state tests/myrv/start.state
# 从状态文件读入 x10、x11 和 0x2000 处的 8 个字节。
slli  rd=x12 rs1=x10 shamt=4       # 0xFF0
sub   rd=x13 rs1=x12 rs2=x11       # 0xFEF
lui   rd=x14 imm=2                 # 0x2000
ld    rd=x15 rs1=x14 imm=0         # 小端：0x8877665544332211
ecall
```

第一行 `# args:` 是运行这个测试时附加的参数，`--state` 指定初始状态文件。

## ③ 生成并核对期望输出

用参考模拟器生成期望输出：

```sh
python3 tools/encode.py build/isa/myrv tests/myrv/sum.prog work/sum-t.hex
build/myrv/xinyu-sim work/sum-t.hex > tests/myrv/sum.expected
python3 tools/encode.py build/isa/myrv tests/myrv/state.prog work/state.hex
build/myrv/xinyu-sim --state tests/myrv/start.state work/state.hex > tests/myrv/state.expected
```

`tests/myrv/state.expected` 应该是：

```text
steps 5
PC 0x0000000000000014
reg x10 0x00000000000000FF
reg x11 0x0000000000000001
reg x12 0x0000000000000FF0
reg x13 0x0000000000000FEF
reg x14 0x0000000000002000
reg x15 0x8877665544332211
mem M 0x0000000000002000 0x1122334455667788
```

::: warning 重要
生成之后要**逐行核对**期望输出是否符合你对指令的理解。期望是模拟器自己算出来的：经过你核对，定向测试才是在检查语义；不核对，它只能保证以后的改动不改变行为。
:::

## ④ 登记并运行

然后在 `mk/myrv.mk` 里登记测试目录：

```make
SIM_TESTS := tests/myrv
STATE_TESTS := state
```

- `SIM_TESTS`：测试目录，每个 `NAME.prog` 都要有 `NAME.expected`；
- `STATE_TESTS`：这些程序还要做一次往返检查——把运行结束的 dump 当作初始状态装回去，跑 0 步，结果必须与原 dump 一字不差。

```sh
make ARCH=myrv sim-test rsim-test
```

```text
pass tests/myrv/state
pass tests/myrv/sum
pass state round trip (sail)
…
pass tests/myrv/state (rust)
pass tests/myrv/sum (rust)
…
pass state round trip (rust)
pass batch of 2 cases (ISA myrv): output equals the single runs, --threads 1 and 4 agree, an invalid launch exits 2
```

有测试不通过时，会打印期望与实际的 `diff -u`，命令以 `Error 1` 结束。
