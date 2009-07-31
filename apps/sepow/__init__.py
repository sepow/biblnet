'''
import datetime
from schedule.models import Calendar
from schedule.models import Event
from schedule.models import Rule

try:
    rule = Rule.objects.get(name="Daily")
except Rule.DoesNotExist:
    print "Need to install the basic rules"
    rule = Rule(frequency = "YEARLY", name = "Yearly", description = "will recur once every Year")
    rule.save()
    print "YEARLY recurrence created"
    rule = Rule(frequency = "MONTHLY", name = "Monthly", description = "will recur once every Month")
    rule.save()
    print "Monthly recurrence created"
    rule = Rule(frequency = "WEEKLY", name = "Weekly", description = "will recur once every Week")
    rule.save()
    print "Weekly recurrence created"
    rule = Rule(frequency = "DAILY", name = "Daily", description = "will recur once every Day")
    rule.save()
    print "Daily recurrence created"
    
    gem i fixtures istedet
'''
