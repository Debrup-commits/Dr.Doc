import Link from 'next/link';

export default function Footer() {
  return (
<<<<<<< HEAD
    <footer className="bg-slate-950 text-slate-100 py-8 border-t border-slate-800">
=======
    <footer className="bg-slate-900 dark:bg-slate-950 text-white py-8">
>>>>>>> 1d392c7 (mcp crude implementation)
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="flex flex-wrap justify-center md:justify-start space-x-6">
            <Link
              href="/documentation"
<<<<<<< HEAD
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
=======
              className="text-slate-400 hover:text-white transition-colors duration-200"
>>>>>>> 1d392c7 (mcp crude implementation)
            >
              Documentation
            </Link>
            <Link
              href="/api-reference"
<<<<<<< HEAD
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
=======
              className="text-slate-400 hover:text-white transition-colors duration-200"
>>>>>>> 1d392c7 (mcp crude implementation)
            >
              API Reference
            </Link>
            <Link
              href="/login"
<<<<<<< HEAD
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
=======
              className="text-slate-400 hover:text-white transition-colors duration-200"
>>>>>>> 1d392c7 (mcp crude implementation)
            >
              Login
            </Link>
            <a
              href="https://fetch.ai"
              target="_blank"
              rel="noopener noreferrer"
<<<<<<< HEAD
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
=======
              className="text-slate-400 hover:text-white transition-colors duration-200"
>>>>>>> 1d392c7 (mcp crude implementation)
            >
              Built with Fetch.ai
            </a>
          </div>
          <div className="text-slate-400 text-sm">
            © 2024 ASI:One. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
