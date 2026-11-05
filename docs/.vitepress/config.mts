import { defineConfig, type DefaultTheme } from 'vitepress'

// Served from GitHub Pages under /isaforge-site/.
const base = '/isaforge-site/'

const STEPS_EN = [
  'The skeleton and a first instruction', 'Running a program', 'The common instructions', 'Directed tests',
  'Differential testing', 'Extensions and feature switches', 'Aliases', 'A custom instruction and its equivalence',
  'Checking against external references', 'Coverage and the manual'
]
const STEPS_ZH = [
  '骨架和第一条指令', '让程序跑起来', '补齐常用指令', '定向测试', '随机差分',
  '扩展与特性开关', '别名', '自定义指令与等价性', '对照外部参考', '覆盖率与手册'
]

function sidebar(zh: boolean): DefaultTheme.SidebarItem[] {
  const p = zh ? '/zh' : ''
  const steps = zh ? STEPS_ZH : STEPS_EN
  return [
    {
      text: zh ? '用法' : 'Guide',
      items: [
        { text: zh ? 'ISAForge 是什么' : 'What is ISAForge', link: `${p}/guide/introduction` },
        { text: zh ? '快速开始' : 'Getting started', link: `${p}/guide/getting-started` },
        { text: zh ? '写一个 ISA 包' : 'Writing an ISA package', link: `${p}/guide/package` },
        { text: zh ? '生成什么' : 'What is generated', link: `${p}/guide/generated` },
        { text: zh ? '验证' : 'Verification', link: `${p}/guide/verification` },
        { text: zh ? '边写边看' : 'Write and see', link: `${p}/guide/workflow` }
      ]
    },
    {
      text: zh ? '示例：从零写一个 RV64I' : 'Example: RV64I from scratch',
      items: [
        { text: zh ? '概览' : 'Overview', link: `${p}/examples/rv64/` },
        ...steps.map((s, i) => ({ text: `${i + 1}. ${s}`, link: `${p}/examples/rv64/step-${i + 1}` })),
        { text: zh ? '常见报错与命令速查' : 'Errors and commands', link: `${p}/examples/rv64/reference` }
      ]
    }
  ]
}

export default defineConfig({
  base,
  title: 'ISAForge',
  cleanUrls: true,
  lastUpdated: true,
  // Sail's let, if, match and foreach read like OCaml; the block keeps its sail label.
  markdown: { languageAlias: { sail: 'ocaml' } },
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}logo.svg` }]],
  themeConfig: {
    logo: { light: '/logo.svg', dark: '/logo-dark.svg' },
    search: {
      provider: 'local',
      options: {
        locales: {
          zh: {
            translations: {
              button: { buttonText: '搜索', buttonAriaLabel: '搜索' },
              modal: {
                noResultsText: '没有结果',
                resetButtonTitle: '清除',
                footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
              }
            }
          }
        }
      }
    }
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en',
      description: 'ISAForge: write an instruction set once, and get its toolchain, simulators, manual and verification.',
      themeConfig: {
        nav: [
          { text: 'Guide', link: '/guide/introduction', activeMatch: '/guide/' },
          { text: 'Example', link: '/examples/rv64/', activeMatch: '/examples/' }
        ],
        sidebar: { '/guide/': sidebar(false), '/examples/': sidebar(false) },
        footer: { copyright: 'Copyright © 2026 the ISAForge authors' }
      }
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      link: '/zh/',
      description: 'ISAForge：写一次指令集，生成整套工具链、模拟器和手册，并逐项验证。',
      themeConfig: {
        nav: [
          { text: '用法', link: '/zh/guide/introduction', activeMatch: '/zh/guide/' },
          { text: '示例', link: '/zh/examples/rv64/', activeMatch: '/zh/examples/' }
        ],
        sidebar: { '/zh/guide/': sidebar(true), '/zh/examples/': sidebar(true) },
        footer: { copyright: 'Copyright © 2026 ISAForge 作者' },
        outline: { label: '本页目录' },
        docFooter: { prev: '上一页', next: '下一页' },
        lastUpdated: { text: '最后更新' },
        darkModeSwitchLabel: '深色模式',
        lightModeSwitchTitle: '切换到浅色模式',
        darkModeSwitchTitle: '切换到深色模式',
        sidebarMenuLabel: '目录',
        returnToTopLabel: '回到顶部',
        langMenuLabel: '语言'
      }
    }
  }
})
