const path = require('path');

module.exports = {
  mode: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  entry: {
    main: './src/js/main.js',
    'index': './src/js/index.js',
    // Core modules
    'app-initializer': './src/js/core/app-initializer.js',
    'chart-manager': './src/js/core/chart-manager.js',
    'state-manager': './src/js/core/state-manager.js',
    'ui-controller': './src/js/core/ui-controller.js',
    // Data handling modules
    'data-loader': './src/js/data-handling/data-loader.js',
    'data-processor': './src/js/data-handling/data-processor.js',
    'data-exporter': './src/js/data-handling/data-exporter.js',
    'example-manager': './src/js/data-handling/example-manager.js',
    // Adapter modules
    'chart-date-adapter': './src/js/adapters/chart-date-adapter.js',
    'chart-renderer': './src/js/adapters/chart-renderer.js',
    'chart-type-adapters': './src/js/adapters/chart-type-adapters.js',
    'candlestick-helper': './src/js/adapters/candlestick-helper.js',
    'chart-fix': './src/js/adapters/chart-fix.js',
    // Utility modules
    'dependency-checker': './src/js/utils/dependency-checker.js',
    'file-handler': './src/js/utils/file-handler.js',
    'theme-handler': './src/js/utils/theme-handler.js',
    'chart-themes': './src/js/utils/chart-themes.js',
    'json-validator': './src/js/utils/json-validator.js',
    'utils': './src/js/utils/utils.js',
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'static/js/dist'),
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  devtool: 'source-map',
};
