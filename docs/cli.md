# ContextCache CLI Documentation

The ContextCache CLI provides command-line access to the AI memory engine.

## Installation

```bash
pip install -r backend/requirements.txt

##Basic Usage
bash# Check system status
python contextcache.py status

# Insert text into memory
python contextcache.py memory insert "Alice works at Google. Bob is her manager."

# Query the knowledge graph
python contextcache.py query search "Alice"

# Show memory statistics
python contextcache.py memory stats

Commands
General Commands

status - Check system status and connection
version - Show version information
shell - Start interactive shell mode

Memory Commands

memory insert <text> - Insert text into memory
memory bulk-insert <file> - Bulk insert from file
memory stats - Show memory statistics
memory export <file> - Export memory graph
memory clear - Clear all memory (requires auth)

Query Commands

query search <text> - Search the knowledge graph
query graph - Visualize the entire graph
query related <entity> - Find relationships for an entity

Admin Commands (Require Authentication)

admin login - Login as admin
admin config - Manage configuration
admin logs - View system logs
admin backup - Create system backup

Interactive Shell
Start the interactive shell for a more convenient interface:
bashpython contextcache.py shell
In shell mode:

insert <text> - Insert text
query <text> - Query graph
stats - Show statistics
help - Show commands
exit - Exit shell

Examples
Inserting Knowledge
bash# Simple insert
python contextcache.py memory insert "Python is a programming language"

# Insert with context
python contextcache.py memory insert "It was created by Guido van Rossum" --context "Python history"

# Bulk insert from file
python contextcache.py memory bulk-insert knowledge.txt
Querying
bash# Search for entities
python contextcache.py query search "Python" --limit 5

# Find relationships
python contextcache.py query related "Python" --depth 2

# Export graph visualization
python contextcache.py query graph --output graph.json
Advanced Usage
bash# Show verbose output
python contextcache.py memory insert "Complex text..." --verbose

# Different output formats
python contextcache.py query search "AI" --format json

# Skip triple extraction
python contextcache.py memory insert "Raw text storage" --no-extract
Configuration
The CLI connects to the backend API at http://localhost:8000 by default.
For production use, you can configure:

API endpoint
Authentication tokens
Output preferences

Notes

Admin commands require authentication via the web UI
The CLI uses the same backend as the web interface
All data is stored in the ArangoDB database


### Step 8.10: Test the CLI

Let's test the CLI tool:

```bash
# Make sure backend is running
# In one terminal:
source venv/bin/activate
python -m backend.main

# In another terminal:
source venv/bin/activate

# Test basic commands
python contextcache.py --help
python contextcache.py status
python contextcache.py version

# Test memory insertion
python contextcache.py memory insert "The CLI tool for ContextCache is now complete. It supports memory operations and queries."

# Test querying
python contextcache.py query search "CLI"

# Test interactive shell
python contextcache.py shell

