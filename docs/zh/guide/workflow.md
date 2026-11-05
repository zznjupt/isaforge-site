# 边写边看

写 ISA 包时，要尽快知道刚写的东西对不对、长什么样。ISAForge 把这件事放在编辑器、终端和浏览器里。

## 编辑器

```sh
make editor
```

它在本地写好 VS Code 的设置，推荐安装 Red Hat 的 XML 插件。之后编辑 ISA 包里的文件时：

- 元素和属性自动补全，鼠标悬停显示中文说明；
- 写错的元素、属性和取值当场标红；
- 已有的 VS Code 设置保留，只补上缺的几项。

IntelliJ 系列在 Schemas and DTDs 里把 `urn:xinyu:isa:1` 映射到 `schema/isa.xsd`；其他编辑器指向 `schema/catalog.xml`。

## 保存即检查

```sh
make ARCH=myrv watch
```

```text
preview: http://127.0.0.1:8000/   assembler: http://127.0.0.1:8000/__asm/
watching isa/myrv (Ctrl-C to stop)
[10:20:31] check passed, documentation updated (1.1 s)
```

每次保存 ISA 包里的文件，它都会：

- 重建并检查这个 ISA 包，只跑它自己的检查；
- 检查通过：重新生成手册，浏览器里的预览页自动刷新；
- 检查不通过：终端和预览页顶部显示报错，路径指向你编辑的源文件，手册停在上一次通过的版本。

汇编器自己的检查放在手册更新之后、在后台跑，只查你改到的指令。B300 的 SASS 这样上千种编码的 ISA 包，手册约 18 秒更新，预览页顶部显示后台正在跑哪一步；改动是按文件内容判断的，编辑器的临时文件不会触发检查。

## 汇编与反汇编

预览页顶栏的「汇编/反汇编」是一个浏览器里的汇编器，用的是最近一次通过检查的构建：

<div class="forge-figure">

[![汇编与反汇编页：左边逐行汇编并画出每个字段的位，右边是指令速查](/screens/asm-page.png){.light-only}](/screens/asm-page.png)
[![汇编与反汇编页，深色模式](/screens/asm-page-dark.png){.dark-only}](/screens/asm-page-dark.png)

</div>

- 每行一条汇编，边输入边出机器码，每个字段的位按手册的颜色画出来；
- 切到“机器码 → 汇编”粘贴指令字，可以直接粘贴反汇编或 objdump 的输出；
- **不记得怎么写**：右边的指令速查按助记符或说明搜索，列出每种写法、每个操作数能取什么，以及一条点“插入”就能用的例子。例子由模板填入简单的值生成，再交给汇编器验证，换一个 ISA 包也不用手写；
- **写错了**：认出指令但操作数不对时，给出它的正确写法，点“换成这个”直接替换；拼错助记符时，给出拼写相近的指令；
- 手册里每个 form 旁边有“试一试”，点开就是填好这个例子的页面；页面地址可以发给别人。

## 手册

<div class="forge-figure">

[![B300 SASS 的 IMAD 手册页：form 一览矩阵和编码图](/screens/manual-imad.png){.light-only}](/screens/manual-imad.png)
[![B300 SASS 的 IMAD 手册页，深色模式](/screens/manual-imad-dark.png){.dark-only}](/screens/manual-imad-dark.png)

</div>

B300 SASS 的 IMAD 有 52 个 form。手册先把它们排成“变体 × 操作数组合”的矩阵，哪些写了语义一眼可见；每个 form 的编码图用三种颜色分开固定位、操作数和编码表，字段表与操作数表并排。
