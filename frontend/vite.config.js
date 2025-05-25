// vite.config.js
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: './public',  // 將根目錄設定為 public 資料夾
  publicDir: '',    // 因為已經在 public 目錄中，所以不需要另外的 public 目錄
  server: {
    port: 8000,
    open: true
  },
  resolve: {
    alias: {
      // 讓 src 目錄可以被正確引用
      '/src': resolve(__dirname, './src'),
      '@': resolve(__dirname, './src')
    }
  },
  build: {
    outDir: '../dist',
    assetsDir: 'assets'
  }
});
