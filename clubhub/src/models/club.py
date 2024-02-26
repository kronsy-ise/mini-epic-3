from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db
import models

class Club:
    id: int
    name: str 
    description: str
    validity: str
    coord: int 

    def __init__(self, id, name, description, validity, coord) -> None:
        self.id = id
        self.name = name 
        self.description = description
        self.validity = validity
        self.coord = coord

    def __repr__(self) -> str:
        return f"Club {self.name} <{self.id}>"

    def get_memberships(self) -> List[models.User]:

        cur = db.cursor()

        cur.execute("SELECT user_id, club_id, role FROM Memberships WHERE club_id = %s", (self.id,))
        entries = cur.fetchall()
        Members = [models.User.fetch(entry[0]) for entry in entries]   
        return Members
    
    def upcomming_events(self) -> List[models.Event]:
        cur = db.cursor()

        cur.execute("SELECT event_id, name, description, date, location, club_id FROM Events WHERE club_id = %s", (self.id,))
        entries = cur.fetchall()
        Events = [models.Event(*entry) for entry in entries]   
        return Events
    
    @staticmethod
    def fetch(club_id : int) -> Optional[Club]:
        """
        Fetches a Club object from the database based on the club_id.

        Args:
            club_id (int): The id of the club to fetch.

        Returns:
            Optional[Club]: The fetched Club object if found, None otherwise.
        """
        cur = db.cursor()

        cur.execute("SELECT name, description, validity, user_id FROM Clubs WHERE club_id = %s", (club_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return Club(club_id, entry[0], entry[1], entry[2], entry[3])

    @staticmethod
    def return_list() -> List[Club]:
        """
        Returns a list of Club objects with all clubs data.

        Returns:
            List[Club]: A list of Club objects.
        """
        cur = db.cursor()

        cur.execute("SELECT club_id, name, description, validity, user_id FROM Clubs ORDER BY club_id")
        entries = cur.fetchall()
        print(entries)
        return [Club(*entry) for entry in entries]

    @staticmethod
    def add_club(name, description, coord):
        """
        Adds a new club to the database.

        Args:
            name (str): The name of the club.
            description (str): The description of the club.
            coord (int): The coordinator of the club.

        Returns:
            str: A success message indicating the club was added successfully.
        """
        cur = db.cursor()

        cur.execute("INSERT INTO Clubs(name, description, validity, user_id) VALUES (%s, %s, %s, %s)", (name, description, 'valid', coord))
        db.commit()
        return "Club added successfully"
    
    @staticmethod
    def delete_club(club_id):
        """
        Deletes a club from the database.

        Args:
            club_id (int): The id of the club to delete.

        Returns:
            str: A success message indicating the club was deleted successfully.
        """
        cur = db.cursor()

        cur.execute("DELETE FROM Clubs WHERE club_id = %s", (club_id,))
        db.commit()
        return "Club deleted successfully"
    
    @staticmethod
    def return_unapproved_clubs():
        """
        Returns the count of unapproved clubs.

        Returns:
            int: The count of unapproved clubs.
        """
        clubs = Club.return_list()
        count = 0
        for club in clubs:
            if club.validity == 'invalid':
                count+=1
        return count
        