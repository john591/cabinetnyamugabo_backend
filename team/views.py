from django.views.generic import DetailView, ListView

from .models import TeamMember


class TeamMemberListView(ListView):
    model = TeamMember
    template_name = "team/member_list.html"
    context_object_name = "team_members"
    queryset = TeamMember.objects.filter(is_active=True)


class TeamMemberDetailView(DetailView):
    model = TeamMember
    template_name = "team/member_detail.html"
    context_object_name = "member"
