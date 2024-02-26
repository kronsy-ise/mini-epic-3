from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db
import models
from datetime import datetime

class Club:
    id: int
    name: str 
    description: str
    validity: str
    coord: int 

    def __init__(self, id, name, description, validity, coord) -> None:
        # Initialize Club object with provided attributes
        self.id = id
        self.name = name 
        self.description = description
        self.validity = validity
        self.coord = coord

    def __repr__(self) -> str:
        # Return a string representation of the Club object
        return f"Club {self.name} <{self.id}>"

    
    def get_memberships(self) -> List[models.User]:
        # Retrieve all memberships associated with the club
        cur = db.cursor()
        cur.execute("SELECT user_id, club_id, role FROM Memberships WHERE club_id = %s", (self.id,))
        entries = cur.fetchall()
        Members = [models.User.fetch(entry[0]) for entry in entries]   
        return Members
    
    def upcomming_events(self) -> List[models.Event]:
        # Retrieve all upcoming events associated with the club
        cur = db.cursor()
        cur.execute("SELECT event_id, name, description, date, location, club_id FROM Events WHERE club_id = %s", (self.id,))
        entries = cur.fetchall()
        Events = [models.Event(*entry) for entry in entries]   
        return Events
    
  
    
    @staticmethod
    def fetch(club_id : int) -> Optional[Club]:
        # Fetch a club from the database based on club_id
        cur = db.cursor()
        cur.execute("SELECT name, description, validity, user_id FROM Clubs WHERE club_id = %s", (club_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return Club(club_id, entry[0], entry[1], entry[2], entry[3])

    @staticmethod
    def return_list() -> List[Club]:
        # Return a list of all clubs in the database
        cur = db.cursor()
        cur.execute("SELECT club_id, name, description, validity, user_id FROM Clubs ORDER BY club_id")
        entries = cur.fetchall()
        print(entries)
        return [Club(*entry) for entry in entries]

    @staticmethod
    def add_club(name, description, coord):
        # Add a new club to the database
        cur = db.cursor()
        cur.execute("INSERT INTO Clubs(name, description, validity, user_id) VALUES (%s, %s, %s, %s)", (name, description, 'valid', coord))
        db.commit()
        return "Club added successfully"
    
    @staticmethod
    def delete_club(club_id):
        # Delete a club from the database based on club_id
        cur = db.cursor()
        cur.execute("DELETE FROM Clubs WHERE club_id = %s", (club_id,))
        db.commit()
        return "Club deleted successfully"
    
    @staticmethod
    def return_unapproved_clubs():
        # Return the count of unapproved clubs in the database
        clubs = Club.return_list()
        count = 0
        for club in clubs:
            if club.validity == 'invalid':
                count+=1
        return count
    
    @staticmethod
    def fetch_club_members(club_id: int)-> List[models.User]:
        # Fetch all members of a club based on club_id
        cur = db.cursor()
        cur.execute("SELECT user_id, username, name, user_kind, email, mobile FROM Users WHERE user_id IN (SELECT user_id FROM CLUB_MEMBERSHIP WHERE club_id = %s)", (club_id,))
        entries = cur.fetchall()
        return [models.User(*entry) for entry in entries]
    
    def club_count():
        # Return the count of clubs in the database
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM Clubs")
        count = cur.fetchone()
        return count[0]