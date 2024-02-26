from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import UserKind,User
import util
from models.club import Club
clubs_app = Blueprint('clubs_app', __name__)

@clubs_app.get("/clubs")
def clubs():
    auth_user = util.verify_session()
    print(auth_user.kind)

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different club page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        clubs = Club.return_list()
        club_count=Club.club_count()
        print(club_count)
        unapproved_clubs = Club.return_unapproved_clubs()
        unappointed_coords = User.unappointed_coords()
        return render_template("admin/clubs.html",clubs=clubs,users=users,
                    club_count=club_count,unapproved_clubs=unapproved_clubs
                    ,unappointed_coords=unappointed_coords)
    elif auth_user.kind == UserKind.Student:
        return render_template("user/clubs.html")
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/clubs.html")
    else:
        return render_template("awaiting_approval.html")
    

@clubs_app.route("/CreateClub", methods=['GET', 'POST'])
def create_club():
    name = request.form.get('name')
    description = request.form.get('description')
    coord = request.form.get('coord')
    
    newclub = Club.add_club(name, description, coord)
    #if newclub is not null then
    if newclub != None:
        print(newclub,"Club added successfully")
    else:
        print("Adding club failed")
    return redirect("/clubs")

@clubs_app.route("/delete-club/<int:club_id>", methods=['POST'])
def delete_club(club_id):
    Club.delete_club(club_id)
    return redirect("/clubs")

@clubs_app.route('/manage-club/<int:club_id>', methods=['GET'])
def manage_club(club_id):
    # Query the database for the club information
    club = Club.fetch(club_id)
    memberships = club.get_memberships()
    upcoming_events = club.upcomming_events()
    # Pass the data to the template
    return render_template('manage_club.html', club=club, upcoming_events=upcoming_events, memberships=memberships)