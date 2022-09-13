# Import external modules
from enum import Enum
import random
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



def upload_endpoint_event_to_azure(event, table_name="FileCreationEvents"):

    from app.server.game_functions import log_uploader
    log_uploader.send_request(
            data = [event.stringify()],
            table_name= table_name)
