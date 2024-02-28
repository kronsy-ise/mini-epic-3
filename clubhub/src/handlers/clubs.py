from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import UserKind,User
import util
from models.club import Club
from models.event import Event
import navigations
clubs_app = Blueprint('clubs_app', __name__)

@clubs_app.get("/clubs")
def clubs():
    auth_user = util.verify_session()
    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different club page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        clubs = Club.return_list()
        event_count = Event.event_count()
        # Fetch all the coordinator details
        coords = {club.coord: User.fetch(club.coord) for club in clubs}
        club_count=Club.club_count()
        print(club_count)
        unapproved_clubs = Club.return_unapproved_clubs()
        unappointed_coords = User.unappointed_coords()
        return render_template("admin/clubs.html",clubs=clubs,users=users,
                    club_count=club_count,unapproved_clubs=unapproved_clubs
                    ,unappointed_coords=unappointed_coords,coords=coords,
                    event_count=event_count)
    elif auth_user.kind == UserKind.Student:
        all_clubs = Club.return_list()
        print(all_clubs)
        return render_template("user/clubs.html",
            navigations=navigations.USER_NAV,
            user_kind="Student",
            clubs = all_clubs)
    elif auth_user.kind == UserKind.Coordinator:
            return render_template("coordinator/clubs.html",
            navigations=navigations.COORDINATOR_NAV,
            user_kind = "Coordinator",
            current_user=auth_user
            
            )
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

@clubs_app.post("/clubs/<int:club_id>/join")
def join_club(club_id):
    auth_user = util.verify_session()
    if auth_user == None:
        return redirect("/")

    if auth_user.kind != UserKind.Student:
        return "Only students may join clubs", 403
    

    try:
        Club.request_membership(auth_user.user_id, club_id)
    except Exception as e:
        print(e)
        return "Internal Server error", 500

    return "Successfully requested to join club", 200

@clubs_app.post("/clubs/<int:club_id>/approve/<int:user_id>")
def approve_club(club_id, user_id):
    auth_user = util.verify_session()
    if auth_user == None:
        return redirect("/")

    if auth_user.kind != UserKind.Coordinator:
        return "Only coordinators may approve", 403
    

    try:
        Club.approve_membership(user_id, club_id)
    except Exception as e:
        return "Internal Server error", 500

    return "Successfully requested to join club", 200

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

