# teams/models.py
# Author: Samuel Coelho (w2078214)
# Individual element - Team models for Sky Connect

from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """Represents a department within Sky Engineering"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    leader = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    """Represents an engineering team at Sky"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('restructuring', 'Restructuring'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    manager = models.CharField(max_length=200)
    manager_role = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    email = models.EmailField(blank=True)
    slack_channel = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """Represents a member of an engineering team"""
    ROLE_CHOICES = [
        ('engineer', 'Engineer'),
        ('architect', 'Architect'),
        ('manager', 'Manager'),
        ('lead', 'Lead'),
    ]

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members'
    )
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    job_title = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} — {self.team.name}"


class Repository(models.Model):
    """Represents a code repository belonging to a team"""
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='repositories'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Repositories"

    def __str__(self):
        return self.name


class Dependency(models.Model):
    """Represents an upstream or downstream dependency between teams"""
    TYPE_CHOICES = [
        ('upstream', 'Upstream'),
        ('downstream', 'Downstream'),
    ]

    from_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='dependencies'
    )
    to_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='dependent_on'
    )
    dependency_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Dependencies"

    def __str__(self):
        return f"{self.from_team.name} → {self.to_team.name} ({self.dependency_type})"