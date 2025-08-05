'use client';

import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { FiMaximize2, FiMinimize2, FiRefreshCw, FiZoomIn, FiZoomOut } from 'react-icons/fi';

interface GraphNode {
  _key: string;
  entity: string;
  entity_type?: string;
}

interface GraphEdge {
  _from: string;
  _to: string;
  verb: string;
  score?: number;
}

interface GraphViewProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: any) => void;
  height?: string;
}

export default function GraphView({ nodes, edges, onNodeClick, height = '600px' }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        // Add nodes
        ...nodes.map(node => ({
          data: {
            id: node._key,
            label: node.entity,
            type: node.entity_type || 'entity'
          }
        })),
        // Add edges
        ...edges.map(edge => ({
          data: {
            source: edge._from.split('/')[1], // Remove collection prefix
            target: edge._to.split('/')[1],
            label: edge.verb,
            weight: edge.score || 1
          }
        }))
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#4F46E5',
            'label': 'data(label)',
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'width': '60px',
            'height': '60px',
            'text-wrap': 'wrap',
            'text-max-width': '50px',
            'border-width': 2,
            'border-color': '#6366F1'
          }
        },
        {
          selector: 'node[type="document"]',
          style: {
            'background-color': '#10B981',
            'shape': 'rectangle',
            'width': '80px',
            'height': '40px'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#6B7280',
            'target-arrow-color': '#6B7280',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#D1D5DB',
            'text-rotation': 'autorotate',
            'text-margin-y': -10
          }
        },
        {
          selector: 'node:selected',
          style: {
            'background-color': '#EF4444',
            'border-color': '#F87171',
            'border-width': 4
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 1000,
        nodeRepulsion: 400000,
        idealEdgeLength: 100,
        edgeElasticity: 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 1000,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0
      },
      wheelSensitivity: 0.2,
      minZoom: 0.1,
      maxZoom: 3
    });

    // Add click handler
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      if (onNodeClick) {
        onNodeClick(node.data());
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, onNodeClick]);

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.2);
      cyRef.current.center();
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.8);
      cyRef.current.center();
    }
  };

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  };

  const handleReset = () => {
    if (cyRef.current) {
      const layout = cyRef.current.layout({
        name: 'cose',
        animate: true,
        animationDuration: 1000
      });
      layout.run();
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-gray-900' : ''}`}>
      {/* Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-white transition"
          title="Zoom In"
        >
          <FiZoomIn />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-white transition"
          title="Zoom Out"
        >
          <FiZoomOut />
        </button>
        <button
          onClick={handleFit}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-white transition"
          title="Fit to Screen"
        >
          <FiMaximize2 />
        </button>
        <button
          onClick={handleReset}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-white transition"
          title="Reset Layout"
        >
          <FiRefreshCw />
        </button>
        <button
          onClick={toggleFullscreen}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-md text-white transition"
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? <FiMinimize2 /> : <FiMaximize2 />}
        </button>
      </div>

      {/* Graph Container */}
      <div
        ref={containerRef}
        className="w-full bg-gray-900 rounded-lg"
        style={{ height: isFullscreen ? '100vh' : height }}
      />

      {/* Node count */}
      <div className="absolute bottom-4 left-4 text-sm text-gray-400">
        {nodes.length} nodes, {edges.length} edges
      </div>
    </div>
  );
}
