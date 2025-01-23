from collections import defaultdict
from typing import Any, Optional, Protocol
import logging
from pymongo import MongoClient
from google.cloud import bigtable  # type: ignore
from spike_docdb_blowout.models import *


logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class NotConnected(Error):
    pass


class DocDB(Protocol):
    def get(self, username: str) -> Optional[User]: ...
    def update(self, user: User) -> None: ...
    def search(self, query: UserFilterParams) -> list[User]: ...
    def health(self) -> bool: ...


class Mongo:
    client: MongoClient

    def __init__(self, connection_uri: str) -> None:
        self.client = MongoClient(connection_uri)

    def get(self, username: str) -> Optional[User]:
        return self.client.cis.users.find_one({"username": username})

    def update(self, user: User) -> None:
        self.client.cis.users.update_one(
            {"username": user.username},
            {"$set": user.dict()},
            upsert=True,
        )

    def search(self, query: UserFilterParams) -> list[User]:
        params: dict[str, Any] = defaultdict(lambda: defaultdict(dict))
        if query.username:
            params["username"] = query.username
        params["connections"]["$elemMatch"]["is_verified"] = query.is_verified
        if query.connection_kind:
            params["connections"]["$elemMatch"]["kind"] = query.connection_kind
        return self.client.cis.users.find(params).to_list()

    def health(self) -> bool:
        if self.client.nodes:
            return True
        raise NotConnected("Could not connect to Mongo")
