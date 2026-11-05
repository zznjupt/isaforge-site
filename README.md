# ISAForge 网站

ISAForge 的产品网站，用 VitePress 搭建。英文在根目录，中文在 `/zh/`。

```sh
npm install
npm run docs:dev        # 本地预览，改了即刷新
npm run docs:build      # 生成静态站点到 docs/.vitepress/dist
npm run docs:preview    # 预览构建结果
```

站点在 https://zznjupt.github.io/isaforge-site/ 。推到 `main` 后，GitHub Actions（`.github/workflows/deploy.yml`）自动构建并发布到 GitHub Pages；路径前缀 `/isaforge-site/` 是 `docs/.vitepress/config.mts` 的 `base`，要和仓库名一致。

## 页面

| 位置 | 内容 |
|---|---|
| `docs/index.md` | 首页：功能、流程图、B300 SASS 的结果 |
| `docs/guide/` | 用法：是什么、快速开始、写一个 ISA 包、生成什么、验证、边写边看 |
| `docs/examples/rv64/` | 示例：从零写一个 RV64I，概览、十步、常见报错与命令速查 |

中文页面在 `docs/zh/` 下一一对应。首页的流程图是组件 `docs/.vitepress/theme/FlowDiagram.vue`（中英文本都在里面），配色变量在 `custom.css`。

## 图

- `docs/public/logo.svg`、`docs/public/icons/`：标志和功能图标，各有深色版；
- `docs/public/screens/`：工具截图，各有深色版，已裁掉工具自己的顶栏；
- `docs/public/tutorial/`：教程里的示意图，由 `scripts/diagrams.py` 生成，每张图有中英文、浅色和深色四个版本。改了图就重新运行：

  ```sh
  python3 scripts/diagrams.py
  ```

## 与工具的教程保持一致

示例是 ISAForge 自带教程（工具仓库的 `docs/tutorial/README.md`）的网站版。网站版是自包含的：答案文件直接写在页面里，链接都指向网站自己的用法页，不指向仓库。

- 教程改了，把改动手工同步到 `docs/zh/examples/rv64/`，再同步英文页；
- 要从头重新切分，运行 `python3 scripts/split_tutorial.py <教程 README> docs/zh/examples/rv64`。它会覆盖手工改过的页面，只在重做时用；
- 页面里的命令输出和数字以工具的实际运行为准，更新时一并核对。

## 写作约定

- 产品名是 ISAForge，它是一套工具，不称“语言”或“框架”；用户写的那份规格叫“ISA 包”（ISA package）；
- 页面上不出现工程细节：测量日期、机器型号、测试文件路径、提交号；
- 不链接到私有仓库；网站保持独立，不引用其他子项目。
