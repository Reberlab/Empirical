from django.db import models
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

import hashlib, time, random
from django import forms


######################## Handling Studys (groups of Experiments)

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

########################## Handling Experiments (groups of cfg files)

class Experiment(models.Model):
    # core definition of an experiment group
    name=models.CharField(max_length=100)
    study=models.ForeignKey('Study',blank=True,null=True,on_delete=models.CASCADE)
    groupToken=models.CharField(max_length=100)
    recycle=models.BooleanField(default=True)
    unique_id=models.BooleanField(default=True)

    groupSessions=models.TextField(default='')
    numTokens=models.IntegerField(default=10, validators=[MaxValueValidator(300),MinValueValidator(1)])
    totalTokens=models.IntegerField(default=10, validators=[MaxValueValidator(10000),MinValueValidator(1)])

    user=models.CharField(max_length=100)
    creationDate=models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name+':'+self.groupToken

    def create_token(self):
        # add tokens
        newToken=hashlib.md5((self.name+str(time.time())+("%08d" % random.randint(100000,999999))).encode('utf-8')).hexdigest()[:16]
        # guarantee unique, just in case
        while Experiment.objects.all().filter(groupToken=newToken).exists():
            newToken=hashlib.md5((self.name+str(time.time())+("%08d" % random.randint(100000,999999))).encode('utf-8')).hexdigest()[:16]
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
    restrict_to_new=forms.BooleanField(widget=forms.CheckboxInput,label='Only administer new cfgs for this token',initial=False,required=False)

    class Meta:
        model = Experiment
        fields = ['recycle', 'unique_id'] #, 'add_all', 'readd_used', 'restrict_to_new'] #, 'mturk_title', 'mturk_description', 'mturk_amount', 'mturk_frame_size']
        labels = {'recycle': "Allow Sessions to recycle in a Group",
                  'unique_id': "Require unique worker id's to participate"}


############################## Handling session data (cfg files)

class SessionManager(models.Manager):
    def create_session(self,name,exp,configFile,user):
        session = self.create(name=name,configFile=configFile,exp=exp,user=user)
        session.make_token()
        session.save()
        return session

class Session(models.Model):
    sessionToken=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    exp=models.ForeignKey('Experiment',blank=True,null=True,on_delete=models.CASCADE)
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
        newToken=hashlib.md5((self.name+self.exp.name+str(time.time())+("%08d" % random.randint(100000,999999))).encode('utf-8')).hexdigest()[:16]
        # guarantee unique, just in case
        while Session.objects.all().filter(sessionToken=newToken).exists():
            newToken=hashlib.md5((self.name+self.name+str(time.time())+("%08d" % random.randint(100000,999999))).encode('utf-8')).hexdigest()[:16]
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


######################## Reporting data from experiment apps

class Report(models.Model):
    sessionToken=models.CharField(max_length=100)
    sessionKey=models.ForeignKey('Session',on_delete=models.CASCADE)
    eventType=models.CharField(max_length=100)
    uploadDate=models.DateTimeField(auto_now_add=True)
    workerId=models.CharField(max_length=100)
    appName=models.CharField(max_length=100)
    appVersion=models.IntegerField(null=True,blank=True)
    dataLog=models.TextField()

    def __unicode__(self):
        return self.sessionToken+'-'+self.eventType

    def appNameVer(self):
        if self.appVersion == None:
            return('%s (none)' % self.appName)
        else:
            return("%s v%d" % (self.appName, self.appVersion))


class ReportForm(ModelForm):
    class Meta:
        model=Report
        fields=['sessionToken', 'eventType', 'appName', 'workerId', 'dataLog']

############################ Participants table

# The preliminary version of the Participant table is aimed at Experimenter use to contact volunteers
#   Later this should inherit from the Django AbstractUser base (to be able to log in, change prefs, etc)
# For now any Participant preferences will have to be set by an Experimenter
# No easy way yet to convert mTurk participants into direct contact ones

class Participant(models.Model):
    tag=models.CharField(max_length=100,blank=False)                   # this is the id by which the participant is referenced in the db
    name=models.CharField(max_length=256,blank=True,default='')        # real name for any additional, outside communication
    email=models.EmailField(max_length=256,blank=True,default='')      # Email contact info
    addedDate=models.DateTimeField(auto_now_add=True)                  # Date when participant added to db

    # Preference fields
    # contact style: None (no more experiments), ok to Email when available, or Opt-in through on Participant dashboard (when available)
    contact_type=models.CharField(max_length=1,choices=(('N','None'),('E','Email'),('O','Opt-in')),default='N')

    # ok to share data across Experimenters (e.g., mainly for when projects have separate IRBs) -- this might need to be experiment specific
    data_share=models.CharField(max_length=1,choices=(('N','None'),('A','All'),('L','Limited')),default='N')

    # a generic arbitrary notes field for experimenters to note anything special about the participant
    notes=models.TextField(blank=True,default='')

    # Demographic fields are not included for now.  I think they'll be better implemented via a link to a study that collected them
    # Payment method information could also be implemented here later

class ParticipantForm(ModelForm):
    class Meta:
        model=Participant
        fields=['tag', 'name', 'email', 'contact_type', 'data_share','notes']


############################ Tracking data downloads

class Download(models.Model):
    experiment=models.ForeignKey('Experiment',blank=True,null=True,on_delete=models.CASCADE)
    event_type=models.CharField(max_length=100)
    downloadDate=models.DateTimeField(auto_now_add=True)
    downloadSince=models.CharField(max_length=100)
    num_records=models.IntegerField(default=0)
    filename=models.CharField(max_length=100)

    def __unicode__(self):
        return self.experiment.name+'_'+self.downloadDate.strftime('%d%b%y:%H%M')

############################ Tracking suspicious upload events

class Security(models.Model):
    sessionToken=models.CharField(max_length=100)
    hit_count=models.IntegerField(default=0)
    locked=models.BooleanField(default=False)
    creationDate=models.DateTimeField(auto_now_add=True)
    securityLog=models.TextField()

    def __unicode__(self):
        return self.sessionToken

