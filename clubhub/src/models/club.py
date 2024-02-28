from __future__ import annotations
from typing import Optional
from typing import List
from globals import db
import models

class Club:
    club_id: int
    name: str 
    description: str
    validity: str
    coord: int 

    def __init__(self, club_id, name, description, validity, coord) -> None:
        # Initialize Club object with provided attributes
        self.club_id = club_id
        self.name = name 
        self.description = description
        self.validity = validity
        self.coord = coord

    def __repr__(self) -> str:
        # Return a string representation of the Club object
        return f"Club {self.name} <{self.club_id}>"

    
    def get_memberships(self) -> List[models.User]:
        # Retrieve all memberships associated with the club
        cur = db.cursor()
        cur.execute("SELECT user_id, club_id, role FROM Memberships WHERE club_id = %s", (self.club_id,))
        entries = cur.fetchall()
        Members = [models.User.fetch(entry[0]) for entry in entries]   
        return Members
    
    @staticmethod
    def approve_membership(user_id: int, club_id: int):
        # Approve a user's membership to a club
        cur = db.cursor()
        try:
            cur.execute("UPDATE CLUB_MEMBERSHIP SET status = 'approved' WHERE user_id = %s AND club_id = %s", (user_id, club_id))
        except Exception as e:
            print("Could not approve membership")
            db.rollback()
            raise e
        db.commit()

    @staticmethod
    def reject_membership(user_id: int, club_id: int):
        # Reject a user's membership to a club
        cur = db.cursor()
        try:
            cur.execute("UPDATE CLUB_MEMBERSHIP SET status = 'rejected' WHERE user_id = %s AND club_id = %s", (user_id, club_id))
        except Exception as e:
            print("Could not reject membership")
            db.rollback()
            raise e
        db.commit()
        
    @staticmethod 
    def fetch_membership_requests():
        # Retrieve all membership requests
        cur = db.cursor()
        cur.execute("SELECT user_id, club_id FROM CLUB_MEMBERSHIP WHERE status = 'pending'")
        entries = cur.fetchall()
        return [{"user_id": entry[0], "club_id": entry[1]} for entry in entries]
