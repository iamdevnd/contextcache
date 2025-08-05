import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint
from typing import Optional
from pathlib import Path
import json

from ..utils import get_api_client, format_triple, save_to_file

app = typer.Typer()
console = Console()

@app.command()
def insert(
    text: str = typer.Argument(..., help="Text to insert into memory"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Optional context"),
    no_extract: bool = typer.Option(False, "--no-extract", help="Skip triple extraction"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show extracted triples")
):
    """Insert text into the memory graph"""
    client = get_api_client()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing text...", total=None)
        
        try:
            response = client.post("/api/memory/insert", json={
                "text": text,
                "context": context,
                "extract_triples": not no_extract
            })
            
            if response.status_code == 200:
                data = response.json()
                progress.update(task, completed=True)
                
                rprint(f"[green]✓ Memory inserted successfully![/green]")
                rprint(f"  • Triples extracted: [cyan]{data['triples_extracted']}[/cyan]")
                rprint(f"  • Nodes created: [cyan]{data['nodes_created']}[/cyan]")
                rprint(f"  • Edges created: [cyan]{data['edges_created']}[/cyan]")
                
                if verbose and data['triples_extracted'] > 0:
                    console.print("\n[bold]Extracted relationships:[/bold]")
                    # Note: In a real implementation, we'd return the actual triples
                    console.print("[dim]Use the query command to explore the extracted knowledge[/dim]")
            else:
                rprint(f"[red]Error: {response.status_code} - {response.text}[/red]")
                
        except Exception as e:
            progress.update(task, completed=True)
            rprint(f"[red]Failed to insert memory: {e}[/red]")

@app.command()
def bulk_insert(
    file: Path = typer.Argument(..., help="File containing texts to insert (one per line)"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Context for all texts"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show progress for each item")
):
    """Bulk insert texts from a file"""
    if not file.exists():
        rprint(f"[red]Error: File '{file}' not found[/red]")
        raise typer.Exit(1)
    
    client = get_api_client()
    texts = file.read_text().strip().split('\n')
    
    total_triples = 0
    total_nodes = 0
    total_edges = 0
    failed = 0
    
    with Progress(console=console) as progress:
        task = progress.add_task(f"Processing {len(texts)} texts...", total=len(texts))
        
        for i, text in enumerate(texts):
            if not text.strip():
                continue
                
            try:
                response = client.post("/api/memory/insert", json={
                    "text": text.strip(),
                    "context": context,
                    "extract_triples": True
                })
                
                if response.status_code == 200:
                    data = response.json()
                    total_triples += data['triples_extracted']
                    total_nodes += data['nodes_created']
                    total_edges += data['edges_created']
                    
                    if verbose:
                        console.print(f"[green]✓[/green] {text[:50]}... ({data['triples_extracted']} triples)")
                else:
                    failed += 1
                    if verbose:
                        console.print(f"[red]✗[/red] {text[:50]}... (failed)")
                        
            except Exception as e:
                failed += 1
                if verbose:
                    console.print(f"[red]✗[/red] {text[:50]}... (error: {e})")
            
            progress.update(task, advance=1)
    
    # Summary
    console.print("\n[bold]Bulk Insert Summary:[/bold]")
    table = Table(show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Texts processed", str(len(texts)))
    table.add_row("Successful", str(len(texts) - failed))
    table.add_row("Failed", str(failed))
    table.add_row("Total triples", str(total_triples))
    table.add_row("Total nodes", str(total_nodes))
    table.add_row("Total edges", str(total_edges))
    
    console.print(table)

@app.command()
def stats():
    """Show memory statistics"""
    client = get_api_client()
    
    try:
        response = client.get("/api/memory/stats")
        if response.status_code == 200:
            stats = response.json()["stats"]
            
            # Create a nice table
            table = Table(title="Memory Statistics", show_header=True, header_style="bold magenta")
            table.add_column("Category", style="cyan", no_wrap=True)
            table.add_column("Count", style="yellow")
            table.add_column("Description", style="dim")
            
            table.add_row("Total Nodes", str(stats["total_nodes"]), "Entities in the knowledge graph")
            table.add_row("Total Edges", str(stats["total_edges"]), "Relationships between entities")
            
            # Memory layers
            if "memory_layers" in stats:
                for layer, count in stats["memory_layers"].items():
                    layer_name = layer.replace('_', ' ').title()
                    table.add_row(f"{layer_name}", str(count), f"Items in {layer} memory")
            
            console.print(table)
        else:
            rprint(f"[red]Error fetching stats: {response.status_code}[/red]")
            
    except Exception as e:
        rprint(f"[red]Failed to get statistics: {e}[/red]")

@app.command()
def export(
    output: Path = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)"),
    pretty: bool = typer.Option(True, "--pretty", help="Pretty print JSON output")
):
    """Export memory graph (requires authentication)"""
    console.print("[yellow]Note: Export requires admin authentication[/yellow]")
    console.print("[dim]Use the web UI or configure auth token for CLI export[/dim]")
    
    # Placeholder for authenticated export
    # In production, this would use auth tokens
    client = get_api_client()
    
    try:
        # This endpoint requires auth
        response = client.get("/api/memory/export")
        if response.status_code == 200:
            data = response.json()
            
            if format == "json":
                save_to_file(output, data["export"], pretty=pretty)
                rprint(f"[green]✓ Exported to {output}[/green]")
            else:
                rprint(f"[yellow]Format '{format}' not yet implemented[/yellow]")
        else:
            rprint(f"[red]Export failed: {response.status_code}[/red]")
            rprint("[yellow]This command requires admin authentication[/yellow]")
            
    except Exception as e:
        rprint(f"[red]Export error: {e}[/red]")

@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
):
    """Clear all memory (requires admin authentication)"""
    if not force:
        confirm = typer.confirm("⚠️  This will permanently delete all memory. Are you sure?")
        if not confirm:
            rprint("[yellow]Operation cancelled[/yellow]")
            raise typer.Exit()
    
    console.print("[yellow]Note: Clear requires admin authentication[/yellow]")
    console.print("[dim]Use the web UI or configure auth token for CLI clear[/dim]")
    
    # Placeholder - in production, this would use auth
    rprint("[red]Clear operation not available in CLI without authentication[/red]")
