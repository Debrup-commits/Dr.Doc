# ASI:One Next.js App

A modern Next.js application with Tailwind CSS that replicates the ASI:One website functionality. This project was converted from static HTML files to a fully functional Next.js application.

## Features

- **Modern Next.js 15** with App Router
- **Tailwind CSS** for styling
- **Dark/Light Theme** toggle with persistent storage
- **Responsive Design** for all screen sizes
- **TypeScript** for type safety
- **Lucide React** for icons

## Pages

- **Home** (`/`) - Landing page with hero section and features
- **Documentation** (`/documentation`) - Comprehensive documentation with sidebar navigation
- **API Reference** (`/api-reference`) - Complete API documentation with examples
- **Login** (`/login`) - Authentication page with sign up/sign in toggle

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
├── src/
│   ├── app/
│   │   ├── documentation/
│   │   │   └── page.tsx
│   │   ├── api-reference/
│   │   │   └── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   └── contexts/
│       └── ThemeContext.tsx
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.mjs
└── README.md
```

## Key Components

### ThemeContext
Provides dark/light theme switching with localStorage persistence.

### Header
Responsive navigation header with mobile menu and theme toggle.

### Footer
Simple footer with links and copyright information.

## Styling

The app uses Tailwind CSS with custom dark mode support. Theme switching is handled through CSS custom properties and the `data-theme` attribute.

## Responsive Design

- Mobile-first approach
- Collapsible sidebar on mobile devices
- Responsive typography and spacing
- Touch-friendly interface elements

## Browser Support

- Modern browsers with ES6+ support
- CSS Grid and Flexbox support required
- LocalStorage for theme persistence

## Development

The app is built with:
- Next.js 15.5.4
- React 19.1.0
- TypeScript
- Tailwind CSS 4
- Lucide React for icons

## Deployment

The app can be deployed to any platform that supports Next.js:
- Vercel (recommended)
- Netlify
- AWS Amplify
- Any Node.js hosting platform

## Conversion Summary

This project was successfully converted from static HTML files to a modern Next.js application:

### Original Files (Removed)
- `index.html` - Home page
- `documentation.html` - Documentation page  
- `api-reference.html` - API reference page
- `login.html` - Login page
- `docs/` - Documentation folder

### New Structure
- **Next.js App Router** with TypeScript
- **Tailwind CSS** for styling
- **Component-based architecture**
- **Theme context** for dark/light mode
- **Responsive design** for all devices
- **Modern development workflow**

### Key Improvements
- ✅ Server-side rendering (SSR)
- ✅ Component reusability
- ✅ Type safety with TypeScript
- ✅ Modern build system
- ✅ Hot reloading for development
- ✅ Optimized production builds
- ✅ Better SEO and performance

## License

This project is a demonstration of converting static HTML to a modern Next.js application.