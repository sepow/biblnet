from django import forms
from django.utils.translation import ugettext_lazy as _
from schedule.models import Event, Occurrence
import datetime
import time


class SpanForm(forms.ModelForm):

    start = forms.DateTimeField(widget=forms.SplitDateTimeWidget)
    end = forms.DateTimeField(widget=forms.SplitDateTimeWidget, help_text = _("The end time must be later than start time."))

    def clean_end(self):
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            raise forms.ValidationError(_("The end time must be later than start time."))
        return self.cleaned_data['end']


class EventForm(SpanForm):
    def __init__(self, hour24=False, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
    
    end_recurring_period = forms.DateTimeField(help_text = _("This date is ignored for one time only events."), required=False)
    
    class Meta:
        model = Event
        exclude = ('creator', 'created_on', 'calendar')
        
    def clean_end_recurring_period(self):
        if self.cleaned_data['rule'] and not self.cleaned_data['end_recurring_period']:
            raise forms.ValidationError(_("There must be an end date for recurring events"))
        return self.cleaned_data['end_recurring_period']

class OccurrenceForm(SpanForm):
    
    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')
