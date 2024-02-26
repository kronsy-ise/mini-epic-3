from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db
import models
class Event:
    def __init__(self, event_id, club_id, name, description, date, venue, ):
        self.event_id = event_id
        self.name = name
        self.club_id = club_id
        self.description = description
        self.date = date
        self.venue = venue


    def __repr__(self) -> str:
            return f"Event {self.name} <{self.id}>"

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
    def add_event(club_id, name, description, date, venue, time):
       
        cur = db.cursor()

        cur.execute("INSERT INTO Events(club_id, name, description, date, venue) VALUES (%s, %s, %s, %s, %s, %s)", (club_id, name, description, date, venue, time))
        db.commit()
        return "Event added successfully"
    
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
    def fetch_club_members(club_id: int)-> List[models.User]:
        cur = db.cursor()
        cur.execute("SELECT user_id, username, name, user_kind, email, mobile FROM Users WHERE user_id IN (SELECT user_id FROM CLUB_MEMBERSHIP WHERE club_id = %s)", (club_id,))
        entries = cur.fetchall()
        return [models.User(*entry) for entry in entries]