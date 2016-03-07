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
    numTokens=models.IntegerField(default=10, validators=[MaxValueValidator(200),MinValueValidator(1)])
    mturk_title=models.CharField(max_length=100,blank=True)
    mturk_amount=models.DecimalField(max_digits=4,decimal_places=2,blank=True,default=5.00)
    mturk_frame_size=models.CharField(max_length=100,blank=True,default=800)
    mturk_description=models.CharField(max_length=1000,blank=True)
    # other details like mTurk or other configuration would go here
    # add id token to this plus a list of all the tokens included for group use...
    groupToken=models.CharField(max_length=100)
    groupSessions=models.TextField()

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
    mturk_key_id=forms.CharField(max_length=100,label='Amazon mTurk key id',required=False)
    mturk_secret_key=forms.CharField(max_length=100,label='Amazon mTurk secret key',required=False)
    emailList=forms.CharField(widget=forms.Textarea,label='List of email addresses (optional)',required=False)
    #priorTokens=forms.CharField(widget=forms.Select(),label='Add to existing group')
    priorTokens=forms.ModelChoiceField(queryset=TokenGeneration.objects.all(),required=False)
    class Meta:
        model = TokenGeneration
        fields = ['appletName', 'numTokens', 'studyName', 'mturk_title', 'mturk_description', 'mturk_amount', 'mturk_frame_size']
        widgets = {'mturk_description': forms.TextInput(attrs={'size': 80}),
                   'mturk_amount': forms.NumberInput(attrs={'step': 0.25})}


class Security(models.Model):
    sessionToken=models.CharField(max_length=100)
    hit_count=models.IntegerField(default=0)
    locked=models.BooleanField(default=False)
    creationDate=models.DateTimeField(auto_now_add=True)
    securityLog=models.TextField()

    def __unicode__(self):
        return self.sessionToken

