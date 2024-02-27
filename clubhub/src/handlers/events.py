from __future__ import annotations
from flask import Blueprint, redirect, render_template, request
from globals import db
from models.user import UserKind,User
import util
from models.club import Club
from models.event import Event
events_app = Blueprint('events_app', __name__)

@events_app.get("/events")
def events():
    auth_user = util.verify_session()
    print(auth_user.kind)

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different home page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        clubs = Club.return_list()
        club_count=Club.club_count()
        events = Event.return_list()
        event_count = Event.event_count()
        unapproved_event_memberships = Event.unapproved_event_memberships()
        return render_template("admin/events.html",clubs=clubs,users=users,events=events,event_count=event_count,
                               unapproved_event_memberships=unapproved_event_memberships,club_count=club_count)
    elif auth_user.kind == UserKind.Student:
        return render_template("user/events.html")
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/events.html")
    else:
        return render_template("awaiting_approval.html")
    

@events_app.route("/CreateEvent", methods=['GET', 'POST'])
def create_event():
    club_id = request.form.get('club_id')
    name = request.form.get('name')
    description = request.form.get('description')
    date = request.form.get('datetime')
    venue = request.form.get('venue')    
    Event.add_event(club_id, name, description, date, venue)
    return redirect("/clubs")

