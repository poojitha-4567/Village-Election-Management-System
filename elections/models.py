
from django.db import models


# VOTER DETAILS MODEL
class Voter(models.Model):
    voter_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    village = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.full_name} ({self.voter_id})"


# CANDIDATE DETAILS MODEL
class Candidate(models.Model):
    candidate_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    village = models.CharField(max_length=100)
    party_name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.full_name} - {self.party_name}"


# VILLAGE DETAILS MODEL
class Village(models.Model):
    village_name = models.CharField(max_length=100, unique=True)
    district = models.CharField(max_length=100)
    mandal = models.CharField(max_length=100)
    population = models.PositiveIntegerField()

    def __str__(self):
        return self.village_name


# VOTE DETAILS MODEL
class Vote(models.Model):
    voter = models.OneToOneField(
        Voter,
        on_delete=models.CASCADE,
        related_name="vote"
    )

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        related_name="votes"
    )

    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.voter.full_name} voted for "
            f"{self.candidate.full_name}"
        )
