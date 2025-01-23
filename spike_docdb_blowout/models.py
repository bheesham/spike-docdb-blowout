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


class GitHubIdV3(BaseModel):
    value: Optional[str]


class FirefoxAccountId(BaseModel):
    value: Optional[str]


class Identities(BaseModel):
    github_id_v3: Optional[GitHubIdV3] = None
    firefox_accounts_id: Optional[FirefoxAccountId] = None


class User(BaseModel):
    username: str
    email: str
    access_information: AccessInformation
    hris: HRInformation
    identities: Identities


class IdentityKind(enum.StrEnum):
    GitHub = "github_id_v3"
    FirefoxAccount = "firefox_accounts_id"


class UserFilterParams(BaseModel):
    identity_name: IdentityKind
    value: Optional[str] = None
