from website.models import Question, Answer, AnswerComment, FossCategory
from django.contrib import admin


class QuestionAdmin(admin.ModelAdmin):
    #search_fields = ['title','user']
    list_filter = ('category','date_created','date_modified')

class AnswerAdmin(admin.ModelAdmin):
    #search_fields = ['question']
    list_filter = ('date_created','date_modified')

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(AnswerComment)
admin.site.register(FossCategory)                                
