from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db
class UserKind(Enum):
    Unapproved = "unapproved"
    Coordinator = "coordinator"
    Student = "student"
    Admin = "admin"
    
    @staticmethod 
    def from_str(s : str) -> UserKind:
        if s == "unapproved": return UserKind.Unapproved
        elif s == "coordinator": return UserKind.Coordinator
        elif s == "student": return UserKind.Student
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
    def fetch(user_id : int) -> Optional[User]:

        cur = db.cursor()

        cur.execute("SELECT username, name, user_kind, email, mobile FROM Users WHERE user_id = %s", (user_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return User(entry[0], entry[1], UserKind.from_str(entry[2]), entry[3], entry[4])
    
    @staticmethod
    def return_list() -> List[List]:
        # Returns a list of lists of all users data in the form of strings;
        cur = db.cursor()

        cur.execute("SELECT user_id,username, name, user_kind, email,mobile FROM Users")
        entries = cur.fetchall()
        return [list(entry) for entry in entries]
