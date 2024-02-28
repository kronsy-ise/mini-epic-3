from __future__ import annotations
from flask import Blueprint, make_response, request, render_template, session, redirect
from globals import db
from models.user import User
from models.user import UserKind
import psycopg2.errors as pgerrors
import util
from models.user import User
import os
from models.club import Club
import navigations
from models.event import Event
home_app = Blueprint('home_app', __name__)


@home_app.get("/home")
def homepage():
    auth_user = util.verify_session()

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different home page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        num_lists = len(User.return_list())
        coord_count = 0
        student_count = 0
        club_count=Club.club_count()
        event_count = Event.event_count()

        for user in users:
            if user[3] == 'coordinator':
                coord_count += 1
            elif user[3] == 'student':
                student_count +=1
                
        return render_template("admin/home.html",users=users ,user_count=num_lists,
                               coord_count=coord_count,student_count=student_count,
                               unapproved_count=num_lists-coord_count-student_count-1,
                               club_count=club_count,event_count=event_count)   

    elif auth_user.kind == UserKind.Student:
        memberships = User.get_user_clubs(auth_user.user_id)
        events = User.get_user_events(auth_user.user_id)
        return render_template("user/home.html",
            navigations=navigations.USER_NAV,
            user_kind = "Student",
            memberships = memberships,
            enrolled_events = events)
        
        
    elif auth_user.kind == UserKind.Coordinator:
        return render_template("coordinator/home.html",
            navigations=navigations.COORDINATOR_NAV,
            user_kind = "Coordinator")
    else:
        return render_template("awaiting_approval.html")
