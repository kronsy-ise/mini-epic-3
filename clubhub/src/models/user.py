from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db
import models
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
    user_id: int
    username: str 
    name: str
    email: str 
    mobile: str
    kind: UserKind

    def __init__(self, user_id, username, name, kind, email, mobile) -> None:
        self.user_id = user_id
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

        cur.execute("SELECT user_id, username, name, user_kind, email, mobile FROM Users WHERE user_id = %s", (user_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return User(entry[0], entry[1], entry[2], UserKind.from_str(entry[3]), entry[4], entry[5])
    
    @staticmethod
    def fetch_unapproved_users() -> List[User]:
        cur = db.cursor()
        cur.execute("SELECT user_id, username, name, user_kind, email, mobile FROM Users WHERE user_kind = 'unapproved'")
        entries = cur.fetchall()
        return [User(*entry) for entry in entries]
    
    @staticmethod
    def return_list() -> List[List]:
        # Returns a list of lists of all users data in the form of strings;
        cur = db.cursor()
        #return an ordered list of user information so the table is ordered by user_id
        cur.execute("SELECT user_id,username, name, user_kind, email,mobile FROM Users ORDER BY user_id ")
        entries = cur.fetchall()
        return [list(entry) for entry in entries]
    @staticmethod
    def unappointed_coords() -> List[List]:
        cur = db.cursor()
        cur.execute("""
        SELECT Users.user_id, Users.username, Users.name, Users.user_kind, Users.email, Users.mobile 
        FROM Users 
        LEFT JOIN Clubs ON Users.user_id = Clubs.user_id
        WHERE Users.user_kind = 'coordinator' AND Clubs.user_id IS NULL
        ORDER BY Users.user_id
        """)
        entries = cur.fetchall()
        return [list(entry) for entry in entries]
    
    @staticmethod   
    def get_user_clubs(user_id) -> List[models.club.Club]:
        # Retrieve all clubs associated with the user
        cur = db.cursor()
        cur.execute("SELECT club_id FROM CLUB_MEMBERSHIP WHERE user_id = %s AND status = 'approved'", (user_id,))
        entries = cur.fetchall()
        clubs = [models.club.Club.fetch(entry[0]) for entry in entries]
        return clubs
    
    @staticmethod
    def get_user_events(user_id) -> List[models.Event]:
        # Retrieve all events associated with the user
        cur = db.cursor()
        cur.execute("SELECT event_id FROM EVENT_PARTICIPATION WHERE user_id = %s", (user_id,))
        entries = cur.fetchall()
        events = [models.Event.fetch(entry[0]) for entry in entries]
        return events