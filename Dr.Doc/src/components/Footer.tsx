import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-slate-950 text-slate-100 py-8 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="flex flex-wrap justify-center md:justify-start space-x-6">
            <Link
              href="/documentation"
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
            >
              Documentation
            </Link>
            <Link
              href="/api-reference"
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
            >
              API Reference
            </Link>
            <Link
              href="/login"
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
            >
              Login
            </Link>
            <a
              href="https://fetch.ai"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-emerald-400 transition-colors duration-200"
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
