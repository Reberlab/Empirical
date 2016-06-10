from django.db import models
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

import hashlib, time, random
from django import forms

class SessionManager(models.Manager):
    def create_session(self,name,configFile,expName):
        session = self.create(name=name,configFile=configFile,expName=expName)
        # add tokens
        newToken=hashlib.md5(session.name+session.expName+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        # guarantee unique, just in case
        while Session.objects.all().filter(sessionToken=newToken).exists():
            newToken=hashlib.md5(session.name+session.expName+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        session.sessionToken=newToken
        session.save()
        return session

class Session(models.Model):
    sessionToken=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    expName=models.CharField(max_length=100)
    configFile=models.TextField()
    creationDate=models.DateTimeField(auto_now_add=True)

    objects=SessionManager()

    def __unicode__(self):
        return self.expName+':'+self.name

class ConfigForm(ModelForm):
    class Meta:
        model = Session
        fields = ['sessionToken', 'name', 'expName', 'configFile']
        labels = {'sessionToken': 'Session Token', 'name': "File name:", 'expName':"Experiment Name:", 'configFile': "Configuration File Contents"}
        widgets = {'configFile': forms.Textarea(attrs={'cols': 80, 'rows': 80}),
                   'sessionToken': forms.HiddenInput()}


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


class Study(models.Model):
    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)
    name=models.CharField(max_length=100)
    consentJSON=models.TextField()
    participants=models.TextField() # this will hold a list of workerIds (e.g., from mTurk) to allow checking for repeat participants
    recycle=models.BooleanField(default=True)
    unique_id=models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class StudyForm(ModelForm):
    class Meta:
        model = Study
        fields = ['name', 'recycle', 'unique_id', 'consentJSON' ]
        labels = {'name': "Study name:",
                  'recycle': "Allow Sessions to recycle in a Group",
                  'unique_id': "Require unique worker id's to participate",
                  'consentJSON':"Consent form in JSON:"}

class TokenGeneration(models.Model):
    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)
    expName=models.CharField(max_length=100)
    appletName=models.CharField(max_length=100)
    studyName=models.ForeignKey('Study',blank=True,null=True)

    # mturk info deprecated
    #mturk_title=models.CharField(max_length=100,blank=True)
    #mturk_amount=models.DecimalField(max_digits=4,decimal_places=2,blank=True,default=5.00)
    #mturk_frame_size=models.CharField(max_length=100,blank=True,default=800)
    #mturk_description=models.CharField(max_length=1000,blank=True)

    # Group token is the id for referencing the group of sessions
    # groupSessions is a list (space delimited) of session tokens to use
    # totalTokens is the total number of sessions in the group
    # numTokens is the subset of tokens to use -- for when restricting to a subset, e.g., after editing
    # note that groupSessions is sorted so that the first numTokens session tokens on the list are
    #  the ones that will be used
    groupToken=models.CharField(max_length=100)
    groupSessions=models.TextField()
    numTokens=models.IntegerField(default=10, validators=[MaxValueValidator(300),MinValueValidator(1)])
    totalTokens=models.IntegerField(default=10, validators=[MaxValueValidator(10000),MinValueValidator(1)])



    def __unicode__(self):
        if self.studyName==None:
            return self.appletName+':'+self.expName+':'+self.groupToken
        return self.studyName.name+':'+self.expName+':'+self.groupToken

    def create_token(self):
        # add tokens
        newToken=hashlib.md5(self.expName+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        # guarantee unique, just in case
        while TokenGeneration.objects.all().filter(groupToken=newToken).exists():
            newToken=hashlib.md5(self.expName+str(time.time())+("%08d" % random.randint(100000,999999))).hexdigest()[:16]
        self.groupToken=newToken
        return



class TokenForm(ModelForm):
    # email field and mturk auth tokens go here
    # these extra pieces of data are used to generate tokens but aren't stored in the database for security
    #mturk_key_id=forms.CharField(max_length=100,label='Amazon mTurk key id',required=False)
    #mturk_secret_key=forms.CharField(max_length=100,label='Amazon mTurk secret key',required=False)
    #priorTokens=forms.CharField(widget=forms.Select(),label='Add to existing group')
    priorTokens=forms.ModelChoiceField(queryset=TokenGeneration.objects.all(),label='Add to existing token group',required=False)
    add_all=forms.BooleanField(widget=forms.CheckboxInput,label='Add all available cfgs?',initial=True,required=False)
    readd_used=forms.BooleanField(widget=forms.CheckboxInput,label='Re-add cfgs with data?',initial=False,required=False)
    restrict_to_new=forms.BooleanField(widget=forms.CheckboxInput,label='Only administer new cfgs for this token',initial=False,required=False)
    participantList=forms.CharField(widget=forms.Textarea,label='List of participants',required=False)

    class Meta:
        model = TokenGeneration
        fields = ['appletName', 'studyName', 'numTokens'] #, 'add_all', 'readd_used', 'restrict_to_new'] #, 'mturk_title', 'mturk_description', 'mturk_amount', 'mturk_frame_size']
        labels = {'appletName': 'Applet for this Experiment:',
                  'numTokens': 'Number of cfgs to include:',
                  'studyName': 'Study that provides consent information:'}
        #widgets = {'mturk_description': forms.TextInput(attrs={'size': 80}),
        #           'mturk_amount': forms.NumberInput(attrs={'step': 0.25})}


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
class Experiment_desc():
    def __init__(self,name,fill=True):
        self.name=name
        if fill:
            self.find_sessions()

    def find_sessions(self):
        session_list=Session.objects.all().filter(expName=self.name).order_by('-creationDate')
        if session_list!=[]:
            self.date=session_list[0].creationDate # experiment creation date is assumed to be the same for all config files
            self.token=session_list[0].sessionToken # this sessionToken can be used as a link to the experiment display view
            cfg_list=[]
            for s in session_list:
                # check for data reports on this session
                report_list=Report.objects.all().filter(sessionToken=s.sessionToken)
                reports=[]
                #for i in report_list:
                #    r = (i.eventType,i.uploadDate)
                #    reports.append(r)
                cfg_list.append((s.name,s.sessionToken,s.creationDate,reports))
            #cfg_list.sort()
            self.cfg_list=cfg_list
            self.num_sessions=len(cfg_list)
        return

    def find_data(self):
        session_list=Session.objects.all().filter(expName=self.name)
        reports=[]
        for s in session_list:
            report_list=Report.objects.all().filter(sessionToken=s.sessionToken).order_by('-uploadDate')
            if report_list.exists():
                for r in report_list:
                    reports.append((s.sessionToken,r.eventType,r.pk,r.uploadDate,self.data_summary(r.dataLog,10,'###')))
        return reports

    # Data summarizing/shortening helper function
    def data_summary(self, log, length, separator=''):
        lines = log.split('\n')
        count = 0
        summary = ''
        for i in lines:
            if count < length:
                summary = summary + ('%d. ' % (count + 1)) + i + '\n'
            count = count + 1
            if i[:len(separator)] == separator:
                summary = summary + separator + '\n'
                count = 0
        return summary