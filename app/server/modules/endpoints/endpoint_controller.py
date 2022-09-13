# Import external modules
from enum import Enum
import random
from app.server.modules.endpoints.file_creation_event import FileCreationEvent
from faker import Faker
from faker.providers import internet, lorem


# Import internal modules
from flask import current_app
from app.server.models import *
from app.server.modules.logging.uploadLogs import LogUploader
from app.server.modules.clock.Clock import Clock
from app.server.utils import *

# instantiate faker
fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)


def upload_endpoint_event_to_azure(event: FileCreationEvent, table_name: str = "FileCreationEvents") -> None:
    """
    A function to upload a FileCreationEvent to ADX
    References global log_uploader to queue log rows for uploading
    """
    from app.server.game_functions import log_uploader
    log_uploader.send_request(
        data=[event.stringify()],
        table_name=table_name)
