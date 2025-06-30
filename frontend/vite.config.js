import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/tiles': {
        target: 'https://noise-map.com',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/tiles/),
        rewrite: (p) => {
          // console.log('Original proxy URL:', p)
          const newPath = p.replace(/^\tiles/, '')
          // const finalUrl = `http://localhost:3737${newPath}`
          // console.log('Final proxy URL:', finalUrl)
          return newPath
        },
      },
    },
  },
  plugins: [vue()],
})
