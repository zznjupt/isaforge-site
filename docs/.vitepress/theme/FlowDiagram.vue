<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

// How ISAForge works, between the hero and the features of the home page:
// what you write, what is generated from it, how it is checked, and the
// loop that runs while you write. Blue is yours, teal generated, orange checked.
const TEXT = {
  zh: {
    title: '从一份规格到整套工具',
    lead: '你只写指令集本身；工具、模拟器和手册都从它生成，再一层层验证。',
    spec: {
      head: '写下 ISA', sub: '一个 ISA 包',
      items: [
        ['XML', '编码与操作数'],
        ['XML', '汇编语法与别名'],
        ['XML', '寄存器、扩展与执行模型'],
        ['Sail', '每条指令的语义']
      ],
      targets: '面向', chips: ['标量 CPU', 'SIMT GPU', 'NPU（即将支持）']
    },
    gen: {
      head: '自动生成', sub: '同一份规格，处处一致',
      items: ['译码器', '汇编器', '反汇编器', 'Sail 参考模型', 'Rust 快速模型', '指令手册']
    },
    check: {
      head: '逐项验证', sub: '每一层查前一层查不到的',
      items: [
        ['静态检查', '译码唯一，汇编无歧义'],
        ['随机差分', '两个模型互为参照'],
        ['等价性证明', 'z3 证明对所有输入成立'],
        ['对照参考', '反汇编器、ISA 模拟器、实机'],
        ['覆盖率', '没测到的一目了然']
      ]
    },
    loop: '边写边看', loopText: '编辑器补全与说明 · 保存即检查，手册自动刷新 · 浏览器里边写汇编边看机器码'
  },
  en: {
    title: 'From one specification to the whole toolchain',
    lead: 'You write the instruction set itself; the tools, simulators and manual are generated from it, then checked layer by layer.',
    spec: {
      head: 'Write the ISA', sub: 'one ISA package',
      items: [
        ['XML', 'Encodings and operands'],
        ['XML', 'Assembly syntax and aliases'],
        ['XML', 'Registers, extensions, execution model'],
        ['Sail', 'Semantics of every instruction']
      ],
      targets: 'For', chips: ['scalar CPUs', 'SIMT GPUs', 'NPUs (coming)']
    },
    gen: {
      head: 'Generate', sub: 'one specification, consistent everywhere',
      items: ['Decoder', 'Assembler', 'Disassembler', 'Sail reference model', 'Rust fast model', 'Instruction manual']
    },
    check: {
      head: 'Verify', sub: 'each layer finds what the last cannot',
      items: [
        ['Static check', 'unique decoding, unambiguous assembly'],
        ['Differential testing', 'two models check each other'],
        ['Equivalence proofs', 'z3 proves it for every input'],
        ['References', 'disassemblers, ISA simulators, hardware'],
        ['Coverage', 'what no test reached, at a glance']
      ]
    },
    loop: 'Write and see', loopText: 'completion and documentation in the editor · every save checked, the manual refreshed · assembly to machine code in the browser as you type'
  }
}

const { lang } = useData()
const t = computed(() => (lang.value.startsWith('zh') ? TEXT.zh : TEXT.en))
</script>

<template>
  <section class="forge-flow" aria-labelledby="forge-flow-title">
    <div class="container">
      <h2 id="forge-flow-title" class="title">{{ t.title }}</h2>
      <p class="lead">{{ t.lead }}</p>
      <div class="grid">
        <div class="stage spec">
          <div class="head"><span class="num">1</span>{{ t.spec.head }}</div>
          <div class="sub">{{ t.spec.sub }}</div>
          <ul class="rows">
            <li v-for="[tag, text] in t.spec.items" :key="text"><span class="tag">{{ tag }}</span>{{ text }}</li>
          </ul>
          <div class="targets">
            <span class="label">{{ t.spec.targets }}</span>
            <span v-for="(c, i) in t.spec.chips" :key="c" class="chip" :class="{ soon: i === 2 }">{{ c }}</span>
          </div>
        </div>
        <div class="arrow" aria-hidden="true">
          <svg viewBox="0 0 40 24"><path d="M2 12 H34 M26 4 L35 12 L26 20" /></svg>
        </div>
        <div class="stage gen">
          <div class="head"><span class="num">2</span>{{ t.gen.head }}</div>
          <div class="sub">{{ t.gen.sub }}</div>
          <ul class="tools">
            <li v-for="item in t.gen.items" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="arrow" aria-hidden="true">
          <svg viewBox="0 0 40 24"><path d="M2 12 H34 M26 4 L35 12 L26 20" /></svg>
        </div>
        <div class="stage check">
          <div class="head"><span class="num">3</span>{{ t.check.head }}</div>
          <div class="sub">{{ t.check.sub }}</div>
          <ul class="rows">
            <li v-for="[name, text] in t.check.items" :key="name"><b>{{ name }}</b><span>{{ text }}</span></li>
          </ul>
        </div>
      </div>
      <div class="loop">
        <svg class="loop-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 12a8 8 0 1 1-2.6-5.9M20 4v5h-5" /></svg>
        <b>{{ t.loop }}</b>
        <span>{{ t.loopText }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.forge-flow {
  padding: 8px 24px 48px;
}
@media (min-width: 640px) {
  .forge-flow { padding: 8px 48px 56px; }
}
@media (min-width: 960px) {
  .forge-flow { padding: 8px 64px 64px; }
}
.container { max-width: 1152px; margin: 0 auto; }
.title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--vp-c-text-1);
}
.lead {
  margin: 6px 0 22px;
  font-size: 15px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}
@media (min-width: 960px) {
  .grid { grid-template-columns: 1fr 40px 1fr 40px 1.15fr; gap: 0; align-items: stretch; }
}

.stage {
  --c: var(--vp-c-brand-1);
  position: relative;
  border-radius: 12px;
  padding: 18px 20px 20px;
  background: var(--vp-c-bg-soft);
  border-top: 3px solid var(--c);
}
.stage.gen { --c: var(--forge-teal); }
.stage.check { --c: var(--forge-orange); }
.head {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}
.num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--c);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}
.dark .stage.spec .num { color: #1b1b1f; }
.sub {
  margin: 4px 0 14px 34px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}
ul { list-style: none; margin: 0; padding: 0; }
.rows li {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 7px 0;
  font-size: 14px;
  line-height: 1.5;
  color: var(--vp-c-text-1);
  border-top: 1px solid var(--vp-c-divider);
}
.rows li:first-child { border-top: none; }
.tag {
  flex: none;
  min-width: 38px;
  padding: 0 6px;
  border-radius: 6px;
  font-family: var(--vp-font-family-mono);
  font-size: 11px;
  line-height: 20px;
  text-align: center;
  color: var(--c);
  background: var(--vp-c-bg);
  border: 1px solid var(--c);
}
.check .rows li { flex-direction: column; gap: 0; }
.check .rows b { font-weight: 600; }
.check .rows span { font-size: 13px; color: var(--vp-c-text-2); }
.check .rows li b::before {
  content: "";
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 8px;
  border-radius: 50%;
  background: var(--c);
  vertical-align: 2px;
}
.check .rows span { padding-left: 15px; }

.tools {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.tools li {
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-left: 3px solid var(--c);
}

.targets {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--vp-c-divider);
  font-size: 12px;
}
.targets .label { color: var(--vp-c-text-2); margin-right: 2px; }
.chip {
  padding: 1px 10px;
  border-radius: 999px;
  line-height: 20px;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
}
.chip.soon { color: var(--vp-c-text-2); border-style: dashed; }

.arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 28px;
  color: var(--vp-c-text-3);
}
.arrow svg {
  width: 30px;
  height: 18px;
  transform: rotate(90deg);
  fill: none;
  stroke: currentColor;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-linejoin: round;
}
@media (min-width: 960px) {
  .arrow { height: auto; }
  .arrow svg { transform: none; }
}

.loop {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 12px;
  margin-top: 14px;
  padding: 12px 18px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  font-size: 14px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
}
.loop b { color: var(--vp-c-text-1); font-weight: 600; }
.loop-icon {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: var(--vp-c-brand-1);
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
