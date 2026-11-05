# Step 9: Checking against external references

> **Goal**: confirm that the description matches the real RV64I: encodings and syntax against llvm-mc, execution against Spike.

**Why external references too**

- The checks so far show that the description is consistent with itself, but it can still differ from the real ISA, for example with an encoding bit written wrong;
- RV64I has references ready to use: llvm-mc decides encodings and assembly syntax, Spike decides execution results;
- For your own ISA, an existing simulator, RTL or hardware can be the reference; with no reference at all, you rely on reviewed directed tests and equivalence checks.

## ① Add two targets to the mk file

Add these two targets to the end of `mk/myrv.mk` (the paths are Homebrew's default install locations):

```make
# External references (step 9): llvm-mc generates corpora, Spike compares execution.
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

## ② llvm-mc: encodings and syntax

`make corpus` generates a batch of instruction words for each form, has llvm-mc disassemble them, and saves the results as corpora:

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

| Comparison | Result | Meaning |
|---|---|---|
| Without aliases | 784/784 match | encodings and base syntax are the same as LLVM's |
| With aliases | 690/784 match | llvm-mc prints 94 words as aliases (`j`, `jal`, `bnez`, `beqz`, `neg` and others, from JAL, BNE, BEQ, SUB and ADD), which this tutorial does not declare |

This is how a reference comparison finds what a description is missing. To see how the aliases are written, look at BEQ, JAL, SUB and the other files in `isa/rv64/`, the full RV64 ISA package that comes with ISAForge.

Register the corpus without aliases in `mk/myrv.mk`. From then on, every `make ARCH=myrv check` compares the disassembly and checks the assembly round trip:

```make
CORPUS_NO_ALIASES := tests/corpus/myrv/no-aliases.tsv
ASM_CHECK := tests/corpus/myrv/no-aliases.tsv
```

The round-trip line is `784/784 exact, 0 same text, 0 not encodable, 0 with no text, 0 untexted  round-trip  no-aliases.tsv`: the text of every word in the corpus assembles back to the same word (`exact`). `same text` counts texts that assemble to a different word that prints the same (when one text has several encodings), `not encodable` those a legality condition rejects, and `with no text` texts the assembler cannot read.

## ③ Spike: execution results

Compare execution with Spike:

```sh
make ARCH=myrv FEATURES="I M" spike
```

```text
pass 2 directed programs: Spike = Sail = Rust
pass 300 random programs (36479 instructions), 0 redrawn after a Spike trap: Spike = Sail = Rust
hit fraction 298/300 generated memory ranges changed (99%)
```

On the two directed tests and 300 random programs, Spike, the Sail model and the Rust model agree exactly on registers, PC and memory. Directed tests without `--state` start from an all-zero state, as on the two models.

::: warning Important
**`FEATURES="I M"`**: Spike does not know the custom extension Xmy. The names of the enabled features make up Spike's `--isa` argument (here `rv64im`), so SH1ADD has to be left out; otherwise Spike traps as soon as a random program reaches it. The custom instruction is covered by the equivalence checks of step 8.
:::
