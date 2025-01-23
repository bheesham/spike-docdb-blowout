import enum
from typing import Optional
from pydantic import BaseModel


class AccessInformation(BaseModel):
    """
    Various places where we get group information from.

    * ldap: LDAP!
    * mozillians: peoplemo.
    """

    ldap: dict[str, Optional[str]]
    mozillians: dict[str, Optional[str]]


class Worker(enum.StrEnum):
    Employee = enum.auto()
    Manager = enum.auto()
    Director = enum.auto()


class HRInformation(BaseModel):
    employee_id: str
    worker_type: Worker
    primary_work_email: str
    managers_primary_work_email: Optional[str]


class ConnectionKind(enum.StrEnum):
    GitHub = enum.auto()
    FirefoxAccount = enum.auto()
    LDAP = enum.auto()


class Connection(BaseModel):
    kind: ConnectionKind
    username: str
    is_verified: bool


class User(BaseModel):
    username: str
    email: str
    access_information: AccessInformation
    hris: HRInformation
    connections: list[Connection]


class UserFilterParams(BaseModel):
    username: Optional[str] = None
    connection_kind: Optional[ConnectionKind] = None
    is_verified: Optional[bool] = False
