from __future__ import annotations
from enum import Enum
from typing import Optional

from globals import db
class UserKind(Enum):
    Unapproved = "unapproved"
    Coordinator = "coordinator"
    User = "user"
    Admin = "admin"
    
    @staticmethod 
    def from_str(s : str) -> UserKind:
        if s == "unapproved": return UserKind.Unapproved
        elif s == "coordinator": return UserKind.Coordinator
        elif s == "user": return UserKind.User
        elif s == "admin": return UserKind.Admin
        
        raise Exception("Unknown kind")

class User:
    username : str 
    name : str
    email : str 
    mobile : str
    kind : UserKind

    def __init__(self, username, name, kind, email, mobile) -> None:
        self.username = username
        self.name = name 
        self.kind = kind
        self.email = email
        self.mobile = mobile

    def __repr__(self) -> str:
        return f"User {self.name} <{self.username}> kind={self.kind}"

    @staticmethod
    def fetch(id : int) -> Optional[User]:

        cur = db.cursor()

        cur.execute("SELECT username, name, is_admin, user_kind, email, mobile FROM Users WHERE id = %s", (id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return User(entry[0], entry[1], entry[2], UserKind.from_str(entry[3]), entry[4], entry[5])
