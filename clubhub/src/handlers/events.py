from __future__ import annotations
from flask import Blueprint, redirect, render_template, request
from globals import db
from models.user import UserKind,User
import util
from models.club import Club
from models.event import Event
import navigations
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

        memberships = User.get_user_clubs(auth_user.user_id)
        membership_ids = [m.club_id for m in memberships]
        all_events = Event.return_list()

        club_events = [e for e in all_events if e.club_id in membership_ids]
        other_events = [e for e in all_events if e.club_id not in membership_ids]
        
        print(membership_ids)
        return render_template("user/events.html",
         navigations=navigations.USER_NAV,
         user_kind="Student",
         club_events=club_events,
         other_events=other_events)
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/events.html",
            navigations=navigations.COORDINATOR_NAV,
            user_kind = "Coordinator")
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
    return redirect("/events")

@events_app.post("/events/<int:event_id>/join")
def join_event(event_id):
    auth_user = util.verify_session()

    if auth_user == None:
        return redirect("/")
    if auth_user.kind != UserKind.Student:
        return "Only users may join events", 400
    user_id = auth_user.user_id

    event = Event.fetch(event_id)

    if event is None:
        return "Event Not Found", 404
    
    club = event.club_id

    user_clubs = User.get_user_clubs(user_id)

    if club in user_clubs:
        # Join Directly to the event 

        Event.join(user_id, event_id)
        return "Successsfully joined event", 200
    else:
        # Create a join request to the event
        Event.request_join(user_id, event_id)
        return "Successsfully requested to join event", 200


