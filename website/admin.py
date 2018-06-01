from website.models import Question, Answer, AnswerComment, FossCategory, Profile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin


class QuestionAdmin(admin.ModelAdmin):
    #search_fields = ['title','user']
    list_filter = ('category','date_created','date_modified')

class AnswerAdmin(admin.ModelAdmin):
    #search_fields = ['question']
    list_filter = ('date_created','date_modified')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerComment)
admin.site.register(FossCategory)                                
