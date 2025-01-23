import os
from typing import Annotated, Optional
from spike_docdb_blowout.models import *
from spike_docdb_blowout import docdb

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Spike: DocDB Blowout",
    summary="""An example API to "measure" various document databases.""",
)

client: docdb.DocDB

if os.environ["DRIVER"] == "mongodb":
    client = docdb.Mongo(os.environ["MONGODB_URI"])
else:
    raise ValueError("Invalid docdb driver")

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
        raise HTTPException(status_code=500, detail=str(exc))
