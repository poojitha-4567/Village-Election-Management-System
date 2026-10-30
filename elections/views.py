
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv

from .models import Voter, Candidate, Village, Vote


# USER REGISTRATION
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not all([username, email, password, confirm_password]):
            messages.error(request, "Please fill all fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(
                request, "Registration successful. Please login."
            )
            return redirect("login")

    return render(request, "elections/register.html")


# USER LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# DASHBOARD
@login_required
def dashboard_view(request):
    context = {
        "voter_count": Voter.objects.count(),
        "candidate_count": Candidate.objects.count(),
        "village_count": Village.objects.count(),
    }
    return render(request, "elections/home.html", context)


# VOTERS: ADD, SEARCH AND PAGINATION
@login_required
def voter_list_view(request):
    if request.method == "POST":
        voter_id = request.POST.get("voter_id", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        age = request.POST.get("age", "").strip()
        village = request.POST.get("village", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not all([voter_id, full_name, age, village, phone]):
            messages.error(request, "Please fill all fields.")
        elif Voter.objects.filter(voter_id=voter_id).exists():
            messages.error(request, "Voter ID already exists.")
        else:
            try:
                age_value = int(age)

                if age_value < 18:
                    messages.error(
                        request, "Voter age must be 18 or above."
                    )
                else:
                    Voter.objects.create(
                        voter_id=voter_id,
                        full_name=full_name,
                        age=age_value,
                        village=village,
                        phone=phone
                    )
                    messages.success(
                        request, "Voter details added successfully!"
                    )
                    return redirect("voters")

            except ValueError:
                messages.error(request, "Please enter a valid age.")

    search_query = request.GET.get("q", "").strip()
    voters = Voter.objects.all().order_by("id")

    if search_query:
        voters = voters.filter(
            Q(voter_id__icontains=search_query)
            | Q(full_name__icontains=search_query)
            | Q(village__icontains=search_query)
        )

    paginator = Paginator(voters, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "elections/voter_list.html", {
        "voters": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query
    })


# EDIT VOTER
@login_required
def edit_voter_view(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)

    if request.method == "POST":
        new_voter_id = request.POST.get("voter_id", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        age = request.POST.get("age", "").strip()
        village = request.POST.get("village", "").strip()
        phone = request.POST.get("phone", "").strip()

        if not all([new_voter_id, full_name, age, village, phone]):
            messages.error(request, "Please fill all fields.")
        elif Voter.objects.filter(
            voter_id=new_voter_id
        ).exclude(id=voter.id).exists():
            messages.error(request, "Voter ID already exists.")
        else:
            try:
                age_value = int(age)

                if age_value < 18:
                    messages.error(
                        request, "Voter age must be 18 or above."
                    )
                else:
                    voter.voter_id = new_voter_id
                    voter.full_name = full_name
                    voter.age = age_value
                    voter.village = village
                    voter.phone = phone
                    voter.save()

                    messages.success(
                        request, "Voter updated successfully!"
                    )
                    return redirect("voters")

            except ValueError:
                messages.error(request, "Please enter a valid age.")

    return render(
        request, "elections/edit_voter.html", {"voter": voter}
    )


# DELETE VOTER
@login_required
def delete_voter_view(request, voter_id):
    if request.method == "POST":
        voter = get_object_or_404(Voter, id=voter_id)
        voter.delete()
        messages.success(request, "Voter deleted successfully!")

    return redirect("voters")


# CANDIDATES: ADD, SEARCH AND PAGINATION
@login_required
def candidate_list_view(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        age = request.POST.get("age", "").strip()
        village = request.POST.get("village", "").strip()
        party_name = request.POST.get("party_name", "").strip()
        symbol = request.POST.get("symbol", "").strip()

        if not all([
            candidate_id, full_name, age,
            village, party_name, symbol
        ]):
            messages.error(request, "Please fill all fields.")
        elif Candidate.objects.filter(
            candidate_id=candidate_id
        ).exists():
            messages.error(request, "Candidate ID already exists.")
        else:
            try:
                age_value = int(age)

                if age_value < 18:
                    messages.error(
                        request, "Candidate age must be 18 or above."
                    )
                else:
                    Candidate.objects.create(
                        candidate_id=candidate_id,
                        full_name=full_name,
                        age=age_value,
                        village=village,
                        party_name=party_name,
                        symbol=symbol
                    )
                    messages.success(
                        request, "Candidate added successfully!"
                    )
                    return redirect("candidates")

            except ValueError:
                messages.error(request, "Please enter a valid age.")

    search_query = request.GET.get("q", "").strip()
    candidates = Candidate.objects.all().order_by("id")

    if search_query:
        candidates = candidates.filter(
            Q(candidate_id__icontains=search_query)
            | Q(full_name__icontains=search_query)
            | Q(village__icontains=search_query)
            | Q(party_name__icontains=search_query)
            | Q(symbol__icontains=search_query)
        )

    paginator = Paginator(candidates, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "elections/candidate_list.html", {
        "candidates": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query
    })


# EDIT CANDIDATE
@login_required
def edit_candidate_view(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == "POST":
        new_candidate_id = request.POST.get(
            "candidate_id", ""
        ).strip()
        full_name = request.POST.get("full_name", "").strip()
        age = request.POST.get("age", "").strip()
        village = request.POST.get("village", "").strip()
        party_name = request.POST.get("party_name", "").strip()
        symbol = request.POST.get("symbol", "").strip()

        if not all([
            new_candidate_id, full_name, age,
            village, party_name, symbol
        ]):
            messages.error(request, "Please fill all fields.")
        elif Candidate.objects.filter(
            candidate_id=new_candidate_id
        ).exclude(id=candidate.id).exists():
            messages.error(request, "Candidate ID already exists.")
        else:
            try:
                age_value = int(age)

                if age_value < 18:
                    messages.error(
                        request, "Candidate age must be 18 or above."
                    )
                else:
                    candidate.candidate_id = new_candidate_id
                    candidate.full_name = full_name
                    candidate.age = age_value
                    candidate.village = village
                    candidate.party_name = party_name
                    candidate.symbol = symbol
                    candidate.save()

                    messages.success(
                        request, "Candidate updated successfully!"
                    )
                    return redirect("candidates")

            except ValueError:
                messages.error(request, "Please enter a valid age.")

    return render(
        request,
        "elections/edit_candidate.html",
        {"candidate": candidate}
    )


# DELETE CANDIDATE
@login_required
def delete_candidate_view(request, candidate_id):
    if request.method == "POST":
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.delete()
        messages.success(request, "Candidate deleted successfully!")

    return redirect("candidates")


# VILLAGES: ADD, SEARCH AND PAGINATION
@login_required
def village_list_view(request):
    if request.method == "POST":
        village_name = request.POST.get("village_name", "").strip()
        district = request.POST.get("district", "").strip()
        mandal = request.POST.get("mandal", "").strip()
        population = request.POST.get("population", "").strip()

        if not all([village_name, district, mandal, population]):
            messages.error(request, "Please fill all fields.")
        elif Village.objects.filter(
            village_name__iexact=village_name
        ).exists():
            messages.error(request, "Village already exists.")
        else:
            try:
                population_value = int(population)

                if population_value < 0:
                    messages.error(
                        request, "Population cannot be negative."
                    )
                else:
                    Village.objects.create(
                        village_name=village_name,
                        district=district,
                        mandal=mandal,
                        population=population_value
                    )
                    messages.success(
                        request, "Village added successfully!"
                    )
                    return redirect("villages")

            except ValueError:
                messages.error(
                    request, "Please enter a valid population."
                )

    search_query = request.GET.get("q", "").strip()
    villages = Village.objects.all().order_by("id")

    if search_query:
        villages = villages.filter(
            Q(village_name__icontains=search_query)
            | Q(district__icontains=search_query)
            | Q(mandal__icontains=search_query)
        )

    paginator = Paginator(villages, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "elections/village_list.html", {
        "villages": page_obj.object_list,
        "page_obj": page_obj,
        "search_query": search_query
    })


# EDIT VILLAGE
@login_required
def edit_village_view(request, village_id):
    village = get_object_or_404(Village, id=village_id)

    if request.method == "POST":
        village_name = request.POST.get("village_name", "").strip()
        district = request.POST.get("district", "").strip()
        mandal = request.POST.get("mandal", "").strip()
        population = request.POST.get("population", "").strip()

        if not all([village_name, district, mandal, population]):
            messages.error(request, "Please fill all fields.")
        elif Village.objects.filter(
            village_name__iexact=village_name
        ).exclude(id=village.id).exists():
            messages.error(request, "Village already exists.")
        else:
            try:
                population_value = int(population)

                if population_value < 0:
                    messages.error(
                        request, "Population cannot be negative."
                    )
                else:
                    village.village_name = village_name
                    village.district = district
                    village.mandal = mandal
                    village.population = population_value
                    village.save()

                    messages.success(
                        request, "Village updated successfully!"
                    )
                    return redirect("villages")

            except ValueError:
                messages.error(
                    request, "Please enter a valid population."
                )

    return render(
        request, "elections/edit_village.html", {"village": village}
    )


# DELETE VILLAGE
@login_required
def delete_village_view(request, village_id):
    if request.method == "POST":
        village = get_object_or_404(Village, id=village_id)
        village.delete()
        messages.success(request, "Village deleted successfully!")

    return redirect("villages")


# VOTING PAGE
@login_required
def voting_page(request):
    candidates = Candidate.objects.all().order_by("full_name")

    if request.method == "POST":
        voter_id = request.POST.get("voter_id", "").strip()
        candidate_id = request.POST.get("candidate_id", "").strip()

        if not voter_id or not candidate_id:
            messages.error(
                request,
                "Please enter a Voter ID and select a candidate."
            )
            return redirect("voting")

        try:
            voter = Voter.objects.get(voter_id=voter_id)
            candidate = Candidate.objects.get(candidate_id=candidate_id)

            with transaction.atomic():
                Vote.objects.create(
                    voter=voter,
                    candidate=candidate
                )

            messages.success(request, "Vote submitted successfully!")

        except Voter.DoesNotExist:
            messages.error(request, "Invalid Voter ID.")
        except Candidate.DoesNotExist:
            messages.error(request, "Invalid candidate.")
        except IntegrityError:
            messages.error(
                request, "This voter has already voted."
            )

        return redirect("voting")

    return render(
        request,
        "elections/voting.html",
        {"candidates": candidates}
    )


# ELECTION STATISTICS
@login_required
def statistics_view(request):
    candidate_votes = Candidate.objects.annotate(
        total_votes=Count("votes")
    ).order_by("-total_votes", "full_name")

    return render(request, "elections/statistics.html", {
        "voter_count": Voter.objects.count(),
        "candidate_count": Candidate.objects.count(),
        "village_count": Village.objects.count(),
        "candidate_votes": candidate_votes,
        "total_votes": Vote.objects.count(),
    })


# REPORTS
@login_required
def reports_view(request):
    return render(request, "elections/reports.html", {
        "voter_count": Voter.objects.count(),
        "candidate_count": Candidate.objects.count(),
        "village_count": Village.objects.count(),
        "total_votes": Vote.objects.count(),
    })


# CSV EXPORT
@login_required
def export_csv_view(request, report_type):
    report_config = {
        "voters": {
            "model": Voter,
            "filename": "voters_report.csv",
            "headers": [
                "Voter ID", "Full Name", "Age", "Village", "Phone"
            ],
            "fields": [
                "voter_id", "full_name", "age", "village", "phone"
            ]
        },

        "candidates": {
            "model": Candidate,
            "filename": "candidates_report.csv",
            "headers": [
                "Candidate ID", "Full Name", "Age",
                "Village", "Party Name", "Symbol"
            ],
            "fields": [
                "candidate_id", "full_name", "age",
                "village", "party_name", "symbol"
            ]
        },

        "villages": {
            "model": Village,
            "filename": "villages_report.csv",
            "headers": [
                "Village Name", "District", "Mandal", "Population"
            ],
            "fields": [
                "village_name", "district", "mandal", "population"
            ]
        },

        "votes": {
            "model": Vote,
            "filename": "votes_report.csv",
            "headers": [
                "Voter ID",
                "Voter Name",
                "Candidate Name",
                "Party Name",
                "Election Symbol",
                "Voted At"
            ],
            "fields": [
                "voter__voter_id",
                "voter__full_name",
                "candidate__full_name",
                "candidate__party_name",
                "candidate__symbol",
                "voted_at"
            ]
        }
    }

    config = report_config.get(report_type)

    if config is None:
        return HttpResponse("Report not found.", status=404)

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )
    response.write("\ufeff")
    response["Content-Disposition"] = (
        f'attachment; filename="{config["filename"]}"'
    )

    writer = csv.writer(response)
    writer.writerow(config["headers"])

    records = config["model"].objects.all().values_list(
        *config["fields"]
    )

    for record in records:
        writer.writerow(record)

    return response


# LOGOUT
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")
