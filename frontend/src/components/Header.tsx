import React from 'react';
import { Languages } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="pt-8 pb-4 px-6">
      <div className="flex items-center justify-center space-x-3">
        <div className="p-2 bg-blue-500 rounded-lg text-white">
          <Languages size={28} />
        </div>
        <h1 className="text-3xl font-bold text-white">Document Translation</h1>
      </div>
      <p className="text-center text-gray-400 mt-2 max-w-lg mx-auto">
        Securely upload your documents for translation. All file processing is done with high-quality machine translation.
      </p>
    </header>
  );
};

export default Header;