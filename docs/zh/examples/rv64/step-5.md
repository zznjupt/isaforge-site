# 第 5 步：随机差分

> **目标**：用大量随机程序确认两个模拟器的行为完全一致。

## ① 运行

```sh
make ARCH=myrv fuzz
```

ISAForge 按你的 ISA 包随机生成 300 个程序和随机初始状态（寄存器和一段内存），分别在两个模拟器上运行并比较输出。约一分半钟：

```text
300 programs agree (24694 warp instructions); 45319 generated words, 0 undecodable; runs ended by: exited 141, step limit 127, illegal instruction 32
hit fraction 135/300 cases store into generated memory (45%), 173/4800 ranges changed; 300/300 programs execute a memory access
```

## ② 读懂输出

| 片段 | 含义 |
|---|---|
| `300 programs agree` | 两个模拟器的输出逐字一致 |
| `runs ended by` | 程序怎么结束的。`illegal instruction` 来自随机跳到不对齐地址的分支，属于正常情况 |
| `hit fraction` | 多少用例的 store 改写了随机内存 |

- 不一致时，工具保留用例并打印复现命令；
- `FUZZ_COUNT` 改用例数，`FUZZ_SEED` 改随机种子。

::: danger 小心
**随机差分证明不了语义是对的。** 两个模拟器从同一份 XML 生成，它们一致只说明 ISAForge 把你的语义忠实地生成成了两份实现。语义本身写错时，两份会一起错，随机差分查不出来。语义对不对，要靠定向测试（第 4 步）、等价性检查（第 8 步）和外部参考（第 9 步）。
:::
