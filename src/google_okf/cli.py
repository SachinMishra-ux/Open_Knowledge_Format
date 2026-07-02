import os
import sys
import click
import yaml
from pathlib import Path
from google_okf.core.models import Concept
from google_okf.core.writer import write_bundle
from google_okf.core.reader import read_bundle, validate_bundle_links
from google_okf.producers.document import DocumentProducer
from google_okf.producers.mysql import MySQLProducer
from google_okf.producers.mongodb import MongoDBProducer

@click.group()
def cli():
    """Google Open Knowledge Format (OKF) command line utility."""
    pass

@cli.command()
@click.argument("directory", type=click.Path(file_okay=False))
def init(directory):
    """Initialize a blank OKF Knowledge Bundle directory."""
    bundle_path = Path(directory)
    try:
        bundle_path.mkdir(parents=True, exist_ok=True)
        # Create subdirectories for typical asset concepts
        (bundle_path / "tables").mkdir(exist_ok=True)
        (bundle_path / "documents").mkdir(exist_ok=True)
        (bundle_path / "definitions").mkdir(exist_ok=True)
        
        # Create a default index.md
        index_content = (
            "---\n"
            "type: Index\n"
            "title: Knowledge Index\n"
            "description: Root index of the Knowledge Bundle.\n"
            "---\n\n"
            "# Knowledge Bundle Index\n\n"
            "Welcome to your Open Knowledge Format (OKF) bundle.\n"
        )
        with open(bundle_path / "index.md", "w", encoding="utf-8") as f:
            f.write(index_content)
            
        # Create a basic .gitignore to ignore OS artifacts
        gitignore_content = ".DS_Store\n__pycache__/\n"
        with open(bundle_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
            
        click.echo(f"Successfully initialized blank OKF bundle at: {bundle_path.resolve()}")
    except Exception as e:
        click.echo(f"Error initializing bundle: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
def lint(directory):
    """Validate OKF compliance and verify all internal markdown links."""
    bundle_path = Path(directory)
    click.echo(f"Validating OKF bundle at: {bundle_path.resolve()}")
    
    errors = 0
    
    # 1. Parse all concepts
    try:
        concepts = read_bundle(bundle_path)
        click.echo(f"Successfully parsed {len(concepts)} concept file(s).")
    except Exception as e:
        click.echo(f"❌ Failed to parse bundle files: {e}", err=True)
        errors += 1
        sys.exit(1)
        
    # 2. Check each concept frontmatter requirements
    for concept_id, concept in concepts.items():
        if not concept.type:
            click.echo(f"❌ Concept '{concept_id}' is missing required 'type' frontmatter field.", err=True)
            errors += 1
            
    # 3. Check for broken internal links
    broken_links = validate_bundle_links(bundle_path)
    if broken_links:
        click.echo(f"Found {len(broken_links)} broken internal link(s):")
        for source_id, link, error in broken_links:
            click.echo(f"  ❌ Broken link in '{source_id}': '{link}' -> {error}", err=True)
            errors += 1
    else:
        click.echo("✅ All internal markdown links resolved successfully.")
        
    if errors > 0:
        click.echo(f"❌ Validation failed with {errors} error(s).", err=True)
        sys.exit(1)
    else:
        click.echo("🎉 Knowledge Bundle is fully OKF compliant!")

@cli.command()
@click.option("--type", "-t", type=click.Choice(["files", "mysql", "mongodb"]), help="The type of producer to run.")
@click.option("--uri", "-u", help="Database connection URI.")
@click.option("--db-name", "-d", help="Database name (required for MongoDB).")
@click.option("--src-dir", "-s", type=click.Path(exists=True, file_okay=False), help="Source directory (required for flat files).")
@click.option("--out-dir", "-o", type=click.Path(file_okay=False), default="bundle", help="Output directory for generated OKF files.")
@click.option("--config", "-c", type=click.Path(exists=True, dir_okay=False), help="Path to a YAML configuration file.")
def produce(type, uri, db_name, src_dir, out_dir, config):
    """Generate OKF Concepts from a data source and save them to a bundle."""
    producer_type = type
    connection_uri = uri
    database_name = db_name
    source_dir = src_dir
    output_dir = Path(out_dir)
    
    # Load configuration file if provided
    if config:
        try:
            with open(config, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            producer_type = producer_type or cfg.get("producer")
            connection_uri = connection_uri or cfg.get("connection_uri") or cfg.get("uri")
            database_name = database_name or cfg.get("database_name") or cfg.get("db_name")
            source_dir = source_dir or cfg.get("source_dir") or cfg.get("src_dir")
            if "output_dir" in cfg or "out_dir" in cfg:
                output_dir = Path(cfg.get("output_dir") or cfg.get("out_dir"))
        except Exception as e:
            click.echo(f"Error loading config file: {e}", err=True)
            sys.exit(1)
            
    if not producer_type:
        click.echo("Error: --type or a config file with 'producer' specified is required.", err=True)
        sys.exit(1)
        
    producer = None
    
    if producer_type == "files":
        if not source_dir:
            click.echo("Error: --src-dir is required for flat files producer.", err=True)
            sys.exit(1)
        producer = DocumentProducer(source_dir=source_dir)
        
    elif producer_type == "mysql":
        if not connection_uri:
            click.echo("Error: --uri is required for MySQL database producer.", err=True)
            sys.exit(1)
        producer = MySQLProducer(connection_uri=connection_uri)
        
    elif producer_type == "mongodb":
        if not connection_uri or not database_name:
            click.echo("Error: --uri and --db-name are required for MongoDB producer.", err=True)
            sys.exit(1)
        producer = MongoDBProducer(connection_uri=connection_uri, database_name=database_name)
        
    if not producer:
        click.echo("Error: Invalid producer setup.", err=True)
        sys.exit(1)
        
    click.echo(f"Running '{producer_type}' producer...")
    try:
        concepts = producer.produce()
        click.echo(f"Successfully generated {len(concepts)} concept(s). Writing to '{output_dir}'...")
        write_bundle(output_dir, concepts)
        click.echo("Done!")
    except Exception as e:
        click.echo(f"Error during execution: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()
