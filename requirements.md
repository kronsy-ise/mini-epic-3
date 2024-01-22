# Key Features:


## User Registration and Roles:
1. The system will primarily have two types of users: students and coordinators.
2. Anyone can request registration into the system, by filling a registration form i.e. providing a
username, password, contact, email, etc.
3. The first registered user becomes the admin coordinator, a non-deletable account with
special privileges.
4. The subsequent registrations must be approved by the coordinator as student or
coordinator membership.
5. Only approved members should have the access(login) to the application and rejected
records should be deleted from the system.
6. Approved users can update their profile information i.e. contact number etc.
Club Management:
1. Coordinators can create new clubs within the system.
2. Each club has a name, description, validity status, and an associated coordinator from a list
of available coordinators.
3. A coordinator can only be associated with one club.
4. The admin coordinator cannot be associated with any club.
Club Membership:
1. The approved users can see the list of the clubs.
2. Users can request membership to the club of their choice.
3. The relevant club coordinator will see the pending requests and approve/reject club
membership.
4. Users can request/join a maximum of three clubs


## Event Management:
1. Club coordinators can create club events with a title, description, date, time, and venue for
their event.
2. All users can see the list of upcoming events (along with the information of host club) and
can apply to participate/play in each event listed.
3. The events are free and the event registration requests from members of the same club
should automatically be approved.
4. The approval for members from different clubs requires coordinator intervention/approval.

## Privacy and Information Access:
1. The admin coordinator has access to contact and membership information for all users.
2. The club coordinators can only view contact information of members within their club.
3. All other members can only see their own profile information.

## Design requirements:
1. Design a Database Schema that is complaint with 3NF.
2. Integrity constraints must be implemented while designing database
3. Every table must have two additional columns for auditing. i.e. created & updated
timestamps columns.
4. Refine your schema based on the given design document and execute all the DDL
statements against that schema.
5. Design Database views for standard reporting.
6. Implement triggers for autonomous tasks.



# Deliverables

1. A database Schema (automatically exported from database)
2. A .txt file containing all DDL scripts.
3. A backup file from the database containing all the DDL scripts exported from the
database.
4. A .txt file containing all DML scripts.
5. A working web application in Python
6. Project setup guide
7. How can we setup point a & b to run the project to machine X.
8. A 1-2 pager project report about the brief introduction of the project, the design
choices and a list of assumption if you make any
