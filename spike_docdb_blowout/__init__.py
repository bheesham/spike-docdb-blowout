import os
from typing import Annotated, Optional
from fastapi import FastAPI, HTTPException, Query
from spike_docdb_blowout.models import *
from spike_docdb_blowout import docdb


class Error(Exception):
    pass


class Configuration(Error):
    pass


app = FastAPI(
    title="Spike: DocDB Blowout",
    summary="""An example API to "measure" various document databases.""",
)

client: docdb.DocDB


try:
    if os.environ["DRIVER"] == "mongodb":
        try:
            client = docdb.Mongo(os.environ["MONGODB_URI"])
        except KeyError as exc:
            raise Configuration("MONGODB_URI environment variable not found") from exc
    elif os.environ["DRIVER"] == "bigtable":
        client = docdb.BigTable()
    else:
        raise Configuration("Invalid docdb driver")
except KeyError as exc:
    raise Configuration("DRIVER environment variable not found") from exc


@app.get(
    "/users",
    summary="Searches for users",
)
def user_search(
    query: Annotated[UserFilterParams, Query()],
) -> list[User]:
    """
    It might be easier to use `Request` to keep compatibility with CISv1.
    """
    return client.search(query)


@app.put(
    "/users",
    summary="Create/update a user",
)
def user_put(user: User) -> None:
    client.update(user)


@app.get(
    "/users/{username}",
    summary="Details about a specific user",
)
def users_get(username: str) -> User:
    if (user := client.get(username)) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/health", include_in_schema=False)
def health() -> None:
    try:
        client.health()
    except docdb.Error as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
