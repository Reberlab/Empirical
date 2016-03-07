__author__ = 'drlemur'

from django.conf import settings
import boto.mturk.connection, boto.mturk.question, boto.mturk.price
from django.core.mail import send_mail

# add form choice options: web page print, email links, or mturk posting
# for email, we will need the email addresses
# for mturk. we will need authentication

def mTurkHITs(credentials,tokenURL,numTokens,title,description,frame_height,amount):
    aws_id="%s" % credentials[0]
    aws_key="%s" % credentials[1]
    mturk = boto.mturk.connection.MTurkConnection(
        aws_access_key_id =  aws_id,
        aws_secret_access_key = aws_key,
        host = settings.MTURK_HOST
    )

    log="[%s], [%s]; " % (aws_id,aws_key)

    keywords = ["Cognitive Psychology"]
    questionform = boto.mturk.question.ExternalQuestion( tokenURL, frame_height )
    try:
        new_hit = mturk.create_hit(
            title = title,
            description = description,
            keywords = keywords,
            question = questionform,
            max_assignments = numTokens,
            reward = boto.mturk.price.Price( amount = amount))
        log+="Created hit %s, %s; " % (tokenURL,title)
    except boto.mturk.connection.MTurkRequestError as e:
        log+="Error: %s " % e.body
    return log

# Note: email invitations need a subject line, editable message text
#  and will have to log in/authenticate via an email server

def emailInvites(address_list,tokenList):
    log='Emailing participants'
    a=address_list.split()

    for i in range(min(len(a),len(tokenList))): # use whichever is shorter
        message="Per your request, you can participate in <Exp> by clicking this link or pasting it into your browser address bar: %s" % tokenList[i]
        log+='send_mail(subject,\'%s\',from_email,[%s]);' % (message,a[i])

    return log
