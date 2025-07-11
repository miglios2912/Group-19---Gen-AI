# TUM Chatbot Frontend

We built a mobile-friendly React interface that makes it easy for students and staff to chat with our university assistant.

## Features

**Mobile-First Design**

- Works well on phones, tablets, and desktop
- Touch-friendly interface with proper button sizes
- Optimized for iOS Safari and Android Chrome

**Smart Interface**

- Auto-hiding keyboard after sending messages
- Quick suggestion chips for common questions
- Real-time typing indicators
- Message history with copy functionality

**Campus Integration**

- Interactive campus map selection
- Campus-specific information display
- Visual TUM branding and colors

**User Experience**

- Dark mode support with system preference detection
- Smooth animations and transitions
- Accessible design with proper contrast
- Loading states and error handling

## Technical Architecture

**Development Mode:**

- **Vite dev server** runs on port 5173
- Hot module replacement for instant updates
- Proxy API requests to Flask backend (port 8083)
- Source maps for debugging

**Production Mode:**

- **Vite build** creates optimized bundle in `dist/`
- Assets are minified and compressed
- React components are bundled into static files
- Built files are served by Flask as static content

## Technical Features

- **React 19.1+** with modern hooks and context API
- **Vite 6.3+** for fast development and optimized builds
- **CSS custom properties** for theming and dark mode
- **Responsive design** with CSS Grid and Flexbox
- **Safe area insets** for iPhone notch support
- **Lucide React** for consistent iconography

## Files Structure

- `src/App.jsx` - Main application component with routing
- `src/components/ChatWindow.jsx` - Chat interface and message handling
- `src/components/InfoSidebar.jsx` - Campus links and navigation
- `src/components/DarkModeToggle.jsx` - Theme switching component
- `src/App.css` - Main application styles
- `src/index.css` - Global styles and CSS variables
- `public/` - Static assets and campus map images

## Configuration

### The port ip and port for the backend must be correctly set in vite.config.js!!!

## Development

```bash
npm install
npm run dev  # Runs on http://localhost:5173
```

## Building

```bash
npm run build  # Creates optimized bundle in dist/
```

## Production Integration

The built files are integrated with Flask backend:

1. Vite builds React app into static files
2. Flask serves `index.html` from `/static/` directory
3. API requests go to `/api/v2/` endpoints
4. Single container deployment serves both frontend and backend

The integration allows for seamless deployment while maintaining development flexibility.
