const HistoricalPreview: React.FC = () => {
  const figures = [
    { name: 'Napoleon', emoji: '👑' },
    { name: 'Cleopatra', emoji: '🏺' },
    { name: 'Leonardo da Vinci', emoji: '🎨' },
    { name: 'Marie Antoinette', emoji: '👸' },
    { name: 'JFK', emoji: '🇺🇸' },
    { name: 'Frida Kahlo', emoji: '🌺' },
  ];

  return (
    <div className="mt-12 text-center">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        Meet Some Historical Figures
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
        {figures.map((figure) => (
          <div key={figure.name} className="text-center p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
            <div className="text-2xl mb-2">{figure.emoji}</div>
            <div className="text-xs text-gray-600 font-medium">{figure.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoricalPreview;