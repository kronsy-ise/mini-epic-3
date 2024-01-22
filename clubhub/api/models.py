from __future__ import annotations
from django.db import models

class Club(models.Model):

    ACTIVE="A"
    INACTIVE="I"

    CLUB_STATUS_CHOICES = (
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive")
    )
    
    name = models.TextField(max_length = 20)
    description = models.TextField(max_length = 300)
    status = models.CharField(max_length=1, choices=CLUB_STATUS_CHOICES)

    coordinator = models.OneToOneField('User', on_delete=models.CASCADE)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(models.Model):

    STUDENT = "S"
    COORDINATOR = "C"

    USER_KIND_CHOICES = (
        (STUDENT, "Student"),
        (COORDINATOR, "Co-Ordinator")
    )

    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    password_hash = models.TextField()
    kind = models.CharField(max_length=1, choices=USER_KIND_CHOICES)
    approved = models.BooleanField()

    # The admin user is the first user created in the system
    is_admin = models.BooleanField()

    clubs = models.ManyToManyField(Club)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event(models.Model):

    title = models.TextField(max_length = 30)
    description = models.TextField(max_length = 300)
    time = models.DateTimeField()
    venue = models.TextField()

    organizing_club = models.OneToOneField(Club, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




