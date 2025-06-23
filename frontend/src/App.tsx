import React from 'react';

function App() {
  console.log('🔥 App rendering with Tailwind v3!');
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">✨</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Success! 🎉
          </h1>
          <p className="text-gray-600 mb-6">
            Tailwind CSS v3 is working!
          </p>
          <button className="btn-primary w-full mb-4">
            Primary Button Test
          </button>
          <button className="btn-secondary w-full">
            Secondary Button Test
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;