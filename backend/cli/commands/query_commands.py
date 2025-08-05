import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
from typing import Optional
import json

from ..utils import get_api_client, format_graph_data

app = typer.Typer()
console = Console()

@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to return"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json, graph)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed results")
):
    """Search the knowledge graph"""
    client = get_api_client()
    
    with console.status(f"[bold green]Searching for '{query}'..."):
        try:
            response = client.post("/api/memory/query", json={
                "query": query,
                "top_k": limit
            })
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {}).get("results", [])
                
                if not results:
                    rprint(f"[yellow]No results found for '{query}'[/yellow]")
                    return
                
                if format == "table":
                    _display_results_table(results, query, verbose)
                elif format == "json":
                    console.print(Syntax(json.dumps(results, indent=2), "json"))
                elif format == "graph":
                    _display_results_graph(results)
                else:
                    rprint(f"[red]Unknown format: {format}[/red]")
            else:
                rprint(f"[red]Search failed: {response.status_code}[/red]")
                
        except Exception as e:
            rprint(f"[red]Search error: {e}[/red]")

def _display_results_table(results: list, query: str, verbose: bool):
    """Display search results in a table"""
    table = Table(title=f"Search Results for '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Entity", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Relationships", style="green")
    
    for i, result in enumerate(results, 1):
        node = result.get("node", {})
        edges = result.get("edges", [])
        
        entity = node.get("entity", "Unknown")
        entity_type = node.get("entity_type", "entity")
        rel_count = len(edges)
        
        # Truncate long entities
        if len(entity) > 50 and not verbose:
            entity = entity[:47] + "..."
        
        table.add_row(
            str(i),
            entity,
            entity_type,
            f"{rel_count} connections"
        )
        
        if verbose and edges:
            # Show some relationships
            for edge in edges[:3]:
                verb = edge.get("verb", "related")
                table.add_row("", f"  → {verb}", "", "", end_section=i == len(results))
    
    console.print(table)

def _display_results_graph(results: list):
    """Display results as a text graph"""
    console.print(Panel.fit("[bold]Knowledge Graph View[/bold]"))
    
    for i, result in enumerate(results):
        node = result.get("node", {})
        edges = result.get("edges", [])
        
        entity = node.get("entity", "Unknown")
        console.print(f"\n[bold cyan]{entity}[/bold cyan]")
        
        if edges:
            for edge in edges[:5]:  # Show up to 5 edges
                verb = edge.get("verb", "related")
                from_id = edge.get("_from", "").split("/")[-1]
                to_id = edge.get("_to", "").split("/")[-1]
                
                if from_id == node.get("_key"):
                    console.print(f"  └─[green]{verb}[/green]→ {to_id}")
                else:
                    console.print(f"  └─←[green]{verb}[/green]─ {from_id}")

@app.command()
def graph(
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum nodes to display"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save graph to file")
):
    """Visualize the entire knowledge graph"""
    client = get_api_client()
    
    with console.status("[bold green]Loading knowledge graph..."):
        try:
            response = client.get(f"/api/memory/graph?limit={limit}")
            
            if response.status_code == 200:
                data = response.json()
                graph_data = data.get("graph", {})
                
                nodes = graph_data.get("nodes", [])
                edges = graph_data.get("edges", [])
                
                console.print(f"\n[bold]Knowledge Graph Summary:[/bold]")
                console.print(f"  • Nodes: [cyan]{len(nodes)}[/cyan]")
                console.print(f"  • Edges: [cyan]{len(edges)}[/cyan]")
                
                if output:
                    # Save to file
                    with open(output, 'w') as f:
                        json.dump(graph_data, f, indent=2)
                    rprint(f"[green]✓ Graph saved to {output}[/green]")
                else:
                    # Display sample
                    console.print("\n[bold]Sample Nodes:[/bold]")
                    for node in nodes[:10]:
                        console.print(f"  • {node.get('entity', 'Unknown')} [{node.get('entity_type', 'entity')}]")
                    
                    if len(nodes) > 10:
                        console.print(f"  [dim]... and {len(nodes) - 10} more[/dim]")
                    
                    console.print("\n[dim]Use --output to save the full graph[/dim]")
            else:
                rprint(f"[red]Failed to load graph: {response.status_code}[/red]")
                
        except Exception as e:
            rprint(f"[red]Graph error: {e}[/red]")

@app.command()
def related(
    entity: str = typer.Argument(..., help="Entity to find relationships for"),
    depth: int = typer.Option(1, "--depth", "-d", help="Relationship depth to explore"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum relationships to show")
):
    """Find relationships for a specific entity"""
    client = get_api_client()
    
    # Use the query endpoint to find the entity
    with console.status(f"[bold green]Finding relationships for '{entity}'..."):
        try:
            response = client.post("/api/memory/query", json={
                "query": entity,
                "top_k": 1  # Get the best match
            })
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", {}).get("results", [])
                
                if not results:
                    rprint(f"[yellow]Entity '{entity}' not found[/yellow]")
                    return
                
                # Get the first (best) match
                result = results[0]
                node = result.get("node", {})
                edges = result.get("edges", [])
                
                console.print(Panel.fit(
                    f"[bold cyan]{node.get('entity', 'Unknown')}[/bold cyan]\n"
                    f"Type: {node.get('entity_type', 'entity')}\n"
                    f"ID: {node.get('_key', 'unknown')}",
                    title="Entity Details"
                ))
                
                if edges:
                    table = Table(title="Relationships", show_header=True)
                    table.add_column("Direction", style="yellow", width=10)
                    table.add_column("Relationship", style="green")
                    table.add_column("Entity", style="cyan")
                    
                    for edge in edges[:limit]:
                        from_id = edge.get("_from", "").split("/")[-1]
                        to_id = edge.get("_to", "").split("/")[-1]
                        verb = edge.get("verb", "related")
                        
                        if from_id == node.get("_key"):
                            table.add_row("→", verb, to_id)
                        else:
                            table.add_row("←", verb, from_id)
                    
                    console.print(table)
                    
                    if len(edges) > limit:
                        console.print(f"\n[dim]Showing {limit} of {len(edges)} relationships[/dim]")
                else:
                    console.print("[yellow]No relationships found[/yellow]")
            else:
                rprint(f"[red]Query failed: {response.status_code}[/red]")
                
        except Exception as e:
            rprint(f"[red]Error: {e}[/red]")
