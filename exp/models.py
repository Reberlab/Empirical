from django.db import models
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

import hashlib, time, random
from django import forms

class Study(models.Model):
    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)

    name=models.CharField(max_length=100)
    appletName=models.CharField(max_length=100)
    consentJSON=models.TextField()
    participants=models.TextField() # this will hold a list of workerIds (e.g., from mTurk) to allow checking for repeat participants

    def __unicode__(self):
        return self.name

    def addParticipant(self,workerid,session):
        self.participants=self.participants+('%s:%s ' % (workerid,session))
        self.save()


class StudyForm(ModelForm):
    class Meta:
        model = Study
        fields = ['name', 'appletName', 'consentJSON' ]
        labels = {'name': "Study name:",
                  'appletName': "Name of applet to run experiment",
                  'consentJSON':"Consent form in JSON:"}

##########################

#class ExperimentManager(models.Manager):
#    def create_experiment(self,user,name,app,study,recycle,unique):
#        e = self.create(user=user, name=name, appletName=app, study=study, recycle=recycle, unique_id=unique)
#        e.create_token()
#        e.save()
#        return e

class Experiment(models.Model):
    # core definition of an experiment group
    name=models.CharField(max_length=100)
    study=models.ForeignKey('Study',blank=True,null=True)
    groupToken=models.CharField(max_length=100)
    recycle=models.BooleanField(default=True)
    unique_id=models.BooleanField(default=True)

    groupSessions=models.TextField(default='')
    numTokens=models.IntegerField(default=10, validators=[MaxValueValidator(300),MinValueValidator(1)])
    totalTokens=models.IntegerField(default=10, validators=[MaxValueValidator(10000),MinValueValidator(1)])

    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)

    #objects=ExperimentManager()

    def __unicode__(self):
        return self.name+':'+self.groupToken

    def create_token(self):
        # add tokens
        newToken=hashlib.md5(self.name+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        # guarantee unique, just in case
        while Experiment.objects.all().filter(groupToken=newToken).exists():
            newToken=hashlib.md5(self.name+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        self.groupToken=newToken
        return

    def add_sessions(self,sessions,limit=False):
        if self.groupSessions=='':
            self.groupSessions=sessions
            self.totalTokens=len(sessions.split(' '))
            self.numTokens=self.totalTokens
            return
        self.groupSessions=sessions+' '+self.groupSessions
        self.totalTokens = len(self.groupSessions.split(' '))
        if limit:
            self.numTokens=len(sessions.split(' '))
        else:
            self.numTokens=self.totalTokens

    # base should be constructed in the view that calls this to get the link
    def link_url(self,base,workerid=''):
        if workerid=='':
            return "%s?group=%s" % (base,self.groupToken)
        return "%s?group=%s&workerId=%s" % (base,self.groupToken,workerid)

# Experiments either get created:
# 1. As a blank template (e.g., cfgs will be created manually or copied from another existing experiment)
# 2. When a .zip file of .cfgs is uploaded

# This form will get used if (a) creating a blank Exp to add to later, (b) editing the Experiment object

class ExperimentForm(ModelForm):

    class Meta:
        model = Experiment
        fields = ['name', 'recycle', 'unique_id'] #, 'add_all', 'readd_used', 'restrict_to_new'] #, 'mturk_title', 'mturk_description', 'mturk_amount', 'mturk_frame_size']
        labels = {'name': 'Name for this Experiment',
                  'recycle': "Allow Sessions to recycle in a Group",
                  'unique_id': "Require unique worker id's to participate"}
        widgets = {'study': forms.HiddenInput()}


class ExperimentUploadForm(ModelForm):

    study_id=forms.ModelChoiceField(queryset=Study.objects.all(),label='Associated Study',required=True)
    #add_all=forms.BooleanField(widget=forms.CheckboxInput,label='Add all available cfgs?',initial=True,required=False)
    #readd_used=forms.BooleanField(widget=forms.CheckboxInput,label='Re-add cfgs with data?',initial=False,required=False)
    restrict_to_new=forms.BooleanField(widget=forms.CheckboxInput,label='Only administer new cfgs for this token',initial=False,required=False)

    class Meta:
        model = Experiment
        fields = ['recycle', 'unique_id'] #, 'add_all', 'readd_used', 'restrict_to_new'] #, 'mturk_title', 'mturk_description', 'mturk_amount', 'mturk_frame_size']
        labels = {'recycle': "Allow Sessions to recycle in a Group",
                  'unique_id': "Require unique worker id's to participate"}


##############################

class SessionManager(models.Manager):
    # should user be passed in here as well?
    def create_session(self,name,exp,configFile,user):
        session = self.create(name=name,configFile=configFile,exp=exp,user=user)
        session.make_token()
        session.save()
        return session

class Session(models.Model):
    sessionToken=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    #expName=models.CharField(max_length=100)
    exp=models.ForeignKey('Experiment',blank=True,null=True)
    configFile=models.TextField()
    lastStarted=models.DateTimeField(blank=True,null=True,default=None)

    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)

    objects=SessionManager()

    def __unicode__(self):
        if self.exp==None:
            return "None:"+self.name
        return self.exp.name+':'+self.name

    def make_token(self):
        newToken=hashlib.md5(self.name+self.exp.name+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        # guarantee unique, just in case
        while Session.objects.all().filter(sessionToken=newToken).exists():
            newToken=hashlib.md5(self.name+self.name+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        self.sessionToken=newToken
        return


class ConfigForm(ModelForm):
    class Meta:
        model = Session
        fields = ['sessionToken', 'name', 'configFile']
        labels = {'sessionToken': 'Session Token',
                  'name': "File name:",
                  'exp': "Experiment:",
                  'configFile': "Configuration File Contents"}
        widgets = {'configFile': forms.Textarea(attrs={'cols': 80, 'rows': 80}),
                   'sessionToken': forms.HiddenInput()}


########################

class Report(models.Model):
    sessionToken=models.CharField(max_length=100)
    sessionKey=models.ForeignKey('Session')
    eventType=models.CharField(max_length=100)
    uploadDate=models.DateTimeField(auto_now_add=True)
    dataLog=models.TextField()
    # app, ip other upload tracking information?

    def __unicode__(self):
        return self.sessionToken+'-'+self.eventType

class ReportForm(ModelForm):
    class Meta:
        model=Report
        fields=['sessionToken', 'eventType', 'dataLog']


############################


class Security(models.Model):
    sessionToken=models.CharField(max_length=100)
    hit_count=models.IntegerField(default=0)
    locked=models.BooleanField(default=False)
    creationDate=models.DateTimeField(auto_now_add=True)
    securityLog=models.TextField()

    def __unicode__(self):
        return self.sessionToken


###### General classes used in views but aren't Djanog models

# Experiments as a structure don't exist in the db, each session has it's own line
#  so experiment information is assembled on the fly from what is in the db
# class Experiment_desc():
#     def __init__(self,name,fill=True):
#         self.name=name
#         if fill:
#             self.find_sessions()
#
#     def find_sessions(self):
#         session_list=Session.objects.all().filter(expName=self.name).order_by('-creationDate')
#         if session_list!=[]:
#             self.date=session_list[0].creationDate # experiment creation date is assumed to be the same for all config files
#             self.token=session_list[0].sessionToken # this sessionToken can be used as a link to the experiment display view
#             cfg_list=[]
#             for s in session_list:
#                 # check for data reports on this session
#                 report_list=Report.objects.all().filter(sessionToken=s.sessionToken)
#                 reports=[]
#                 #for i in report_list:
#                 #    r = (i.eventType,i.uploadDate)
#                 #    reports.append(r)
#                 cfg_list.append((s.name,s.sessionToken,s.creationDate,reports))
#             #cfg_list.sort()
#             self.cfg_list=cfg_list
#             self.num_sessions=len(cfg_list)
#         return
#
#     def find_data(self):
#         session_list=Session.objects.all().filter(expName=self.name)
#         reports=[]
#         for s in session_list:
#             report_list=Report.objects.all().filter(sessionToken=s.sessionToken).order_by('-uploadDate')
#             if report_list.exists():
#                 for r in report_list:
#                     reports.append((s.sessionToken,r.eventType,r.pk,r.uploadDate,self.data_summary(r.dataLog,10,'###')))
#         return reports
#
#     # Data summarizing/shortening helper function
#     def data_summary(self, log, length, separator=''):
#         lines = log.split('\n')
#         count = 0
#         summary = ''
#         for i in lines:
#             if count < length:
#                 summary = summary + ('%d. ' % (count + 1)) + i + '\n'
#             count = count + 1
#             if i[:len(separator)] == separator:
#                 summary = summary + separator + '\n'
#                 count = 0
#         return summary