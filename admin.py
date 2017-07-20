from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Programme, UserProgramme, Stage, MasterCourse, ScheduledCourse, ProgrammeMasterCourse


class ProgrammeMasterForm(forms.ModelForm):
    """
    form for master courses
    """
    display_order = forms.ChoiceField(label=_('display order'), required=False)

    def __init__(self, *args, **kwargs):
        super(ProgrammeMasterForm, self).__init__(*args, **kwargs)
        display_orders = range(1, MasterCourse.objects.count() + 1)
        self.fields['display_order'].choices = [('', '')] + [(str(x), str(x)) for x in display_orders]

    def clean(self):
        cleaned_data = super(ProgrammeMasterForm, self).clean()

        # ensure 'display_order' is set to zero if empty
        cleaned_data['display_order'] = cleaned_data['display_order'] or 0

        # validate that programme and master don't already exist where stage is not selected
        # note this is not enforced on the database with the unique together constraint
        stage = cleaned_data.get('stage')
        if not stage:
            programme = cleaned_data.get('programme')
            master_course = cleaned_data.get('master_course')
            pk = self.instance.pk or 0
            if ProgrammeMasterCourse.objects.filter(
                    programme=programme,
                    master_course=master_course,
                    stage=None
            ).exclude(pk=pk).exists():
                error = _('Programme master with this Programme and Master course already exists')
                raise forms.ValidationError(error)
        return cleaned_data

    class Meta:
        model = ProgrammeMasterCourse
        fields = '__all__'


class StageForm(forms.ModelForm):
    """
    form for stages
    """
    STAGE_ORDER_MAX = 100
    stage_order = forms.ChoiceField(label=_('Order'))
    stage_order.choices = [('', '')] + [(str(x), str(x)) for x in range(1, STAGE_ORDER_MAX)]


class ProgrammeMasterInline(admin.TabularInline):
    """
    inline for master courses
    """
    model = ProgrammeMasterCourse
    form = ProgrammeMasterForm
    verbose_name = _('Master course')
    verbose_name_plural = _('Master courses')
    ordering = ['stage__stage_order', 'display_order', 'master_course__display_name', ]


class StageInline(admin.TabularInline):
    """
    inline for stages
    """
    model = Stage
    ordering = ['stage_order', ]
    form = StageForm


class ScheduledCourseInline(admin.TabularInline):
    """
    inline for scheduled courses
    """
    model = ScheduledCourse
    readonly_fields = ['display_name', 'vle_course_id', 'open_date', 'start_date', 'end_date', 'close_date', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProgrammeStageAdmin(admin.ModelAdmin):
    """
    admin for programmes, with inline stages
    """
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'stage_count',)
    search_fields = ('display_name',)
    inlines = [StageInline, ]
    ordering = ['display_name', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProgrammeMasterCourseAdmin(admin.ModelAdmin):
    """
    admin for programmes, with inline master courses
    """
    readonly_fields = ('display_name',)
    list_display = ('display_name', 'master_course_count',)
    search_fields = ('display_name',)
    inlines = [ProgrammeMasterInline, ]
    ordering = ['display_name', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MasterCourseAdmin(admin.ModelAdmin):
    """
    admin for master courses, with inline scheduled courses
    """
    list_display = ('display_name',)
    search_fields = ('display_name', 'vle_course_id',)
    inlines = [ScheduledCourseInline, ]
    readonly_fields = ['display_name', 'vle_course_id', 'weeks_duration', 'commitment', 'credits', 'compulsory', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProgrammeStage(Programme):
    """
    proxy model to registered in the admin site
    """
    class Meta:
        proxy = True


class ProgrammeCourse(Programme):
    """
    proxy model to registered in the admin site
    """
    class Meta:
        proxy = True


@admin.register(UserProgramme)
class UserProgrammeAdmin(admin.ModelAdmin):
    list_display = ('user', 'programme',)
    list_filter = ('programme',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'user__email', 'programme__name',)

admin.site.register(Programme)
admin.site.register(ProgrammeStage, ProgrammeStageAdmin)
admin.site.register(ProgrammeCourse, ProgrammeMasterCourseAdmin)
admin.site.register(MasterCourse, MasterCourseAdmin)
