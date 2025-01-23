from collections import defaultdict
from typing import Any, Optional, Protocol
import datetime
import json
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
        # Searching for a specific user.
        if query.identity_name and query.value:
            params = {
                f"identities.{query.identity_name}.value": query.value,
            }
            return self.client.cis.users.find(params).to_list()
        # Where users have an identity that's active.
        if query.identity_name:
            params = {
                f"identities.{query.identity_name}.value": {
                    "$exists": True,
                    "$nin": ["", None],
                },
            }
            return self.client.cis.users.find(params).to_list()
        return []

    def health(self) -> bool:
        if self.client.nodes:
            return True
        raise NotConnected("Could not connect to Mongo")


class BigTable:
    client: bigtable.client.Client
    instance: bigtable.instance.Instance
    users: bigtable.table.Table

    def __init__(self) -> None:
        self.client = bigtable.client.Client()
        self.instance = self.client.instance("cis")
        self.users = self.instance.table("users")
        raise NotImplementedError("We'd need to re-think our schema with BigTable, something we're not prepared to do at this time.")

    def get(self, username: str) -> Optional[User]:
        raise NotImplementedError("BigTable get")

    def update(self, user: User) -> None:
        timestamp = datetime.datetime.utcnow()
        user_document = user.dict()
        row = self.users.direct_row(user_document.pop("username"))
        for column_family, value in user_document.items():
            match value:
                case dict(v):
                    row.set_cell(column_family, column_family, json.dumps(value), timestamp)
                case v:
                    row.set_cell(column_family, column_family, value, timestamp)

    def search(self, query: UserFilterParams) -> list[User]:
        raise NotImplementedError("BigTable search")

    def health(self) -> bool:
        raise NotImplementedError("BigTable health")
