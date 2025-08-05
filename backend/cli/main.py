import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
import json
from typing import Optional
from pathlib import Path

from .commands import memory_commands, admin_commands, query_commands
from .utils import get_api_client, format_graph_data, save_to_file

# Create the main Typer app
app = typer.Typer(
    name="contextcache",
    help="ContextCache CLI - AI Memory Engine",
    add_completion=True,
    rich_markup_mode="rich"
)

# Add command groups
app.add_typer(memory_commands.app, name="memory", help="Memory management commands")
app.add_typer(query_commands.app, name="query", help="Query and search commands")
app.add_typer(admin_commands.app, name="admin", help="Admin commands")

console = Console()

@app.command()
def version():
    """Show version information"""
    rprint(Panel.fit(
        "[bold blue]ContextCache CLI[/bold blue]\n"
        "Version: 1.0.0\n"
        "AI Memory Engine with Knowledge Graphs",
        title="About"
    ))

@app.command()
def status():
    """Check system status and connection"""
    with console.status("[bold green]Checking system status..."):
        client = get_api_client()
        try:
            # Check health
            health_response = client.get("/health")
            health_data = health_response.json()
            
            # Get stats
            stats_response = client.get("/api/memory/stats")
            stats_data = stats_response.json()
            
            # Create status table
            table = Table(title="System Status", show_header=True, header_style="bold magenta")
            table.add_column("Component", style="cyan", no_wrap=True)
            table.add_column("Status", style="green")
            table.add_column("Details", style="yellow")
            
            table.add_row("API Server", "✓ Connected", f"http://localhost:8000")
            table.add_row("Database", health_data.get("database", "Unknown"), "ArangoDB")
            table.add_row("Total Nodes", str(stats_data["stats"]["total_nodes"]), "Knowledge graph nodes")
            table.add_row("Total Edges", str(stats_data["stats"]["total_edges"]), "Relationships")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error checking status: {e}[/red]")
            console.print("[yellow]Make sure the backend is running on http://localhost:8000[/yellow]")

@app.command()
def shell():
    """Start interactive shell mode"""
    console.print("[bold green]Starting ContextCache interactive shell...[/bold green]")
    console.print("Type 'help' for available commands, 'exit' to quit\n")
    
    while True:
        try:
            command = console.input("[bold blue]contextcache>[/bold blue] ").strip()
            
            if command.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif command.lower() == 'help':
                console.print("""
[bold]Available commands:[/bold]
  insert <text>     - Insert text into memory
  query <text>      - Query the knowledge graph
  stats             - Show memory statistics
  clear             - Clear all memory (requires confirmation)
  export <file>     - Export memory to file
  exit              - Exit the shell
                """)
            elif command.startswith('insert '):
                text = command[7:]
                _insert_text_shell(text)
            elif command.startswith('query '):
                text = command[6:]
                _query_text_shell(text)
            elif command == 'stats':
                _show_stats_shell()
            elif command == 'clear':
                _clear_memory_shell()
            elif command.startswith('export '):
                filename = command[7:]
                _export_memory_shell(filename)
            else:
                console.print(f"[red]Unknown command: {command}[/red]")
                console.print("Type 'help' for available commands")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def _insert_text_shell(text: str):
    """Insert text in shell mode"""
    client = get_api_client()
    try:
        response = client.post("/api/memory/insert", json={
            "text": text,
            "extract_triples": True
        })
        data = response.json()
        console.print(f"[green]✓ Inserted! Extracted {data['triples_extracted']} triples[/green]")
    except Exception as e:
        console.print(f"[red]Failed to insert: {e}[/red]")

def _query_text_shell(text: str):
    """Query in shell mode"""
    client = get_api_client()
    try:
        response = client.post("/api/memory/query", json={
            "query": text,
            "top_k": 5
        })
        data = response.json()
        
        if data["results"]["results"]:
            console.print(f"\n[bold]Found {len(data['results']['results'])} results:[/bold]")
            for i, result in enumerate(data["results"]["results"], 1):
                node = result.get("node", {})
                edges = result.get("edges", [])
                console.print(f"\n[cyan]{i}. {node.get('entity', 'Unknown')}[/cyan]")
                if edges:
                    console.print("   Relationships:")
                    for edge in edges[:3]:  # Show first 3 edges
                        console.print(f"   - {edge.get('verb', 'related')}")
        else:
            console.print("[yellow]No results found[/yellow]")
    except Exception as e:
        console.print(f"[red]Query failed: {e}[/red]")

def _show_stats_shell():
    """Show stats in shell mode"""
    client = get_api_client()
    try:
        response = client.get("/api/memory/stats")
        stats = response.json()["stats"]
        
        table = Table(title="Memory Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Nodes", str(stats["total_nodes"]))
        table.add_row("Total Edges", str(stats["total_edges"]))
        
        for layer, count in stats.get("memory_layers", {}).items():
            table.add_row(f"{layer.title()} Memory", str(count))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to get stats: {e}[/red]")

def _clear_memory_shell():
    """Clear memory in shell mode"""
    confirm = console.input("[red]Are you sure you want to clear all memory? (yes/no): [/red]")
    if confirm.lower() == 'yes':
        # Note: This would require authentication in production
        console.print("[yellow]Clear function requires admin authentication[/yellow]")
    else:
        console.print("[green]Cancelled[/green]")

def _export_memory_shell(filename: str):
    """Export memory in shell mode"""
    console.print(f"[yellow]Export to {filename} requires admin authentication[/yellow]")

if __name__ == "__main__":
    app()
