import datetime
from dataclasses import dataclass


@dataclass
class Session:
    session_id: str
    login: str
    start_session_time: datetime.datetime
    live_up_time: datetime.datetime

    def __init__(self, params):
        self.session_id, self.login, self.start_session_time, self.live_up_time = params
