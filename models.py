from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Programme(models.Model):
    display_name = models.CharField(_('Display name'), max_length=100)

    def stage_count(self):
        return self.stage_set.count()
    stage_count.short_description = _('Number of stages')

    def master_course_count(self):
        return self.programmemastercourse_set.count()
    master_course_count.short_description = _('Number of master courses')

    def __str__(self):
        return self.display_name


class UserProgramme(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return '"{} {}" is a member of programme "{}"'.format(
            self.user.first_name,
            self.user.last_name,
            self.programme.display_name,
        )

    class Meta:
        unique_together = ('user', 'programme',)


class Stage(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    display_name = models.CharField(_('Display name'), max_length=100)
    stage_order = models.PositiveIntegerField(_('Order'))

    @property
    def courses_available(self):
        return self.programmemastercourse_set.filter(available=True).order_by('display_order')

    def __str__(self):
        return self.display_name

    class Meta:
        unique_together = ('programme', 'stage_order',)


class MasterCourse(models.Model):
    display_name = models.CharField(_('display name'), max_length=100)
    vle_course_id = models.CharField(_('VLE Course ID Number'), max_length=100, db_index=True, unique=True)
    compulsory = models.BooleanField(_('compulsory'), default=False)
    commitment = models.CharField(_('commitment'), max_length=100, blank=True)
    credits = models.PositiveIntegerField(_('credits'), null=True, blank=True)
    weeks_duration = models.PositiveIntegerField(_('duration in weeks'), null=True, blank=True)

    @property
    def next_start_date(self):
        all_dates = [s.start_date for s in self.scheduledcourse_set.all()]
        future_dates = [d for d in all_dates if d is not None and d >= datetime.today().date()]
        if len(future_dates) == 0:
            return None
        return min(future_dates)

    def __str__(self):
        return self.display_name


class ScheduledCourse(models.Model):
    display_name = models.CharField(_('display name'), max_length=100)
    master_course = models.ForeignKey(MasterCourse, on_delete=models.PROTECT)
    vle_course_id = models.CharField(_('VLE Course ID Number'), max_length=100, db_index=True, unique=True)
    open_date = models.DateField(_('open date'), null=True, blank=True, db_index=True)
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end (complete) date'), null=True, blank=True)
    close_date = models.DateField(_('close date'), null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(
            self.master_course.display_name,
            self.display_name
        )


class ScheduledCourseGroup(models.Model):
    display_name = models.CharField(_('display name'), max_length=100)
    scheduled_course = models.ForeignKey(ScheduledCourse, on_delete=models.PROTECT)
    vle_group_id = models.CharField(_('VLE Group ID Number'), max_length=100, db_index=True)

    def __str__(self):
        return '{} - {} - {}'.format(
            self.scheduled_course.master_course.display_name,
            self.scheduled_course.display_name,
            self.display_name
        )


class ProgrammeMasterCourse(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    master_course = models.ForeignKey(MasterCourse, on_delete=models.CASCADE)  # this should probably be a OneToOneField
    available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)

    def __str__(self):
        return '{} / {} {}'.format(
            self.programme.display_name,
            self.master_course.display_name,
            '(' + self.stage.display_name + ')' if self.stage else ''
        )

    class Meta:
        unique_together = ('programme', 'master_course',)
