from arango import ArangoClient
from arango.database import Database
from arango.exceptions import DocumentInsertError, ArangoError
from typing import Optional, List, Dict, Any
import logging
from ..config import get_settings
from .models import MemoryNode, MemoryEdge, MemoryLayer

logger = logging.getLogger(__name__)

class ArangoDriver:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to ArangoDB"""
        try:
            self.client = ArangoClient(
                hosts=f'http://{self.settings.arango_host}:{self.settings.arango_port}'
            )
            
            sys_db = self.client.db(
                '_system',
                username=self.settings.arango_username,
                password=self.settings.arango_root_password
            )
            
            # Create database if it doesn't exist
            if not sys_db.has_database(self.settings.arango_database):
                sys_db.create_database(self.settings.arango_database)
            
            # Connect to the database
            self.db = self.client.db(
                self.settings.arango_database,
                username=self.settings.arango_username,
                password=self.settings.arango_root_password
            )
            
            self._setup_collections()
            logger.info("Successfully connected to ArangoDB")
            
        except ArangoError as e:
            logger.error(f"Failed to connect to ArangoDB: {e}")
            raise
    
    def _setup_collections(self):
        """Create required collections and indexes"""
        # Node collection
        if not self.db.has_collection('mem_nodes'):
            self.db.create_collection('mem_nodes')
            nodes = self.db.collection('mem_nodes')
            nodes.add_persistent_index(fields=['entity'])
            nodes.add_persistent_index(fields=['entity_type'])
        
        # Edge collection
        if not self.db.has_collection('mem_edges'):
            self.db.create_collection('mem_edges', edge=True)
            edges = self.db.collection('mem_edges')
            edges.add_persistent_index(fields=['verb'])
            edges.add_persistent_index(fields=['layer'])
            edges.add_persistent_index(fields=['created_at'])
        
        # Session collection
        if not self.db.has_collection('sessions'):
            self.db.create_collection('sessions')
        
        # Admin config collection
        if not self.db.has_collection('admin_config'):
            self.db.create_collection('admin_config')
            # Insert default config
            config = self.db.collection('admin_config')
            if config.count() == 0:
                config.insert({
                    '_key': 'default',
                    'rate_limit_per_minute': self.settings.rate_limit_per_minute,
                    'rate_limit_per_hour': self.settings.rate_limit_per_hour,
                    'footer_text': 'Built by Nikhil Dodda',
                    'max_memory_items': self.settings.max_memory_items
                })
    
    def insert_node(self, node: MemoryNode) -> str:
        """Insert or update a memory node"""
        collection = self.db.collection('mem_nodes')
        node_dict = node.dict(by_alias=True, exclude_none=True)
        
        # Check if node exists
        existing = collection.find({'entity': node.entity}, limit=1)
        existing_list = list(existing)
        
        if existing_list:
            # Update existing node
            doc_id = existing_list[0]['_key']
            node_dict['updated_at'] = node.updated_at.isoformat()
            collection.update({'_key': doc_id}, node_dict)
            return f"mem_nodes/{doc_id}"
        else:
            # Insert new node
            node_dict['created_at'] = node.created_at.isoformat()
            node_dict['updated_at'] = node.updated_at.isoformat()
            result = collection.insert(node_dict)
            return f"mem_nodes/{result['_key']}"
    
    def insert_edge(self, edge: MemoryEdge) -> str:
        """Insert a memory edge"""
        collection = self.db.collection('mem_edges')
        edge_dict = edge.dict(by_alias=True, exclude_none=True)
        edge_dict['created_at'] = edge.created_at.isoformat()
        
        result = collection.insert(edge_dict)
        return result['_key']
    
    def query_memories(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Query memories using AQL"""
        aql = """
        FOR node IN mem_nodes
            FILTER CONTAINS(LOWER(node.entity), LOWER(@query))
            LET edges = (
                FOR edge IN mem_edges
                    FILTER edge._from == node._id OR edge._to == node._id
                    RETURN edge
            )
            RETURN {
                node: node,
                edges: edges
            }
        LIMIT @limit
        """
        
        cursor = self.db.aql.execute(
            aql,
            bind_vars={'query': query, 'limit': top_k}
        )
        
        results = list(cursor)
        return {
            'results': results,
            'count': len(results)
        }
    
    def get_graph_stats(self) -> Dict[str, int]:
        """Get graph statistics"""
        nodes = self.db.collection('mem_nodes')
        edges = self.db.collection('mem_edges')
        
        return {
            'total_nodes': nodes.count(),
            'total_edges': edges.count(),
            'memory_layers': {
                layer.value: edges.find({'layer': layer.value}).count()
                for layer in MemoryLayer
            }
        }
    
    def clear_all(self):
        """Clear all memory data"""
        self.db.collection('mem_nodes').truncate()
        self.db.collection('mem_edges').truncate()
        self.db.collection('sessions').truncate()
        logger.info("All memory data cleared")
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            self.db.aql.execute("RETURN 1")
            return True
        except:
            return False

# Singleton instance
_driver_instance = None

def get_arango_driver() -> ArangoDriver:
    global _driver_instance
    if _driver_instance is None:
        _driver_instance = ArangoDriver()
    return _driver_instance
