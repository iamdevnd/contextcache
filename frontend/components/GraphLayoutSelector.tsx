import { FiGrid, FiCircle, FiActivity, FiShuffle } from 'react-icons/fi';

interface GraphLayoutSelectorProps {
  currentLayout: string;
  onLayoutChange: (layout: string) => void;
}

export default function GraphLayoutSelector({ currentLayout, onLayoutChange }: GraphLayoutSelectorProps) {
  const layouts = [
    { name: 'cose', label: 'Force-Directed', icon: <FiActivity /> },
    { name: 'circle', label: 'Circle', icon: <FiCircle /> },
    { name: 'grid', label: 'Grid', icon: <FiGrid /> },
    { name: 'random', label: 'Random', icon: <FiShuffle /> },
  ];

  return (
    <div className="flex space-x-2">
      {layouts.map(layout => (
        <button
          key={layout.name}
          onClick={() => onLayoutChange(layout.name)}
          className={`p-2 rounded-md transition ${
            currentLayout === layout.name
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-400 hover:text-white hover:bg-gray-600'
          }`}
          title={layout.label}
        >
          {layout.icon}
        </button>
      ))}
    </div>
  );
}
