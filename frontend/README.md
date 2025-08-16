# Frontend Development Guide

This document provides guidance for working with the modern JavaScript development environment in the scouting backend project.

## Prerequisites

- Node.js (LTS version recommended)
- npm (comes with Node.js)
- Python 3.x (for Django backend)

## Quick Start

### Development Setup

1. **Install dependencies:**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Start development servers:**
   ```bash
   # Terminal 1: Start Django development server
   python manage.py runserver
   
   # Terminal 2: Start webpack in watch mode (optional)
   npm run watch
   ```

3. **Build for production:**
   ```bash
   npm run build
   ./build.sh  # Full build including Django static collection
   ```

## Development Scripts

| Command | Description |
|---------|-------------|
| `npm run build` | Build production-optimized bundles |
| `npm run dev` | Start webpack dev server with hot reloading |
| `npm run watch` | Watch files and rebuild on changes |
| `npm run lint` | Check code quality with ESLint |
| `npm run lint:fix` | Auto-fix linting issues |
| `npm run format` | Format code with Prettier |

## Project Structure

```
frontend/
├── src/
│   ├── index.js              # Main entry point
│   ├── shared/               # Shared utilities
│   │   ├── api.js           # API helpers (fetch, CSRF, etc.)
│   │   └── utils.js         # DOM utilities and helpers
│   ├── scanner/             # QR scanner functionality
│   │   └── scanner.js       # Modern QR scanner module
│   ├── strategy/            # Strategy and picklist management
│   │   └── picklist.js      # Team picklist drag-and-drop
│   └── team/                # Team-related functionality
│       └── replay_system.js # Match replay visualization
├── dist/                     # Built assets (auto-generated)
└── package.json             # Node.js dependencies and scripts
```

## Code Organization

### Shared Utilities

**API Utilities (`@shared/api`):**
- `getCookie(name)` - Get Django CSRF tokens
- `apiRequest(url, options)` - Make authenticated API requests
- `postJSON(url, data)` - POST JSON data with CSRF protection
- `triggerHapticFeedback()` - Trigger device vibration

**DOM Utilities (`@shared/utils`):**
- `getElementById(id)` - Safe element selection with error handling
- `addEventListener(element, event, handler)` - Safe event binding
- `createElement(tag, attrs, content)` - Create elements programmatically
- `debounce(func, wait)` - Debounce function calls
- `throttle(func, limit)` - Throttle function calls

### Module Patterns

Each module follows a consistent class-based pattern:

```javascript
import { postJSON } from '@shared/api';
import { getElementById, addEventListener } from '@shared/utils';

class MyModule {
  constructor() {
    this.config = { /* configuration */ };
    this.elements = { /* cached DOM elements */ };
    this.init();
  }

  init() {
    this.initializeElements();
    this.setupEventListeners();
  }

  initializeElements() {
    this.elements.button = getElementById('my-button');
  }

  setupEventListeners() {
    addEventListener(this.elements.button, 'click', () => this.handleClick());
  }

  async handleClick() {
    try {
      const response = await postJSON('/api/endpoint', { data: 'value' });
      // Handle response
    } catch (error) {
      console.error('Error:', error);
    }
  }
}

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  new MyModule();
});

export default MyModule;
```

## Development Workflow

### 1. Creating New Modules

1. Create new file in appropriate directory (`frontend/src/`)
2. Follow the class-based pattern shown above
3. Import required utilities from `@shared/`
4. Add to webpack entry points if needed (in `webpack.config.js`)

### 2. Code Quality

- **Linting:** ESLint enforces code quality and style
- **Formatting:** Prettier ensures consistent formatting
- **Modern JS:** Use ES6+ features (classes, arrow functions, async/await)
- **Modules:** Use ES6 imports/exports for modularity

### 3. Testing Changes

```bash
# Check for linting issues
npm run lint

# Build and test
npm run build
python manage.py collectstatic --noinput

# Run Django with built assets
python manage.py runserver
```

## Migrating Legacy JavaScript

When migrating existing JavaScript files:

### Before (Legacy)
```javascript
// Global variables and functions
let draggedItem = null;

function saveData() {
    fetch('/api/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => console.log(data));
}

document.getElementById('save-btn').addEventListener('click', saveData);
```

### After (Modern)
```javascript
import { postJSON } from '@shared/api';
import { getElementById, addEventListener } from '@shared/utils';

class DataManager {
  constructor() {
    this.draggedItem = null;
    this.init();
  }

  init() {
    this.saveButton = getElementById('save-btn');
    addEventListener(this.saveButton, 'click', () => this.saveData());
  }

  async saveData() {
    try {
      const response = await postJSON('/api/save', this.getData());
      console.log('Saved:', response);
    } catch (error) {
      console.error('Save failed:', error);
    }
  }

  getData() {
    return { /* data to save */ };
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new DataManager();
});
```

## Build Output

The build process creates optimized bundles:

- **Code Splitting:** Shared utilities are bundled separately
- **Minification:** Production builds are minified and optimized
- **Source Maps:** Available for debugging
- **Cache Busting:** Filenames include content hashes for cache invalidation

Example build output:
```
frontend/dist/
├── main.[hash].js              # Main entry point
├── scanner.[hash].js           # Scanner module
├── picklist.[hash].js          # Picklist module
├── shared.[hash].js            # Shared utilities
└── *.map                       # Source maps
```

## Integration with Django

The built assets are automatically included in Django's static files:

1. **Development:** Assets built to `frontend/dist/`
2. **Django Config:** `STATICFILES_DIRS` includes `frontend/dist/`
3. **Collection:** `collectstatic` copies to `staticfiles/`
4. **Templates:** Include with `{% load static %}` and `{% static 'scanner.[hash].js' %}`

## Troubleshooting

### Common Issues

**Build Errors:**
- Check Node.js version (LTS recommended)
- Run `npm install` to update dependencies
- Check for syntax errors with `npm run lint`

**Import Errors:**
- Verify file paths in imports
- Check that files exist in `frontend/src/`
- Ensure webpack aliases are configured correctly

**Django Integration:**
- Run `npm run build` before `collectstatic`
- Check `STATICFILES_DIRS` includes `frontend/dist/`
- Verify template static file references

### Debugging

1. **Development Mode:**
   ```bash
   npm run watch  # Auto-rebuild on changes
   ```

2. **Source Maps:** Available in browser dev tools for debugging built code

3. **Console:** Modern modules expose debug objects:
   ```javascript
   // In browser console
   window.qrScanner      // QR scanner instance
   window.teamPicklist   // Picklist instance
   ```

## Performance Considerations

- **Lazy Loading:** Consider dynamic imports for large modules
- **Bundle Analysis:** Use webpack-bundle-analyzer to optimize bundles
- **Caching:** Built files include content hashes for browser caching
- **Compression:** Enable gzip compression in production

## Next Steps

1. **Complete Migration:** Migrate remaining legacy JavaScript files
2. **Testing:** Add unit tests with Jest
3. **TypeScript:** Consider adding TypeScript for better type safety
4. **PWA Features:** Add service worker for offline functionality
5. **Performance:** Implement code splitting for larger modules

This modern JavaScript development environment provides a solid foundation for building maintainable, performant frontend code while integrating seamlessly with the existing Django backend.