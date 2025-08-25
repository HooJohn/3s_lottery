import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'

  return {
    plugins: [
      react()
    ],
    
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@/components': path.resolve(__dirname, './src/components'),
        '@/pages': path.resolve(__dirname, './src/pages'),
        '@/hooks': path.resolve(__dirname, './src/hooks'),
        '@/utils': path.resolve(__dirname, './src/utils'),
        '@/store': path.resolve(__dirname, './src/store'),
        '@/types': path.resolve(__dirname, './src/types'),
        '@/assets': path.resolve(__dirname, './src/assets'),
        '@/locales': path.resolve(__dirname, './src/locales'),
      },
    },
    
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    
    build: {
      outDir: 'dist',
      sourcemap: !isProduction,
      minify: isProduction ? 'terser' : false,
      target: 'es2015',
      cssCodeSplit: true,
      
      // Terser配置
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info'],
        },
        mangle: {
          safari10: true,
        },
      } : {},
      
      rollupOptions: {
        output: {
          // 更细粒度的代码分割
          manualChunks: (id) => {
            // 第三方库分割
            if (id.includes('node_modules')) {
              // React相关
              if (id.includes('react') || id.includes('react-dom')) {
                return 'react-vendor'
              }
              // 路由相关
              if (id.includes('react-router')) {
                return 'router-vendor'
              }
              // 状态管理
              if (id.includes('redux') || id.includes('@reduxjs')) {
                return 'state-vendor'
              }
              // 国际化
              if (id.includes('i18next') || id.includes('react-i18next')) {
                return 'i18n-vendor'
              }
              // UI和动画
              if (id.includes('framer-motion') || id.includes('lucide-react')) {
                return 'ui-vendor'
              }
              // 图表库
              if (id.includes('chart.js') || id.includes('react-chartjs')) {
                return 'charts-vendor'
              }
              // 工具库
              if (id.includes('lodash') || id.includes('date-fns') || id.includes('axios')) {
                return 'utils-vendor'
              }
              // 其他第三方库
              return 'vendor'
            }
            
            // 页面级别分割
            if (id.includes('/pages/auth/')) {
              return 'auth-pages'
            }
            if (id.includes('/pages/games/')) {
              return 'games-pages'
            }
            if (id.includes('/pages/wallet/')) {
              return 'wallet-pages'
            }
            if (id.includes('/pages/rewards/')) {
              return 'rewards-pages'
            }
            
            // 组件分割
            if (id.includes('/components/ui/')) {
              return 'ui-components'
            }
            if (id.includes('/components/games/')) {
              return 'games-components'
            }
          },
          
          // 文件命名策略
          chunkFileNames: (chunkInfo) => {
            const facadeModuleId = chunkInfo.facadeModuleId
            if (facadeModuleId) {
              if (facadeModuleId.includes('pages')) {
                return 'pages/[name]-[hash].js'
              }
              if (facadeModuleId.includes('components')) {
                return 'components/[name]-[hash].js'
              }
            }
            return 'chunks/[name]-[hash].js'
          },
          entryFileNames: 'js/[name]-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.')
            const ext = info[info.length - 1]
            if (/\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/i.test(assetInfo.name)) {
              return `media/[name]-[hash].${ext}`
            }
            if (/\.(png|jpe?g|gif|svg|webp|avif)(\?.*)?$/i.test(assetInfo.name)) {
              return `images/[name]-[hash].${ext}`
            }
            if (/\.(woff2?|eot|ttf|otf)(\?.*)?$/i.test(assetInfo.name)) {
              return `fonts/[name]-[hash].${ext}`
            }
            return `assets/[name]-[hash].${ext}`
          }
        },
      },
    },
    
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@reduxjs/toolkit',
        'react-redux',
        'react-i18next',
        'i18next',
        'framer-motion',
        'lucide-react',
        'date-fns',
        'lodash-es'
      ],
      exclude: ['@vite/client', '@vite/env'],
    },
    
    // 预构建配置
    esbuild: {
      drop: isProduction ? ['console', 'debugger'] : [],
      legalComments: 'none',
    },
    
    // CSS配置
    css: {
      devSourcemap: !isProduction,
    },
    
    // 定义全局常量
    define: {
      __DEV__: !isProduction,
      __PROD__: isProduction,
      __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    }
  }
})