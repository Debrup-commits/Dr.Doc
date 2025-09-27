'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ChevronRight, BookOpen, Code, ArrowLeft } from 'lucide-react';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { documentation, getDocCategory, getDocSection, getAllCategories } from '@/lib/docs';

export default function DocumentationSection() {
  const params = useParams();
  const router = useRouter();
  const categoryId = params.category as string;
  const sectionId = params.section as string;

  const [activeCategory, setActiveCategory] = useState(categoryId);
  const [activeSection, setActiveSection] = useState(sectionId);

  const categories = getAllCategories();
  const currentCategory = getDocCategory(activeCategory);
  const currentSection = getDocSection(activeCategory, activeSection);

  const categoryIcons: { [key: string]: any } = {
    'getting-started': BookOpen,
    'build-with-asi-one': Code,
  };

  const scrollToSection = (categoryId: string, sectionId: string) => {
    setActiveCategory(categoryId);
    setActiveSection(sectionId);
    router.push(`/documentation/${categoryId}/${sectionId}`);
  };

  // Update state when URL params change
  useEffect(() => {
    if (categoryId && sectionId) {
      setActiveCategory(categoryId);
      setActiveSection(sectionId);
    }
  }, [categoryId, sectionId]);

  // Redirect to first section if invalid
  useEffect(() => {
    if (!currentSection && categories.length > 0) {
      const firstCategory = categories[0];
      const firstSection = firstCategory.sections[0];
      if (firstSection) {
        router.replace(`/documentation/${firstCategory.id}/${firstSection.id}`);
      }
    }
  }, [currentSection, categories, router]);

  if (!currentSection) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <BookOpen size={48} className="mx-auto text-gray-400 dark:text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Documentation Section Not Found
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            The requested documentation section could not be found.
          </p>
          <button
            onClick={() => router.push('/documentation')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200"
          >
            Back to Documentation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <button
            onClick={() => router.push('/documentation')}
            className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 mb-4 transition-colors duration-200"
          >
            <ArrowLeft size={20} />
            <span>Back to Documentation</span>
          </button>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {currentSection.title}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            {currentCategory?.title} • {currentSection.title}
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6 sticky top-24">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Table of Contents
              </h2>
              <nav className="space-y-2">
                {categories.map((category) => {
                  const Icon = categoryIcons[category.id] || BookOpen;
                  return (
                    <div key={category.id} className="space-y-1">
                      <button
                        onClick={() => scrollToSection(category.id, category.sections[0]?.id || '')}
                        className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors duration-200 ${
                          activeCategory === category.id
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                        }`}
                      >
                        <Icon size={18} />
                        <span className="font-medium">{category.title}</span>
                      </button>
                      
                      {/* Sub-sections */}
                      {activeCategory === category.id && (
                        <div className="ml-6 space-y-1">
                          {category.sections.map((section) => (
                            <button
                              key={section.id}
                              onClick={() => scrollToSection(category.id, section.id)}
                              className={`w-full flex items-center space-x-2 px-3 py-1 rounded text-left transition-colors duration-200 ${
                                activeSection === section.id
                                  ? 'bg-blue-50 dark:bg-blue-800 text-blue-600 dark:text-blue-400'
                                  : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-slate-700'
                              }`}
                            >
                              <ChevronRight size={14} />
                              <span className="text-sm">{section.title}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8">
              <MarkdownRenderer content={currentSection.content} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
