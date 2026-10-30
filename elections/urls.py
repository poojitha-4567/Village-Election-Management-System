
from django.urls import path
from . import views

urlpatterns = [

    # Login
    path("", views.login_view, name="login"),

    # Registration
    path("register/", views.register_view, name="register"),

    # Dashboard
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # Statistics
    path("statistics/", views.statistics_view, name="statistics"),

    # Reports
    path("reports/", views.reports_view, name="reports"),

    # CSV Export - Voters, Candidates, Villages and Votes
    path(
        "reports/export/<str:report_type>/",
        views.export_csv_view,
        name="export_csv",
    ),

    # Voters
    path("voters/", views.voter_list_view, name="voters"),

    path(
        "voters/edit/<int:voter_id>/",
        views.edit_voter_view,
        name="edit_voter",
    ),

    path(
        "voters/delete/<int:voter_id>/",
        views.delete_voter_view,
        name="delete_voter",
    ),

    # Candidates
    path("candidates/", views.candidate_list_view, name="candidates"),

    path(
        "candidates/edit/<int:candidate_id>/",
        views.edit_candidate_view,
        name="edit_candidate",
    ),

    path(
        "candidates/delete/<int:candidate_id>/",
        views.delete_candidate_view,
        name="delete_candidate",
    ),

    # Villages
    path("villages/", views.village_list_view, name="villages"),

    path(
        "villages/edit/<int:village_id>/",
        views.edit_village_view,
        name="edit_village",
    ),

    path(
        "villages/delete/<int:village_id>/",
        views.delete_village_view,
        name="delete_village",
    ),

    # Voting
    path("voting/", views.voting_page, name="voting"),

    # Logout
    path("logout/", views.logout_view, name="logout"),
]
