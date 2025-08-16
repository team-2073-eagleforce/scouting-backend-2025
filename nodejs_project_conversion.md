# Node.js Project Conversion Guide

This document outlines the conversion of the scouting backend project to use modern Node.js tooling for JavaScript development and asset management.

## Overview

The scouting backend project currently uses a traditional Django static files approach with JavaScript files scattered across different apps. This conversion will introduce modern Node.js tooling to improve the development experience, code organization, and build processes.

## Current Architecture

### JavaScript File Organization
- `staticfiles/scanner/scanner.js` - QR code scanning functionality
- `staticfiles/strategy/picklist.js` - Team picklist management
- `staticfiles/team/replay_system.js` - Match replay visualization
- `staticfiles/admin/js/` - Django admin interface scripts
- App-specific `static/` directories with duplicate files

### Current Issues
1. **Code Duplication**: Same JS files exist in both `staticfiles/` and app `static/` directories
2. **No Dependency Management**: External libraries are manually included
3. **No Build Process**: No minification, bundling, or optimization
4. **No Code Quality Tools**: No linting or formatting
5. **Manual Asset Management**: Static files managed manually

## Proposed Node.js Architecture

### Project Structure
```
├── frontend/
│   ├── src/
│   │   ├── scanner/
│   │   │   ├── scanner.js
│   │   │   └── qr-scanner.js
│   │   ├── strategy/
│   │   │   └── picklist.js
│   │   ├── team/
│   │   │   └── replay_system.js
│   │   ├── shared/
│   │   │   ├── utils.js
│   │   │   └── api.js
│   │   └── index.js
│   ├── dist/ (build output)
│   ├── package.json
│   ├── webpack.config.js
│   ├── .eslintrc.js
│   └── .prettierrc
├── staticfiles/ (Django static files)
└── manage.py
```

### Technology Stack
- **Package Manager**: npm
- **Build Tool**: Webpack 5
- **Code Quality**: ESLint + Prettier
- **Development**: Webpack Dev Server with hot reloading
- **Production**: Minification and optimization

## Implementation Plan

### Phase 1: Setup Node.js Environment
1. Initialize npm project with `package.json`
2. Install development dependencies
3. Configure build tools (Webpack)
4. Set up code quality tools (ESLint, Prettier)

### Phase 2: Reorganize JavaScript Files
1. Create `frontend/src/` directory structure
2. Move and refactor existing JS files
3. Extract common functionality into shared modules
4. Update import/export statements for ES modules

### Phase 3: Build Integration
1. Configure Webpack for development and production builds
2. Update Django settings for new static file locations
3. Create build scripts in package.json
4. Set up development workflow

### Phase 4: Development Workflow
1. Configure development server with hot reloading
2. Set up watch mode for automatic rebuilds
3. Create deployment scripts
4. Update documentation

## Benefits

### Developer Experience
- **Modern JavaScript**: ES6+ features, modules, async/await
- **Hot Reloading**: Instant feedback during development
- **Code Quality**: Automatic linting and formatting
- **Dependency Management**: Easy library installation and updates

### Performance
- **Bundling**: Reduced HTTP requests
- **Minification**: Smaller file sizes
- **Tree Shaking**: Remove unused code
- **Code Splitting**: Load only necessary code

### Maintainability
- **Organized Structure**: Clear separation of concerns
- **Shared Code**: Reusable components and utilities
- **Type Safety**: Optional TypeScript integration
- **Testing**: Jest testing framework integration

## Migration Strategy

### Development Environment Setup
```bash
# Install Node.js (LTS version)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Initialize project
cd /path/to/scouting-backend-2025
npm init -y

# Install dependencies
npm install --save-dev webpack webpack-cli webpack-dev-server
npm install --save-dev @babel/core @babel/preset-env babel-loader
npm install --save-dev eslint prettier eslint-config-prettier
npm install --save-dev css-loader style-loader mini-css-extract-plugin
```

### Django Integration
```python
# settings.py
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend', 'dist'),  # Built assets
    os.path.join(BASE_DIR, 'scanner', 'static'),
    os.path.join(BASE_DIR, 'teams', 'static'),
    os.path.join(BASE_DIR, 'strategy', 'static'),
]

# Development vs Production
if DEBUG:
    # Use Webpack dev server
    WEBPACK_DEV_SERVER_URL = 'http://localhost:8080'
else:
    # Use built static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
```

## File-by-File Migration

### scanner.js
- **Current**: Direct fetch calls, manual DOM manipulation
- **Proposed**: Modular structure with error handling, shared API utilities

### picklist.js
- **Current**: Global variables, mixed concerns
- **Proposed**: Class-based structure, state management, shared utilities

### replay_system.js
- **Current**: Large monolithic file
- **Proposed**: Separate modules for canvas, animation, data fetching

## Development Workflow

### Development Mode
```bash
# Start Django development server
python manage.py runserver

# Start Webpack development server (separate terminal)
npm run dev

# Watch for changes and rebuild
npm run watch
```

### Production Build
```bash
# Build optimized assets
npm run build

# Collect Django static files
python manage.py collectstatic
```

## Backward Compatibility

During the transition:
1. Keep existing files functional
2. Gradually migrate one module at a time
3. Maintain Django's static file structure
4. Ensure production deployments continue working

## Testing Strategy

### JavaScript Testing
- **Unit Tests**: Jest for individual functions
- **Integration Tests**: Test API interactions
- **E2E Tests**: Playwright for full user workflows

### Performance Testing
- **Bundle Analysis**: Webpack Bundle Analyzer
- **Load Testing**: Lighthouse performance audits
- **Memory Profiling**: Chrome DevTools

## Deployment Considerations

### Vercel Integration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel_app.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "npm run build",
        "outputDirectory": "dist"
      }
    }
  ]
}
```

### CI/CD Pipeline
```yaml
# .github/workflows/build.yml
- name: Setup Node.js
  uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'

- name: Install dependencies
  run: npm ci

- name: Build frontend
  run: npm run build

- name: Collect static files
  run: python manage.py collectstatic --noinput
```

## Timeline

- **Week 1**: Setup Node.js environment and basic tooling
- **Week 2**: Migrate scanner.js and establish patterns
- **Week 3**: Migrate picklist.js and strategy components
- **Week 4**: Migrate replay_system.js and team components
- **Week 5**: Testing, optimization, and documentation

## Next Steps

1. Create initial `package.json` and install dependencies
2. Set up basic Webpack configuration
3. Create development and production build scripts
4. Migrate first JavaScript module (scanner.js) as proof of concept
5. Establish patterns and guidelines for remaining modules

This conversion will significantly improve the development experience while maintaining the existing Django backend architecture and functionality.