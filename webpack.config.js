const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      main: './frontend/src/index.js',
      scanner: './frontend/src/scanner/scanner.js',
      picklist: './frontend/src/strategy/picklist.js',
      replay: './frontend/src/team/replay_system.js'
    },
    
    output: {
      path: path.resolve(__dirname, 'frontend/dist'),
      filename: isProduction ? '[name].[contenthash].js' : '[name].js',
      clean: true,
      publicPath: '/static/',
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
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader'
          ]
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource',
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/i,
          type: 'asset/resource',
        },
      ],
    },
    
    plugins: [
      ...(isProduction ? [
        new MiniCssExtractPlugin({
          filename: '[name].[contenthash].css',
        })
      ] : []),
    ],
    
    devServer: {
      static: {
        directory: path.join(__dirname, 'frontend/dist'),
      },
      compress: true,
      port: 8080,
      hot: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
        'Access-Control-Allow-Headers': 'X-Requested-With, content-type, Authorization'
      }
    },
    
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'frontend/src'),
        '@shared': path.resolve(__dirname, 'frontend/src/shared'),
      }
    },
    
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
          shared: {
            name: 'shared',
            minChunks: 2,
            chunks: 'all',
            enforce: true,
          },
        },
      },
    },
    
    devtool: isProduction ? 'source-map' : 'eval-source-map',
  };
};