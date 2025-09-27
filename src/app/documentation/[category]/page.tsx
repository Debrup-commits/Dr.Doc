'use client';

import { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getAllCategories } from '@/lib/docs';

export default function DocumentationCategory() {
  const params = useParams();
  const router = useRouter();
  const categoryId = params.category as string;

  const categories = getAllCategories();
  const category = categories.find(cat => cat.id === categoryId);

  useEffect(() => {
    if (category && category.sections.length > 0) {
      // Redirect to the first section of the category
      const firstSection = category.sections[0];
      router.replace(`/documentation/${categoryId}/${firstSection.id}`);
    } else {
      // Redirect to main documentation page if category not found
      router.replace('/documentation');
    }
  }, [category, categoryId, router]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-300">Loading documentation...</p>
      </div>
    </div>
  );
}
