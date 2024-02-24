from __future__ import annotations
from enum import Enum
from typing import Optional
from typing import List
from globals import db

class Club:
    id: int
    name : str 
    description : str
    validity : str
    coord : int 

    def __init__(self, id, name, description, validity, coord) -> None:
        self.id = id
        self.name = name 
        self.description = description
        self.validity = validity
        self.coord = coord

    def __repr__(self) -> str:
        return f"Club {self.name} <{self.id}>"
    @staticmethod
    def fetch(club_id : int) -> Optional[Club]:

        cur = db.cursor()

        cur.execute("SELECT name, description, validity, user_id FROM Clubs WHERE club_id = %s", (club_id,))
        entry = cur.fetchone()

        if entry == None:
            return None 
        else:
            return Club(club_id, entry[0], entry[1], entry[2], entry[3])

    @staticmethod
    def return_list() -> List[Club]:
        # Returns a list of Club objects with all clubs data;
        cur = db.cursor()

        cur.execute("SELECT club_id, name, description, validity, user_id FROM Clubs")
        entries = cur.fetchall()
        print(entries)
        return [Club(*entry) for entry in entries]

    @staticmethod
    def add_club(name, description, coord):
        cur = db.cursor()

        cur.execute("INSERT INTO Clubs(name, description, validity, user_id) VALUES (%s, %s, %s, %s)", (name, description, 'valid', coord))
        db.commit()
        return "Club added successfully"
    
    @staticmethod
    def delete_club(club_id):
        cur = db.cursor()

        cur.execute("DELETE FROM Clubs WHERE club_id = %s", (club_id,))
        db.commit()
        return "Club deleted successfully"