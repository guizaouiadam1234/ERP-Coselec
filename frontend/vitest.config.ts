import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'


export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      alias: {
        '/logo_coselec.jfif': 'c:/Users/adam.guizaoui/Desktop/ERP/frontend/public/logo_coselec.jfif'
      }
    },
  }),
)

