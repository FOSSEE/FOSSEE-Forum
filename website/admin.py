from website.models import Question, Answer, AnswerComment, FossCategory, Profile, ModeratorGroup
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib import admin


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_filter = ('category', 'date_created', 'date_modified')

class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['body']
    list_filter = ('date_created', 'date_modified')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class GroupInline(admin.StackedInline):
    model = ModeratorGroup
    can_delete = False
    verbose_name_plural = 'moderator group'

# Define a new User, Group admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerComment)
admin.site.register(FossCategory)
