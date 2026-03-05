"""
GraphRAG Educational Setup System
=================================

Interactive setup that handles fresh installations and existing databases,
designed for educational use with clear explanations and safe operations.

Usage:
    python 0_setup.py           # Interactive mode (default)
    python 0_setup.py --fresh    # Force fresh start
    python 0_setup.py --continue # Continue with existing data
    python 0_setup.py --check    # Just check status
    python 0_setup.py --learning # Educational mode with explanations
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
import sys
import argparse
import subprocess
import time
from enum import Enum
from typing import Dict, Any, Optional
import logging

# Neo4j utils
from langchain_neo4j import Neo4jGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def check_docker_neo4j() -> Dict[str, Any]:
    """Check Docker availability and Neo4j container status."""
    status = {
        'docker_available': False,
        'neo4j_container': None,
        'container_status': None
    }

    try:
        # Check if Docker is running
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.Names}}\t{{.ID}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            status['docker_available'] = True

            # Look for Neo4j container
            for line in result.stdout.strip().split('\n'):
                if line and 'neo4j-graphrag' in line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        status['neo4j_container'] = parts[1]  # Container ID
                        # Check if container is running
                        status['container_status'] = 'Up' if 'Up' in parts[2] else 'Exited'
                    break

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    return status


class Neo4jStatusChecker:
    """Check Neo4j database connection and status."""

    def __init__(self):
        """Initialize Neo4j status checker with connection parameters."""
        self.url = "bolt://localhost:7687"
        self.username = "neo4j"
        self.password = "password123"
        self.graph = None

    def check_connection(self) -> Dict[str, Any]:
        """Check if Neo4j is accessible."""
        result = {
            'connected': False,
            'uri': self.url,
            'version': 'unknown'
        }

        try:
            # Attempt to connect
            self.graph = Neo4jGraph(
                url=self.url,
                username=self.username,
                password=self.password
            )

            # Try to get version
            try:
                version_result = self.graph.query("CALL dbms.components() YIELD versions RETURN versions[0] as version")
                if version_result and len(version_result) > 0:
                    result['version'] = version_result[0].get('version', 'unknown')
            except Exception:
                result['version'] = 'connected'

            result['connected'] = True

        except Exception as e:
            logger.debug(f"Connection failed: {e}")

        return result

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            'total_nodes': 0,
            'total_relationships': 0,
            'node_types': {},
            'programmers': 0,
            'last_update': None
        }

        if not self.graph:
            if not self.check_connection()['connected']:
                return {'error': 'Not connected to Neo4j'}

        try:
            # Get total nodes
            result = self.graph.query("MATCH (n) RETURN count(n) as count")
            if result:
                stats['total_nodes'] = result[0].get('count', 0)

            # Get total relationships
            result = self.graph.query("MATCH ()-[r]->() RETURN count(r) as count")
            if result:
                stats['total_relationships'] = result[0].get('count', 0)

            # Get node types and counts
            result = self.graph.query("""
                MATCH (n)
                UNWIND labels(n) as label
                RETURN label, count(*) as count
                ORDER BY count DESC
            """)
            if result:
                for row in result:
                    label = row.get('label')
                    count = row.get('count', 0)
                    if label:
                        stats['node_types'][label] = count

            # Get programmer count (Person nodes)
            result = self.graph.query("MATCH (p:Person) RETURN count(p) as count")
            if result:
                stats['programmers'] = result[0].get('count', 0)

        except Exception as e:
            logger.debug(f"Error getting stats: {e}")
            return {'error': str(e)}

        return stats

    def check_data_integrity(self) -> Dict[str, Any]:
        """Check data integrity and quality."""
        integrity = {
            'issues': [],
            'warnings': []
        }

        if not self.graph:
            if not self.check_connection()['connected']:
                return integrity

        try:
            # Check for orphaned nodes (nodes with no relationships)
            result = self.graph.query("""
                MATCH (n)
                WHERE NOT (n)-[]-()
                RETURN count(n) as orphaned_count
            """)
            if result and result[0].get('orphaned_count', 0) > 0:
                integrity['warnings'].append(
                    f"{result[0]['orphaned_count']} orphaned nodes (no relationships)"
                )

            # Check for Person nodes without skills
            result = self.graph.query("""
                MATCH (p:Person)
                WHERE NOT (p)-[:HAS_SKILL]->()
                RETURN count(p) as count
            """)
            if result and result[0].get('count', 0) > 0:
                integrity['warnings'].append(
                    f"{result[0]['count']} Person nodes without skills"
                )

        except Exception as e:
            logger.debug(f"Error checking integrity: {e}")

        return integrity

    def clear_database(self, confirm: bool = True) -> bool:
        """Clear all data from the database."""
        if not self.graph:
            if not self.check_connection()['connected']:
                logger.error("Cannot clear database: not connected")
                return False

        try:
            # Delete all nodes and relationships
            self.graph.query("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return False

class SetupMode(Enum):
    INTERACTIVE = "interactive"
    FRESH = "fresh"
    CONTINUE = "continue"
    CHECK = "check"
    LEARNING = "learning"
    INIT = "init"

class GraphRAGSetup:
    """Main setup class for GraphRAG educational system."""

    def __init__(self, mode: SetupMode = SetupMode.INTERACTIVE, learning_mode: bool = False):
        """Initialize setup with specified mode."""
        self.mode = mode
        self.learning_mode = learning_mode
        self.neo4j_checker = Neo4jStatusChecker()

    def main(self):
        """Main setup workflow."""
        self.print_header()

        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False

        # Step 2: Check current state
        status = self.analyze_current_state()
        if not status:
            return False

        # Step 3: Decide action based on mode
        if self.mode == SetupMode.CHECK:
            self.display_status_report(status)
            return True

        elif self.mode == SetupMode.INIT:
            return self.setup_init(status)

        elif self.mode == SetupMode.FRESH:
            return self.setup_fresh(status)

        elif self.mode == SetupMode.CONTINUE:
            return self.setup_continue(status)

        else:  # INTERACTIVE or LEARNING
            return self.interactive_setup(status)

    def print_header(self):
        """Print educational header."""
        print("=" * 70)
        print("🎓 GraphRAG Educational Setup System")
        print("=" * 70)

        if self.learning_mode:
            print("\n📖 Learning Mode: Explanations will be provided for each step")

        print(f"\n🔧 Mode: {self.mode.value.title()}")
        print("-" * 40)

    def check_prerequisites(self) -> bool:
        """Check all prerequisites for the system."""
        print("\n🔍 Checking Prerequisites...")

        all_good = True

        # Check Python environment
        if self.learning_mode:
            print("\n📚 What we're checking:")
            print("  - Python packages (OpenAI, Neo4j, etc.)")
            print("  - Docker availability")
            print("  - Neo4j database connection")
            print("  - OpenAI API key")

        # Check required packages
        try:
            import openai
            import neo4j
            import langchain_openai
            import langchain_neo4j
            print("✓ Required Python packages installed")
        except ImportError as e:
            print(f"✗ Missing Python package: {e}")
            print("  Run: uv sync")
            all_good = False

        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("✗ OPENAI_API_KEY not found")
            print("  Add your API key to .env file")
            all_good = False
        else:
            print("✓ OpenAI API key found")

        # Check Docker and Neo4j
        docker_status = check_docker_neo4j()
        if not docker_status['docker_available']:
            print("✗ Docker not available")
            print("  Install Docker Desktop and start it")
            all_good = False
        else:
            print("✓ Docker available")

        if not all_good:
            print("\n❌ Prerequisites not met. Please fix the issues above.")
            return False

        return True

    def analyze_current_state(self) -> Optional[Dict[str, Any]]:
        """Analyze current database state."""
        print("\n🔍 Analyzing Current State...")

        if self.learning_mode:
            print("\n📚 What's happening:")
            print("  - Checking if Neo4j is running")
            print("  - Looking for existing data")
            print("  - Assessing data quality")

        # Check Neo4j connection
        connection_status = self.neo4j_checker.check_connection()

        if not connection_status['connected']:
            print("⚠️  Neo4j not running")
            docker_status = check_docker_neo4j()

            if docker_status['neo4j_container']:
                if docker_status['container_status'] != 'Up':
                    print("  Starting existing Neo4j container...")
                    self.start_neo4j_container()
                    time.sleep(5)
                    connection_status = self.neo4j_checker.check_connection()
            else:
                print("  No Neo4j container found")
                if not self.setup_neo4j_docker():
                    return None
                connection_status = self.neo4j_checker.check_connection()

        if not connection_status['connected']:
            print("❌ Could not establish Neo4j connection")
            self.show_docker_troubleshooting()
            return None

        print(f"✓ Connected to Neo4j {connection_status.get('version', 'unknown')}")

        # Get database statistics
        db_stats = self.neo4j_checker.get_database_stats()
        if 'error' in db_stats:
            print(f"⚠️  Could not get database stats: {db_stats['error']}")
            db_stats = {'total_nodes': 0, 'total_relationships': 0}

        # Check data integrity
        integrity = self.neo4j_checker.check_data_integrity()

        status = {
            'connection': connection_status,
            'stats': db_stats,
            'integrity': integrity,
            'has_data': db_stats.get('total_nodes', 0) > 0,
            'has_programmers': db_stats.get('programmers', 0) > 0
        }

        return status

    def display_status_report(self, status: Dict[str, Any]):
        """Display comprehensive status report."""
        print("\n📊 Database Status Report")
        print("=" * 40)

        stats = status['stats']

        if status['has_data']:
            print("✓ Knowledge graph exists")
            print(f"  📈 Total nodes: {stats.get('total_nodes', 0):,}")
            print(f"  🔗 Total relationships: {stats.get('total_relationships', 0):,}")
            print()
            print("📋 Entity Counts:")
            for entity, count in stats.get('node_types', {}).items():
                if entity and count > 0:
                    print(f"  • {entity}: {count:,}")

            if stats.get('last_update'):
                print(f"\n🕒 Last updated: {stats['last_update']}")

            # Show integrity issues
            integrity = status.get('integrity', {})
            if integrity.get('issues'):
                print("\n⚠️  Data Issues:")
                for issue in integrity['issues']:
                    print(f"  • {issue}")

            if integrity.get('warnings'):
                print("\n💡 Suggestions:")
                for warning in integrity['warnings']:
                    print(f"  • {warning}")
        else:
            print("✗ No data found (empty database)")

        print("\n🔗 Connection Info:")
        print(f"  URI: {status['connection']['uri']}")
        print(f"  Version: {status['connection'].get('version', 'unknown')}")

    def interactive_setup(self, status: Dict[str, Any]) -> bool:
        """Interactive setup menu."""
        print("\n🎯 What would you like to do?")
        print("-" * 40)

        if status['has_data']:
            options = [
                ("1", "Continue with existing data", "continue"),
                ("2", "View current data status", "status"),
                ("3", "Add more data to existing graph", "extend"),
                ("4", "Rebuild from scratch", "fresh"),
                ("5", "Run test queries", "test"),
                ("6", "Backup current data", "backup"),
                ("0", "Exit", "exit")
            ]
        else:
            options = [
                ("1", "Initialize new knowledge graph", "fresh"),
                ("2", "Load sample data", "sample"),
                ("3", "View setup instructions", "help"),
                ("0", "Exit", "exit")
            ]

        for num, desc, _ in options:
            print(f"  {num}. {desc}")

        while True:
            choice = input("\nEnter your choice (0-6): ").strip()

            action = next((action for num, _, action in options if num == choice), None)
            if action:
                return self.execute_action(action, status)
            else:
                print("Invalid choice. Please try again.")

    def execute_action(self, action: str, status: Dict[str, Any]) -> bool:
        """Execute the chosen action."""
        if action == "exit":
            print("👋 Goodbye!")
            return True

        elif action == "continue":
            print("\n✓ Using existing knowledge graph")
            self.show_next_steps(status)
            return True

        elif action == "status":
            self.display_status_report(status)
            return True

        elif action == "fresh":
            return self.setup_fresh(status)

        elif action == "extend":
            return self.extend_existing_data()

        elif action == "test":
            return self.run_test_queries()

        elif action == "backup":
            return self.backup_data()

        elif action == "sample":
            return self.load_sample_data()

        elif action == "help":
            self.show_help()
            return True

        else:
            print(f"Action '{action}' not implemented yet")
            return True

    def setup_fresh(self, status: Dict[str, Any]) -> bool:
        """Set up fresh knowledge graph."""
        if status['has_data']:
            print("\n⚠️  Warning: This will delete all existing data!")
            if not self.confirm_action("Continue with fresh setup?"):
                return True

        print("\n🚀 Setting up fresh GraphRAG system...")

        if self.learning_mode:
            print("\n📚 What's happening:")
            print("  1. Clearing database completely")
            print("  2. Generating sample programmer data")
            print("  3. Creating knowledge graph from data")
            print("  4. Verifying the setup")

        # Step 1: Clear database
        print("\n1️⃣ Clearing database...")
        if not self.neo4j_checker.clear_database(confirm=True):
            print("❌ Failed to clear database")
            return False
        print("✓ Database cleared")

        # Step 2: Create directories
        print("\n2️⃣ Creating project structure...")
        self.create_project_structure()

        # Step 3: Generate data
        print("\n3️⃣ Generating sample data...")
        if not self.run_script("1_generate_data.py"):
            return False

        # Step 4: Build knowledge graph
        print("\n4️⃣ Building knowledge graph...")
        if not self.run_script("2_data_to_knowledge_graph.py"):
            return False

        # Step 5: Verify
        print("\n5️⃣ Verifying setup...")
        final_status = self.analyze_current_state()
        if final_status and final_status['has_data']:
            print("✅ Setup completed successfully!")
            self.display_status_report(final_status)
            self.show_next_steps(final_status)
            return True
        else:
            print("❌ Setup verification failed")
            return False

    def setup_continue(self, status: Dict[str, Any]) -> bool:
        """Continue with existing data."""
        if not status['has_data']:
            print("No existing data found. Initializing fresh setup...")
            return self.setup_fresh(status)
        else:
            print("✓ Using existing knowledge graph")
            self.show_next_steps(status)
            return True

    def setup_init(self, status: Dict[str, Any]) -> bool:
        """Initialize Neo4j and project structure only."""
        print("\n🔧 Initializing environment...")

        if self.learning_mode:
            print("\n📚 What's happening:")
            print("  1. Starting Neo4j server if not running")
            print("  2. Creating project directory structure")
            print("  3. Database will remain empty for manual data population")

        # Check if Neo4j is running, start if not
        if not status['connection']['connected']:
            print("\n🚀 Starting Neo4j server...")
            docker_status = check_docker_neo4j()

            if docker_status['neo4j_container'] and docker_status['container_status'] != 'Up':
                # Start existing container
                self.start_neo4j_container()
                print("⏳ Waiting for Neo4j to be ready...")
                time.sleep(5)
            elif not docker_status['neo4j_container']:
                # Set up new container
                if not self.setup_neo4j_docker():
                    print("❌ Failed to start Neo4j")
                    return False

            # Verify connection
            connection_status = self.neo4j_checker.check_connection()
            if not connection_status['connected']:
                print("❌ Could not establish Neo4j connection")
                self.show_docker_troubleshooting()
                return False

        # Create project directories
        print("\n📁 Creating project structure...")
        self.create_project_structure()

        # Print Neo4j server addresses
        print("\n🌐 Neo4j Server Active:")
        print("  📊 Neo4j Browser: http://localhost:7474")
        print("  🔌 Bolt Protocol:  bolt://localhost:7687")
        print("  👤 Username: neo4j")
        print("  🔑 Password: password123")

        # Show current database status
        print("\n📊 Current Database Status:")
        if status['has_data']:
            print(f"  ⚠️  Database contains {status['stats'].get('total_nodes', 0)} nodes")
            print("  💡 Use --fresh to clear and rebuild, or --continue to use existing data")
        else:
            print("  ✓ Database is empty and ready")

        # Show next steps
        print("\n🎯 Next Steps:")
        print("  1. Generate sample CVs:")
        print("     uv run 1_generate_data.py")
        print("  2. Build knowledge graph:")
        print("     uv run 2_data_to_knowledge_graph.py")
        print("  3. Query the graph:")
        print("     uv run 3_query_knowledge_graph.py")
        print("\n✅ Initialization complete!")

        return True

    def run_script(self, script_name: str) -> bool:
        """Run a Python script and report results."""
        try:
            if self.learning_mode:
                print(f"  📝 Running {script_name}...")

            result = subprocess.run([
                sys.executable, script_name
            ], capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"✓ {script_name} completed successfully")
                return True
            else:
                print(f"❌ {script_name} failed:")
                print(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ {script_name} timed out")
            return False
        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
            return False

    def create_project_structure(self):
        """Create required directories."""
        directories = [
            "data/programmers",
            "data/projects",
            "data/RFP",
            "results",
            "utils"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        print("✓ Project structure created")

    def setup_neo4j_docker(self) -> bool:
        """Set up Neo4j using Docker."""
        print("\n🐳 Setting up Neo4j with Docker...")

        # Check if docker-compose.yml exists
        if not os.path.exists("docker-compose.yml"):
            print("Creating docker-compose.yml...")
            self.create_docker_compose()

        try:
            result = subprocess.run([
                "docker-compose", "up", "-d"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print("✓ Neo4j started with Docker Compose")
                print("⏳ Waiting for Neo4j to be ready...")
                time.sleep(15)
                return True
            else:
                print(f"❌ Failed to start Neo4j: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error starting Neo4j: {e}")
            return False

    def start_neo4j_container(self):
        """Start existing Neo4j container."""
        try:
            docker_status = check_docker_neo4j()
            if docker_status['neo4j_container']:
                result = subprocess.run([
                    "docker", "start", docker_status['neo4j_container']
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print("✓ Neo4j container started")
                else:
                    print(f"⚠️  Could not start container: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Error starting container: {e}")

    def create_docker_compose(self):
        """Create docker-compose.yml for Neo4j."""
        compose_content = '''version: '3.8'
services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j-graphrag
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password123
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs
      - neo4j-import:/var/lib/neo4j/import
      - neo4j-plugins:/plugins
    restart: unless-stopped

volumes:
  neo4j-data:
  neo4j-logs:
  neo4j-import:
  neo4j-plugins:
'''

        with open("docker-compose.yml", "w") as f:
            f.write(compose_content)
        print("✓ Created docker-compose.yml")

    def show_next_steps(self, status: Dict[str, Any]):
        """Show appropriate next steps."""
        print("\n🎯 Next Steps:")
        print("-" * 30)

        if status['has_programmers']:
            print("• Try some queries:")
            print("  python 3_query_knowledge_graph.py")
            print("• Test GraphRAG vs Naive RAG:")
            print("  python 5_compare_systems.py")
        else:
            print("• Generate some data first:")
            print("  python 1_generate_data.py")

        print("• Explore in Neo4j Browser:")
        print("  http://localhost:7474")
        print("  Username: neo4j, Password: password123")

    def show_help(self):
        """Show detailed help information."""
        print("\n📚 GraphRAG Setup Help")
        print("=" * 30)
        print("""
This system demonstrates GraphRAG (Graph Retrieval Augmented Generation)
for a programmer staffing use case.

Components:
• Neo4j: Graph database for storing relationships
• OpenAI: LLM for text processing and queries
• LangChain: Framework connecting LLMs to data

Workflow:
1. Generate synthetic programmer CVs and project data
2. Extract knowledge graph from unstructured PDFs
3. Query the graph using natural language
4. Compare with traditional RAG approaches

Files:
• 1_generate_data.py: Create sample CVs and projects
• 2_data_to_knowledge_graph.py: Build graph from PDFs
• 3_query_knowledge_graph.py: Query the graph
• 4_graph_rag_system.py: Full GraphRAG implementation
• 5_compare_systems.py: Compare different approaches
        """)

    def show_docker_troubleshooting(self):
        """Show Docker troubleshooting tips."""
        print("\n🔧 Docker Troubleshooting:")
        print("1. Make sure Docker Desktop is running")
        print("2. Try: docker-compose up -d")
        print("3. Check logs: docker-compose logs neo4j")
        print("4. Reset: docker-compose down && docker-compose up -d")

    def confirm_action(self, message: str) -> bool:
        """Get user confirmation."""
        while True:
            response = input(f"{message} (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' or 'n'")

    def extend_existing_data(self) -> bool:
        """Add more data to existing graph."""
        print("\n📈 Extending existing knowledge graph...")
        print("This feature is coming soon!")
        return True

    def run_test_queries(self) -> bool:
        """Run test queries against the graph."""
        print("\n🧪 Running test queries...")
        return self.run_script("3_query_knowledge_graph.py")

    def backup_data(self) -> bool:
        """Backup current graph data."""
        print("\n💾 Backing up data...")
        print("This feature is coming soon!")
        return True

    def load_sample_data(self) -> bool:
        """Load pre-built sample data."""
        print("\n📦 Loading sample data...")
        return self.run_script("1_generate_data.py")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="GraphRAG Educational Setup System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 0_setup.py                # Interactive mode
  python 0_setup.py --init          # Initialize Neo4j and directories only
  python 0_setup.py --fresh         # Fresh installation
  python 0_setup.py --continue      # Use existing data
  python 0_setup.py --check         # Check status only
  python 0_setup.py --learning      # Educational mode with explanations
        """
    )

    parser.add_argument('--init', action='store_true',
                       help='Initialize Neo4j and project structure only')
    parser.add_argument('--fresh', action='store_true',
                       help='Force fresh setup (clears existing data)')
    parser.add_argument('--continue', action='store_true', dest='continue_mode',
                       help='Continue with existing data')
    parser.add_argument('--check', action='store_true',
                       help='Check status only')
    parser.add_argument('--learning', action='store_true',
                       help='Enable educational explanations')

    args = parser.parse_args()

    # Determine mode
    if args.init:
        mode = SetupMode.INIT
    elif args.fresh:
        mode = SetupMode.FRESH
    elif args.continue_mode:
        mode = SetupMode.CONTINUE
    elif args.check:
        mode = SetupMode.CHECK
    elif args.learning:
        mode = SetupMode.LEARNING
    else:
        mode = SetupMode.INTERACTIVE

    return mode, args.learning

def main():
    """Main entry point."""
    try:
        mode, learning_mode = parse_arguments()
        setup = GraphRAGSetup(mode=mode, learning_mode=learning_mode)
        success = setup.main()

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()