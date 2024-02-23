from __future__ import annotations
from flask import Blueprint, redirect, render_template, request, url_for
from globals import db
from models.user import UserKind,User
import util
from models.club import Club
clubs_app = Blueprint('clubs_app', __name__)

@clubs_app.get("/admin/clubs")
def clubs():
    auth_user = util.verify_session()
    print(auth_user.kind)

    if auth_user == None:
        return redirect("/")

    # Depending on the type of registered user 
    # we show a different home page
    
    if auth_user.kind == UserKind.Admin:
        users=User.return_list()
        clubs = Club.return_list()
        return render_template("admin/clubs.html",clubs=clubs,users=users)
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
    users=User.return_list()
    clubs = Club.return_list()
    return redirect("admin/clubs")
