# 第 9 步：对照外部参考

> **目标**：确认描述和真正的 RV64I 一致：编码和语法对照 llvm-mc，执行结果对照 Spike。

**为什么还要外部参考**

- 前面的检查保证描述自洽，但描述可能和真正的 ISA 不一致，比如把某个编码位写错了；
- RV64I 有现成的参考：llvm-mc 判断编码和汇编语法，Spike 判断执行结果；
- 你自己的 ISA 可以用已有的模拟器、RTL 或者硬件当参考；完全没有参考时，就靠核对过的定向测试和等价性检查。

## ① 在 mk 里加两个目标

把下面两个目标加到 `mk/myrv.mk` 末尾（路径是 Homebrew 的默认安装位置）：

```make
# 外部参考（第 9 步）：llvm-mc 生成语料，Spike 比对执行。
LLVMMC ?= /opt/homebrew/opt/llvm/bin/llvm-mc
LLVMNM ?= /opt/homebrew/opt/llvm/bin/llvm-nm
LDLLD ?= /opt/homebrew/opt/lld/bin/ld.lld
SPIKE ?= spike
SPIKE_COUNT ?= 300

.PHONY: corpus spike
corpus: $(ISA)/arch.xml
	python3 tools/llvmprint.py $(ISA) $(LLVMMC) tests/corpus/myrv

spike: $(ISA)/arch.xml $(SIM) rsim
	SPIKE=$(SPIKE) LLVMMC=$(LLVMMC) LDLLD=$(LDLLD) LLVMNM=$(LLVMNM) \
		python3 tools/spikeprint.py $(ISA) build/spike-myrv $(SPIKE_COUNT) $(FUZZ_SEED) \
		$(SIM) $(RSIM) $(SIM_TESTS)
```

## ② llvm-mc：对照编码和语法

`make corpus` 为每个 form 生成一批指令字，让 llvm-mc 反汇编，把结果存成语料：

```sh
make ARCH=myrv corpus
python3 tools/disasm.py --no-aliases build/isa/myrv tests/corpus/myrv/no-aliases.tsv
python3 tools/disasm.py build/isa/myrv tests/corpus/myrv/aliases.tsv
```

```text
aliases.tsv: 784 printed, 0 rejected
no-aliases.tsv: 784 printed, 0 rejected
asm-only.tsv: 0 assembled
784/784 words print exactly as the corpus
   34 jal
        want j 131072
        got  jal x0, 131072
        want jal 4
        got  jal x1, 4
   24 bne
        want bnez x0, 2048
        got  bne x0, x0, 2048
…
690/784 words print exactly as the corpus
```

| 比对 | 结果 | 说明 |
|---|---|---|
| 不带别名 | 784/784 一致 | 编码和基础语法都与 LLVM 相同 |
| 带别名 | 690/784 一致 | llvm-mc 会把 94 个字打印成别名（`j`、`jal`、`bnez`、`beqz`、`neg` 等，分属 JAL、BNE、BEQ、SUB、ADD），本教程没有声明这些别名 |

参考比对就是这样发现描述缺了什么。补齐别名的写法，可以参考 ISAForge 自带的完整 RV64 ISA 包 `isa/rv64/` 里的 BEQ、JAL、SUB 等文件。

把不带别名的语料登记进 `mk/myrv.mk`，以后每次 `make ARCH=myrv check` 都会比对反汇编，并检查汇编往返：

```make
CORPUS_NO_ALIASES := tests/corpus/myrv/no-aliases.tsv
ASM_CHECK := tests/corpus/myrv/no-aliases.tsv
```

汇编往返那一行是 `784/784 exact, 0 same text, 0 not encodable, 0 with no text, 0 untexted  round-trip  no-aliases.tsv`：语料里每个字的文本都汇编回同一个字（`exact`）；`same text` 是汇编成另一个但打印相同的字（同一文本有多种编码时），`not encodable` 是合法性条件拒绝的，`with no text` 是汇编器读不懂的文本。

## ③ Spike：对照执行结果

和 Spike 比对执行：

```sh
make ARCH=myrv FEATURES="I M" spike
```

```text
pass 2 directed programs: Spike = Sail = Rust
pass 300 random programs (36479 instructions), 0 redrawn after a Spike trap: Spike = Sail = Rust
hit fraction 298/300 generated memory ranges changed (99%)
```

两个定向测试和 300 个随机程序在 Spike、Sail 模拟器、Rust 模拟器上的寄存器、PC 和内存完全一致。没写 `--state` 的定向测试从全零状态开始，与两个模拟器相同。

::: warning 重要
**`FEATURES="I M"`**：Spike 不认识自定义扩展 Xmy。启用的特性名会拼成 Spike 的 `--isa` 参数（这里是 `rv64im`），所以要把 SH1ADD 排除在外，否则随机程序一碰到它 Spike 就陷入。自定义指令由第 8 步的等价性检查负责。
:::
