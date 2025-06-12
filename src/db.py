from datetime import datetime
from re import S
from typing import TypedDict
from tinydb import TinyDB, Query
from tinydb.operations import add
from tinydb_serialization.serializers import DateTimeSerializer
import logging

from tinydb_serialization import SerializationMiddleware
logger = logging.getLogger(__name__)

serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'datetime')
DB = TinyDB("db.json", storage=serialization)

Q = Query()

class LogDict(TypedDict):
    pos: str
    epoch: datetime
    message: str

class PhoneDict(TypedDict):
    name: str
    fmp_name: str
    log: list[LogDict]


class Phone:
    name_id: str
    def __init__(self, name_id: str, fmp_name: str | None = None, db: TinyDB = DB):
        self.db = db
        self.name_id = name_id
        if not self.db.contains(Q.name == name_id):
            self.db.insert({"name": name_id, "fmp_name": fmp_name or name_id, "log": []})

    def add_log(self, log: LogDict):
        if not self.db.contains(Q.name == self.name_id):
            logger.error(f"Phone {self.name_id} does not exist in the database.")
            return
        self.db.update(add("log", [log]), Q.name == self.name_id)
    
    @property
    def last_log(self) -> LogDict | None:
        log = self.db.get(Q.name == self.name_id)["log"] # type: ignore
        return log[-1] if log else None
    
    @property
    def doc(self) -> PhoneDict:
        return self.db.get(Q.name == self.name_id) # type: ignore