# Step 4: Directed tests

> **Goal**: fix programs and their expected output, so every later change is checked again on both simulators.

Testing and verification have several layers, each answering a different question. Steps 4 to 10 use them one by one:

<div class="forge-figure">

![What each layer of verification compares and what it finds](/tutorial/verification-en.svg){.light-only}
![What each layer of verification compares and what it finds](/tutorial/verification-en-dark.svg){.dark-only}

</div>

## ① Write a test program

Test programs use the `.prog` format: each line gives a form id and field values, without going through assembly syntax.

Create `tests/myrv/sum.prog`:

```text
# 1 + 2 + ... + 10, stored to memory at 0x1000 and read back.
addi  rd=x1 rs1=x0 imm=10
addi  rd=x2 rs1=x0 imm=0
add   rd=x2 rs1=x2 rs2=x1          # loop body: sum += n
addi  rd=x1 rs1=x1 imm=-1          # n -= 1
bne   rs1=x1 rs2=x0 imm=-8         # back to the loop body while n != 0 (8 bytes back)
lui   rd=x5 imm=1                  # x5 = 0x1000
sd    rs1=x5 rs2=x2 imm=0
ld    rd=x6 rs1=x5 imm=0
ecall
```

- Everything after `#` is a comment;
- The program starts from an all-zero initial state.

## ② Write a test with an initial state

The second test reads the initial values of registers and memory from a state file. A state file has the same format as a dump. Create `tests/myrv/start.state`:

```text
PC 0x0000000000000000
reg x10 0x00000000000000FF
reg x11 0x0000000000000001
mem M 0x0000000000002000 0x1122334455667788
```

The first byte of a `mem` line goes at the lowest address, so the little-endian 8-byte value read from 0x2000 is 0x8877665544332211. Then create `tests/myrv/state.prog`:

```text
# args: --state tests/myrv/start.state
# x10, x11 and the 8 bytes at 0x2000 come from the state file.
slli  rd=x12 rs1=x10 shamt=4       # 0xFF0
sub   rd=x13 rs1=x12 rs2=x11       # 0xFEF
lui   rd=x14 imm=2                 # 0x2000
ld    rd=x15 rs1=x14 imm=0         # little-endian: 0x8877665544332211
ecall
```

The first line, `# args:`, gives extra arguments for running this test; `--state` names the initial state file.

## ③ Generate and check the expected output

Generate the expected output with the reference simulator:

```sh
python3 tools/encode.py build/isa/myrv tests/myrv/sum.prog work/sum-t.hex
build/myrv/xinyu-sim work/sum-t.hex > tests/myrv/sum.expected
python3 tools/encode.py build/isa/myrv tests/myrv/state.prog work/state.hex
build/myrv/xinyu-sim --state tests/myrv/start.state work/state.hex > tests/myrv/state.expected
```

`tests/myrv/state.expected` should be:

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

::: warning Important
Once generated, **check the expected output line by line** against what you understand the instructions to do. The simulator computed it itself: checked by you, a directed test checks the semantics; unchecked, it only makes sure later changes do not change the behaviour.
:::

## ④ Register and run

Then register the test directory in `mk/myrv.mk`:

```make
SIM_TESTS := tests/myrv
STATE_TESTS := state
```

- `SIM_TESTS`: the test directory; each `NAME.prog` needs a `NAME.expected`;
- `STATE_TESTS`: these programs also get a round-trip check: the dump at the end of the run is loaded back as the initial state, run for 0 steps, and must equal the original dump exactly.

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

When a test fails, the expected and actual output are printed as a `diff -u`, and the command ends with `Error 1`.
