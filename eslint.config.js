import js from '@eslint/js';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // Browser globals
        'window': 'readonly',
        'document': 'readonly',
        'console': 'readonly',
        'fetch': 'readonly',
        'setTimeout': 'readonly',
        'clearTimeout': 'readonly',
        'navigator': 'readonly',
        'process': 'readonly',
        // Django globals
        'django': 'readonly',
        'gettext': 'readonly',
        'ngettext': 'readonly',
        'interpolate': 'readonly',
        // QR Scanner globals
        'QrScanner': 'readonly',
        // Browser globals that might not be recognized
        'ResizeObserver': 'readonly',
        'HTMLElement': 'readonly',
      },
    },
    rules: {
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'template-curly-spacing': 'error',
      'arrow-spacing': 'error',
      'comma-dangle': ['error', 'always-multiline'],
      'quotes': ['error', 'single', { avoidEscape: true }],
      'semi': ['error', 'always'],
    },
  },
];