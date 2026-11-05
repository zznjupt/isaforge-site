import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import FlowDiagram from './FlowDiagram.vue'
import './custom.css'

// The home page shows how ISAForge works between its hero and its features.
export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'home-features-before': () => h(FlowDiagram)
  })
}
