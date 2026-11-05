---
layout: home

hero:
  name: ISAForge
  text: 写一次指令集，得到整套工具
  tagline: 用 XML 与 Sail 描述指令集，自动生成汇编器、反汇编器、两个功能模拟器和指令手册，并对照真实工具与硬件逐项验证。
  image:
    light: /logo.svg
    dark: /logo-dark.svg
    alt: ISAForge
  actions:
    - theme: brand
      text: 快速开始
      link: /zh/guide/getting-started
    - theme: alt
      text: 从零写一个 RV64I
      link: /zh/examples/rv64/

features:
  - icon: { light: /icons/spec.svg, dark: /icons/spec-dark.svg, width: 44, height: 44 }
    title: 一份规格，处处一致
    details: 编码、操作数、合法性和汇编语法写在 XML 里，语义写在 Sail 里。译码器、汇编器、反汇编器、两个模拟器和手册都从这一份生成，改一处，处处跟着变。
  - icon: { light: /icons/twin.svg, dark: /icons/twin-dark.svg, width: 44, height: 44 }
    title: 两个模拟器互为参照
    details: Sail 编出的 C 是参考实现，生成的 Rust 版本单线程就快 170 倍。每个 ISA 包都用随机程序比较两者的寄存器、内存和停机原因。
  - icon: { light: /icons/proof.svg, dark: /icons/proof-dark.svg, width: 44, height: 44 }
    title: 证明，而不只是测试
    details: 声明一条新指令等价于一段基础指令，随机比对之外，再用 z3 证明它对所有输入成立；不成立时给出反例的操作数和初值。
  - icon: { light: /icons/reference.svg, dark: /icons/reference-dark.svg, width: 44, height: 44 }
    title: 对照真实参考
    details: 反汇编逐字对照 nvdisasm 与 llvm-mc，执行对照 Spike 和 GPU 实机。覆盖率报告列出没有测到的编码、字段取值和分支。
  - icon: { light: /icons/write.svg, dark: /icons/write-dark.svg, width: 44, height: 44 }
    title: 写的时候就检查
    details: 编辑器里有补全和中文说明；保存即检查、刷新手册；两条指令编码冲突时逐字段对照并给出改法；浏览器里边写汇编边看机器码。
  - icon: { light: /icons/arch.svg, dark: /icons/arch-dark.svg, width: 44, height: 44 }
    title: 从 CPU 到 GPU
    details: 同一套工具既能描述标量 CPU，也能描述 SIMT GPU：lane、谓词执行和 warp 启动都是内置的概念。后续将支持 NPU 等更多类型的处理器。
---

<div class="forge-results">

## 逐字复现 B300 的 SASS

<div class="forge-stats">
  <div class="forge-stat"><div class="value">12189 / 12189</div><div class="label">个 B300 SASS 指令字，反汇编与 NVIDIA nvdisasm 逐字一致</div></div>
  <div class="forge-stat"><div class="value">4457 / 4457</div><div class="label">种指令组合在 B300 实机上与模型的执行结果一致</div></div>
  <div class="forge-stat"><div class="value">614×</div><div class="label">生成的 Rust 模型多线程运行，比 Sail 参考模型快的倍数</div></div>
</div>

NVIDIA B300 的 SASS 没有公开规格，只有二进制和反汇编器。用 ISAForge，我们从开源的指令描述导入它的 259 条指令、1368 种编码，再逐条修正、补上语义：反汇编与 nvdisasm 逐字一致；写了语义的指令在两个模型上随机比对全部一致；61 个指令族又在 B300 实机上逐个输入比对，结果全部相同。

**CPU 与 GPU，同一套工具：**

| 指令集 | 处理器 | 规模 | 反汇编 | 执行 |
|---|---|---|---|---|
| RISC-V RV64I、M、Zba | 标量 CPU | 72 种编码 | 与 llvm-mc 一致：4441 / 4441 | 与 Spike 逐字节一致 |
| NVIDIA B300 SASS | SIMT GPU | 259 条指令、1368 种编码 | 与 nvdisasm 一致：12189 / 12189 | 与实机一致：4457 / 4457 种组合 |

想亲手试一试？[从零写一个 RV64I](/zh/examples/rv64/)：十步写出 13 条指令，一路验证到和 LLVM、Spike 一致。

</div>
