from __future__ import annotations
from typing import Optional
from typing import List
from globals import db
import models
class Event:
    class Events:
        event_id: int
        club_id: int
        name: str 
        description: str
        date: str
        venue: str	 
    
    def __init__(self, event_id, club_id, name, description, date, venue, ):
        self.event_id = event_id
        self.name = name
        self.club_id = club_id
        self.description = description
        self.date = date
        self.venue = venue


    def __repr__(self) -> str:
            return f"Event {self.name} <{self.event_id}>"

    @staticmethod
    def fetch(event_id : int) -> Optional[Event]:
        cur = db.cursor()

        cur.execute("SELECT club_id, name, description, date, venue FROM Events WHERE event_id = %s", (event_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return Event(event_id, *entry)

    @staticmethod
    def return_list() -> List[Event]:
       
        cur = db.cursor()

        cur.execute("SELECT event_id, club_id, name, description, date, venue FROM Events ORDER BY event_id")
        entries = cur.fetchall()
        return [Event(*entry) for entry in entries]

    @staticmethod
    def join(user_id : int, event_id : int):
        cur = db.cursor()

        cur.execute("INSERT INTO EVENT_PARTICIPATION(event_id, user_id, status) VALUES (%s, %s, 'approved')", (event_id, user_id))

        db.commit()
        pass 

    @staticmethod
    def request_join(user_id : int, event_id : int):
        cur = db.cursor()

        cur.execute("INSERT INTO EVENT_PARTICIPATION(event_id, user_id, status) VALUES (%s, %s, 'pending')", (event_id, user_id))

        db.commit()
        pass 

    @staticmethod
    def add_event(club_id, name, description, date, venue):
        cur = db.cursor()
        cur.execute("INSERT INTO Events(club_id, name, description, date, venue) VALUES (%s, %s, %s, %s, %s)", (club_id, name, description, date, venue))
        db.commit()
        return Event.fetch(club_id)
    
    @staticmethod
    def delete_event(event_id):
        
        cur = db.cursor()

        cur.execute("DELETE FROM Events WHERE event_id = %s", (event_id,))
        db.commit()
        return "Event deleted successfully"

    @staticmethod
    def fetch_club_events(club_id : int) -> List[Event]:
        cur = db.cursor()
        cur.execute("SELECT event_id, name, description, date, venue, club_id FROM Events WHERE club_id = %s", (club_id,))
        entries = cur.fetchall()
        return [Event(*entry) for entry in entries]
    
    @staticmethod
    def fetch_event_members(event_id: int) -> List[models.User]:
        cur = db.cursor()
        cur.execute("SELECT user_id, username, name, user_kind, email, mobile FROM Users WHERE user_id IN (SELECT user_id FROM EVENT_PARTICIPATION WHERE event_id = %s)", (event_id,))
        entries = cur.fetchall()
        return [models.User(*entry) for entry in entries]
    
    @staticmethod
    def event_count():
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM Events")
        count = cur.fetchone()
        return count[0]
    
    @staticmethod
    def unapproved_event_memberships():
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM EVENT_PARTICIPATION WHERE status = 'pending' ")
        count = cur.fetchone()
        return count[0]
