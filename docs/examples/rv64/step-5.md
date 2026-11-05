# Step 5: Differential testing

> **Goal**: confirm with many random programs that the two simulators behave exactly alike.

## ① Run

```sh
make ARCH=myrv fuzz
```

ISAForge generates 300 random programs from your ISA package, each with a random initial state (registers and a stretch of memory), runs them on both simulators and compares the output. It takes about a minute and a half:

```text
300 programs agree (24694 warp instructions); 45319 generated words, 0 undecodable; runs ended by: exited 141, step limit 127, illegal instruction 32
hit fraction 135/300 cases store into generated memory (45%), 173/4800 ranges changed; 300/300 programs execute a memory access
```

## ② Read the output

| Part | Meaning |
|---|---|
| `300 programs agree` | the two simulators printed exactly the same |
| `runs ended by` | how the programs ended. `illegal instruction` comes from branches that jump at random to misaligned addresses, and is expected |
| `hit fraction` | how many cases had a store change the random memory |

- When they disagree, the tool keeps the case and prints the command to reproduce it;
- `FUZZ_COUNT` changes the number of cases, `FUZZ_SEED` the random seed.

::: danger Caution
**Differential testing cannot prove the semantics right.** The two simulators are generated from the same XML, so their agreeing shows only that ISAForge turned your semantics faithfully into two implementations. Semantics written wrong are wrong in both, and differential testing cannot find it. Whether the semantics are right is for directed tests (step 4), equivalence checks (step 8) and external references (step 9) to show.
:::
