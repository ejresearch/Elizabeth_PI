#!/usr/bin/env python3
"""
CLI Interface for Bucket Library Management
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from bucket_library_integration import BucketLibraryIntegration

console = Console()

@click.group()
@click.pass_context
def cli(ctx):
    """Bucket Library Management System"""
    ctx.ensure_object(dict)
    ctx.obj['integration'] = BucketLibraryIntegration()

@cli.command()
@click.option('--name', prompt='Bucket name', help='Name of the bucket')
@click.option('--description', default='', help='Description of the bucket')
@click.option('--scope', type=click.Choice(['library', 'local']), default='library', 
              help='Create in library (shared) or local (project-specific)')
@click.pass_context
def create(ctx, name, description, scope):
    """Create a new bucket"""
    integration = ctx.obj['integration']
    
    with console.status(f"Creating {scope} bucket '{name}'..."):
        result = integration.create_bucket(name, description, scope)
    
    if result['success']:
        console.print(f"[green]✓ Created bucket: {result.get('bucket_id', name)}[/green]")
        if 'path' in result:
            console.print(f"  Path: {result['path']}")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

@cli.command()
@click.pass_context
def list(ctx):
    """List all available buckets"""
    integration = ctx.obj['integration']
    
    data = integration.list_available_buckets()
    
    # Project buckets table
    console.print("\n[bold]Project Buckets[/bold]")
    
    if data['project']['local']:
        console.print("\n[cyan]Local Buckets:[/cyan]")
        table = Table()
        table.add_column("Name", style="yellow")
        table.add_column("Type")
        table.add_column("Created")
        
        for bucket in data['project']['local']:
            table.add_row(
                bucket['name'],
                "Local",
                bucket.get('created_at', 'Unknown')[:10]
            )
        console.print(table)
    
    if data['project']['imported']:
        console.print("\n[cyan]Imported Buckets:[/cyan]")
        table = Table()
        table.add_column("ID", style="green")
        table.add_column("Name")
        table.add_column("Projects", style="blue")
        
        for bucket in data['project']['imported']:
            table.add_row(
                bucket['id'],
                bucket['name'],
                ", ".join(bucket.get('projects', []))
            )
        console.print(table)
    
    # Library buckets available for import
    if data['library']['available']:
        console.print("\n[bold]Available in Library[/bold]")
        table = Table()
        table.add_column("ID", style="magenta")
        table.add_column("Name")
        table.add_column("Created By")
        table.add_column("Shared With")
        
        for bucket in data['library']['available']:
            table.add_row(
                bucket['id'],
                bucket['name'],
                bucket.get('created_by_project', 'Unknown'),
                str(len(bucket.get('projects', []))) + " projects"
            )
        console.print(table)

@cli.command()
@click.argument('bucket_id')
@click.pass_context
def import_bucket(ctx, bucket_id):
    """Import a bucket from the library"""
    integration = ctx.obj['integration']
    
    with console.status(f"Importing bucket '{bucket_id}'..."):
        result = integration.project_manager.import_from_library(bucket_id)
    
    if result['success']:
        console.print(f"[green]✓ {result['message']}[/green]")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

@cli.command()
@click.argument('bucket_ids', nargs=-1, required=True)
@click.pass_context
def batch_import(ctx, bucket_ids):
    """Import multiple buckets from the library"""
    integration = ctx.obj['integration']
    
    with console.status(f"Importing {len(bucket_ids)} buckets..."):
        result = integration.batch_import_buckets(list(bucket_ids))
    
    if result['imported']:
        console.print(f"[green]✓ Imported: {', '.join(result['imported'])}[/green]")
    
    if result['failed']:
        console.print("[red]Failed imports:[/red]")
        for failure in result['failed']:
            console.print(f"  - {failure['bucket_id']}: {failure['error']}")

@cli.command()
@click.argument('local_bucket_name')
@click.option('--description', default='', help='Description for the promoted bucket')
@click.pass_context
def promote(ctx, local_bucket_name, description):
    """Promote a local bucket to the library"""
    integration = ctx.obj['integration']
    
    with console.status(f"Promoting '{local_bucket_name}' to library..."):
        result = integration.promote_local_bucket(local_bucket_name, description)
    
    if result['success']:
        console.print(f"[green]✓ {result['message']}[/green]")
        console.print(f"  New ID: {result['bucket_id']}")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

@cli.command()
@click.argument('bucket_id')
@click.argument('target_project')
@click.pass_context
def share(ctx, bucket_id, target_project):
    """Share a bucket with another project"""
    integration = ctx.obj['integration']
    
    with console.status(f"Sharing '{bucket_id}' with '{target_project}'..."):
        result = integration.share_bucket_with_project(bucket_id, target_project)
    
    if result['success']:
        console.print(f"[green]✓ {result['message']}[/green]")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

@cli.command()
@click.argument('bucket_id')
@click.argument('export_path')
@click.pass_context
def export(ctx, bucket_id, export_path):
    """Export a bucket to an external location"""
    integration = ctx.obj['integration']
    
    with console.status(f"Exporting '{bucket_id}'..."):
        result = integration.export_bucket(bucket_id, export_path)
    
    if result['success']:
        console.print(f"[green]✓ Exported to: {result['exported_to']}[/green]")
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

@cli.command()
@click.argument('query')
@click.pass_context
def search(ctx, query):
    """Search for buckets in the library"""
    integration = ctx.obj['integration']
    
    results = integration.search_library(query)
    
    if results:
        console.print(f"\n[bold]Found {len(results)} buckets matching '{query}'[/bold]")
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="yellow")
        table.add_column("Description")
        table.add_column("Projects")
        
        for bucket in results:
            table.add_row(
                bucket['id'],
                bucket['name'],
                bucket.get('description', '')[:50],
                ", ".join(bucket.get('projects', []))
            )
        console.print(table)
    else:
        console.print(f"[yellow]No buckets found matching '{query}'[/yellow]")

@cli.command()
@click.pass_context
def stats(ctx):
    """Show library statistics"""
    integration = ctx.obj['integration']
    
    dashboard = integration.get_library_dashboard()
    
    # Library stats panel
    lib_stats = dashboard['library_stats']
    stats_text = f"""
[bold]Library Statistics[/bold]
━━━━━━━━━━━━━━━━━
Total Buckets: [cyan]{lib_stats['total_buckets']}[/cyan]
Total Projects: [green]{lib_stats['total_projects']}[/green]
Total Size: [yellow]{lib_stats['total_size_mb']:.2f} MB[/yellow]
Average Bucket Size: [magenta]{lib_stats['average_bucket_size_mb']:.2f} MB[/magenta]
Library Path: {lib_stats['library_path']}
"""
    console.print(Panel(stats_text, title="Bucket Library"))
    
    # Project stats
    proj_buckets = dashboard['project_buckets']
    proj_text = f"""
[bold]Project: {dashboard['project_name']}[/bold]
━━━━━━━━━━━━━━━━━
Local Buckets: [yellow]{len(proj_buckets['local'])}[/yellow]
Imported Buckets: [green]{len(proj_buckets['imported'])}[/green]
Active Buckets: [cyan]{len(dashboard['active_buckets'])}[/cyan]
Project Directory: {dashboard['project_dir']}
"""
    console.print(Panel(proj_text, title="Current Project"))
    
    # Most shared buckets
    if lib_stats.get('most_shared_buckets'):
        console.print("\n[bold]Most Shared Buckets[/bold]")
        table = Table()
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Shared With")
        
        for bucket in lib_stats['most_shared_buckets'][:5]:
            table.add_row(
                bucket['id'],
                bucket['name'],
                f"{len(bucket.get('projects', []))} projects"
            )
        console.print(table)

@cli.command()
@click.pass_context
def migrate(ctx):
    """Migrate existing buckets to the library system"""
    integration = ctx.obj['integration']
    
    console.print("[bold]Starting migration of existing buckets...[/bold]")
    
    with console.status("Migrating buckets..."):
        results = integration.migrate_existing_buckets()
    
    if results['migrated']:
        console.print(f"\n[green]✓ Successfully migrated {len(results['migrated'])} buckets:[/green]")
        for item in results['migrated']:
            console.print(f"  - {item['original']} → {item['bucket_id']}")
    
    if results['failed']:
        console.print(f"\n[red]✗ Failed to migrate {len(results['failed'])} buckets:[/red]")
        for item in results['failed']:
            console.print(f"  - {item['bucket']}: {item['error']}")
    
    if results['skipped']:
        console.print(f"\n[yellow]⊘ Skipped {len(results['skipped'])} buckets[/yellow]")

@cli.command()
@click.argument('bucket_id')
@click.pass_context
def info(ctx, bucket_id):
    """Show detailed information about a bucket"""
    integration = ctx.obj['integration']
    
    info = integration.library.get_bucket_info(bucket_id)
    
    if info:
        tree = Tree(f"[bold]{info['name']}[/bold] ({info['id']})")
        
        tree.add(f"Description: {info.get('description', 'None')}")
        tree.add(f"Created: {info['created_at']}")
        tree.add(f"Created By: {info.get('created_by_project', 'Unknown')}")
        
        projects_branch = tree.add("Projects")
        for project in info.get('projects', []):
            projects_branch.add(project)
        
        stats_branch = tree.add("Statistics")
        stats = info.get('stats', {})
        stats_branch.add(f"Documents: {stats.get('document_count', 0)}")
        stats_branch.add(f"Entities: {stats.get('entity_count', 0)}")
        stats_branch.add(f"Relationships: {stats.get('relationship_count', 0)}")
        
        storage_branch = tree.add("Storage")
        storage = info.get('storage', {})
        storage_branch.add(f"Path: {storage.get('path', 'Unknown')}")
        storage_branch.add(f"Size: {storage.get('size_mb', 0):.2f} MB")
        
        console.print(tree)
    else:
        console.print(f"[red]Bucket '{bucket_id}' not found[/red]")

@cli.command()
@click.argument('bucket_id')
@click.argument('document_file')
@click.pass_context
def add_document(ctx, bucket_id, document_file):
    """Add a document to a bucket"""
    integration = ctx.obj['integration']
    
    try:
        with open(document_file, 'r') as f:
            content = f.read()
        
        with console.status(f"Adding document to '{bucket_id}'..."):
            result = integration.add_document_to_bucket(bucket_id, content)
        
        if result['success']:
            console.print(f"[green]✓ {result['message']}[/green]")
        else:
            console.print(f"[red]✗ Failed: {result.get('error')}[/red]")
    except FileNotFoundError:
        console.print(f"[red]File '{document_file}' not found[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

@cli.command()
@click.argument('bucket_id')
@click.argument('query')
@click.option('--mode', type=click.Choice(['naive', 'local', 'global', 'hybrid']), 
              default='hybrid', help='Query mode')
@click.pass_context
def query(ctx, bucket_id, query, mode):
    """Query a bucket"""
    integration = ctx.obj['integration']
    
    with console.status(f"Querying '{bucket_id}'..."):
        result = integration.query_bucket(bucket_id, query, mode)
    
    if result['success']:
        console.print(f"\n[bold]Query Results[/bold] (mode: {mode})")
        console.print(Panel(str(result['result']), title=f"Bucket: {bucket_id}"))
    else:
        console.print(f"[red]✗ Failed: {result.get('error')}[/red]")

if __name__ == '__main__':
    cli()