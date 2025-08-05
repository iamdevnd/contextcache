export default function OfflineNotice() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div className="text-center max-w-2xl mx-auto p-8">
        <h1 className="text-4xl font-bold mb-4">ContextCache</h1>
        <p className="text-xl text-gray-300 mb-8">AI Memory Engine with Knowledge Graphs</p>
        
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-yellow-400">🚧 Backend Setup Required</h2>
          <p className="text-gray-300 mb-4">
            The frontend is successfully deployed! To use ContextCache, you need to:
          </p>
          <ol className="text-left text-gray-300 space-y-2 ml-6">
            <li>1. Deploy the backend API server</li>
            <li>2. Set up ArangoDB database</li>
            <li>3. Configure the API URL in environment variables</li>
          </ol>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Quick Start Options:</h3>
          <div className="text-sm text-gray-400 space-y-2">
            <p>• Local Development: Run backend on localhost:8000</p>
            <p>• Cloud Deployment: Use Railway.app or DigitalOcean</p>
            <p>• Documentation: Check GitHub for setup instructions</p>
          </div>
        </div>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>Built by Nikhil Dodda</p>
          <p>Licensed under PolyForm Noncommercial 1.0.0</p>
        </div>
      </div>
    </div>
  );
}
