import { utimesSync } from 'node:fs'
import { resolve } from 'node:path'
import { defineConfig } from 'vite'

// Code slides import agent/*.py through the `agent` symlink. Vite doesn't watch
// files outside the deck, so touch slides.md when one changes.
const agentDir = resolve(__dirname, '../agent')
const slides = resolve(__dirname, 'slides.md')

export default defineConfig({
  plugins: [{
    name: 'watch-agent-sources',
    configureServer(server) {
      server.watcher.add(agentDir)
      server.watcher.on('change', (file) => {
        if (file.startsWith(agentDir)) utimesSync(slides, new Date(), new Date())
      })
    },
  }],
})
