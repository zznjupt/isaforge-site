---
layout: home

hero:
  name: ISAForge
  text: Write the ISA once, get the whole toolchain
  tagline: Describe an instruction set in XML and Sail, and get its assembler, disassembler, two functional simulators and manual, checked piece by piece against real tools and hardware.
  image:
    light: /logo.svg
    dark: /logo-dark.svg
    alt: ISAForge
  actions:
    - theme: brand
      text: Get started
      link: /guide/getting-started
    - theme: alt
      text: RV64I from scratch
      link: /examples/rv64/

features:
  - icon: { light: /icons/spec.svg, dark: /icons/spec-dark.svg, width: 44, height: 44 }
    title: One specification, consistent everywhere
    details: Encodings, operands, legality and assembly syntax in XML, semantics in Sail. The decoder, assembler, disassembler, both simulators and the manual are all made from it, so a change made once is made everywhere.
  - icon: { light: /icons/twin.svg, dark: /icons/twin-dark.svg, width: 44, height: 44 }
    title: Two simulators that check each other
    details: The C that Sail compiles is the reference; the generated Rust is 170 times as fast on one thread. Every ISA package runs random programs on both and compares registers, memory and how each run ended.
  - icon: { light: /icons/proof.svg, dark: /icons/proof-dark.svg, width: 44, height: 44 }
    title: Proved, not only tested
    details: Declare a new instruction equivalent to a sequence of base ones; besides random comparison, z3 proves it holds for every input, and when it does not, gives the operands and initial values that tell them apart.
  - icon: { light: /icons/reference.svg, dark: /icons/reference-dark.svg, width: 44, height: 44 }
    title: Checked against the real thing
    details: Disassembly is compared word for word with nvdisasm and llvm-mc, execution with Spike and GPU hardware. Coverage reports name the encodings, field values and branches no test reached.
  - icon: { light: /icons/write.svg, dark: /icons/write-dark.svg, width: 44, height: 44 }
    title: Checked as you write
    details: Completion and documentation in the editor; every save checked and the manual refreshed; two clashing encodings compared field by field with a fix; assembly to machine code as you type in the browser.
  - icon: { light: /icons/arch.svg, dark: /icons/arch-dark.svg, width: 44, height: 44 }
    title: From CPUs to GPUs
    details: The same tool describes scalar CPUs and SIMT GPUs alike, with lanes, predicated execution and warp launch built in. NPUs and other kinds of processor are next.
---

<div class="forge-results">

## B300 SASS, word for word

<div class="forge-stats">
  <div class="forge-stat"><div class="value">12189 / 12189</div><div class="label">B300 SASS instruction words disassembled exactly as NVIDIA's nvdisasm prints them</div></div>
  <div class="forge-stat"><div class="value">4457 / 4457</div><div class="label">instruction combinations with the same results on a B300 and in the model</div></div>
  <div class="forge-stat"><div class="value">614×</div><div class="label">as fast as the Sail reference model: the generated Rust model, running multithreaded</div></div>
</div>

NVIDIA's B300 SASS has no public specification, only binaries and a disassembler. With ISAForge we imported its 259 instructions and 1368 encodings from an open-source description, then corrected them one by one and added their semantics: the disassembly matches nvdisasm word for word, the instructions with semantics agree between the two models on random programs, and 61 instruction families agree with a B300, input by input.

**CPUs and GPUs, one tool:**

| Instruction set | Processor | Size | Disassembly | Execution |
|---|---|---|---|---|
| RISC-V RV64I, M, Zba | scalar CPU | 72 encodings | as llvm-mc: 4441 / 4441 | as Spike, to the byte |
| NVIDIA B300 SASS | SIMT GPU | 259 instructions, 1368 encodings | as nvdisasm: 12189 / 12189 | as the hardware: 4457 / 4457 combinations |

Want to try it yourself? [RV64I from scratch](/examples/rv64/): ten steps to 13 instructions, verified all the way to agreeing with LLVM and Spike.

</div>
