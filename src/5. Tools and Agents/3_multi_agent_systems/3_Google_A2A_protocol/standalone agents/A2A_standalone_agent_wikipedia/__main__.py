import logging
import os
import tomli

import click

from agent import Agent
from task_manager import AgentTaskManager
from common.server import A2AServer
from common.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    MissingAPIKeyError,
)
from common.utils.push_notification_auth import PushNotificationSenderAuth
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open("agent_config.toml", "rb") as f:
    config = tomli.load(f)


@click.command()
@click.option('--host', 'host', default=config["server"]["default_host"])
@click.option('--port', 'port', default=config["server"]["default_port"])
def main(host, port):
    """Starts the Wikipedia Agent server."""
    try:
        if not os.getenv('GOOGLE_API_KEY'):
            raise MissingAPIKeyError(
                'GOOGLE_API_KEY environment variable not set.'
            )

        # Create capabilities from config
        capabilities = AgentCapabilities(
            streaming=config["agent_card"]["capabilities"]["streaming"],
            pushNotifications=config["agent_card"]["capabilities"]["pushNotifications"]
        )
        
        # Create skills from config
        skills = []
        for skill_config in config["agent_card"]["skills"]:
            skill = AgentSkill(
                id=skill_config["id"],
                name=skill_config["name"],
                description=skill_config["description"],
                tags=skill_config["tags"],
                examples=skill_config["examples"],
            )
            skills.append(skill)
        
        # Create agent card from config
        agent_card = AgentCard(
            name=config["agent_card"]["name"],
            description=config["agent_card"]["description"],
            url=f'http://{host}:{port}/',
            version=config["agent_card"]["version"],
            defaultInputModes=Agent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=Agent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=skills,
        )

        notification_sender_auth = PushNotificationSenderAuth()
        notification_sender_auth.generate_jwk()
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(
                agent=Agent(),
                notification_sender_auth=notification_sender_auth,
            ),
            host=host,
            port=port,
        )

        server.app.add_route(
            '/.well-known/jwks.json',
            notification_sender_auth.handle_jwks_endpoint,
            methods=['GET'],
        )

        logger.info(f'Starting server on {host}:{port}')
        server.start()
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
