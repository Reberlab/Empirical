/**
 * Created by PJR on 8/5/2015.
 */

// var DEVELOPMENT_SERVER=true;
//var LIVE_MTURK='https://www.mturk.com/mturk/externalSubmit';
//var SANDBOX_MTURK='https://workersandbox.mturk.com/mturk/externalSubmit';

// https://www.reberlab.org/static/SISL.html?group=de945007aec0184d&assignmentId=123RVWYBAZW00EXAMPLE456RVWYBAZW00EXAMPLE&hitId=123RVWYBAZW00EXAMPLE&turkSubmitTo=https://www.mturk.com/&workerId=AZ3456EXAMPLE


var server_debug = true;

var ServerHelper = {
    server_url: '', // (DEVELOPMENT_SERVER) ? "http://127.0.0.1:8000/exp/" : "https://www.reberlab.org/exp/",
    image_url: '', //(DEVELOPMENT_SERVER) ? "http://127.0.0.1:8000/images/" : "https://www.reberlab.org/images/",
    xmlhttp: new XMLHttpRequest(),
    groupToken: '',
    sessionToken: "",
    config_file: "",
    consent_string: "",  // this is the original JSON string from Empirical
    consent_form: {},    // which gets parsed into an object
    workerId: "",
    prompt_string: "Please enter your User ID:",
    fatal_error: false,
    error: "",
    response_log: "",
    status: "",
    status_time: "",
    status_since: 0.0,
    demo_mode: false,
    mturk: false,
    mturk_submit: '',
    mturk_info: '',
    start_requested: false,
    start_received: false,
    data_logged: false,
    upload_requested: false,
    upload_in_progress: false,
    upload_queue: [],
    upload_connection_log: '',

    empirical_start: function(url) {
        var params={};
        var q=url.split('?');
        u = new URL(url);
        if (u.port=='' || u.port==80) host=u.hostname;
        else host=u.hostname+':'+u.port
        this.server_url = u.protocol + '//' + host +'/exp/';
        this.image_url = u.protocol + '//' + host + '/images/';
        if (q.length<2) return(params);
        q = q[1].split('&');
        for(var i=0;i < q.length;i++) {
            var t=q[i].split('=');
            if(t.length==1) params[t[0]]='None';
            else if(t.length==2) params[t[0]]=t[1];
            else params[t[0]]= t.slice(1);
        }
        if (params.hasOwnProperty('group')) {
            this.groupToken = params['group'];
        } else {
            this.error="No group token in URL";
            this.fatal_error=true;
        }
        if (params.hasOwnProperty('workerId')) this.workerId = params['workerId'];
        else if (params.hasOwnProperty('workerid')) this.workerId = params['workerid'];
        else if (params.hasOwnProperty('name')) this.workerId = params['name'];
        else this.workerId='';
        if (this.workerId=='demo' || params.hasOwnProperty('demo')) this.demo_mode=true;
        else if (this.workerId=='prompt' || params.hasOwnProperty('prompt')) {  // can't prompt if demo mode
            // prompt for name/sona id
            var typed_name = prompt(ServerHelper.prompt_string);
            name_ok = /^[a-z0-9_]+$/i.test(typed_name);
            while (!name_ok) {
                typed_name = prompt("User id can only have numbers, letters or underscore:");
                name_ok = /^[a-z0-9_]+$/i.test(typed_name);
            }
            this.workerId=typed_name;
            response_log.push("SubjectID: " + this.workerId);
        }
        if (params.hasOwnProperty('assignmentId')) { // this is an mturk session
            this.mturk=true;
            if (params['assignmentId']=='ASSIGNMENT_ID_NOT_AVAILABLE') {
                this.demo_mode=true;
            } else {
                var mturk_info="assignmentId=" + params['assignmentId'] + "\n";
                if (params.hasOwnProperty('hitId')) mturk_info+="hitId=" + params['hitId'] + "\n";
                mturk_info+="workerId=" + this.workerId + "\n";
                if (params.hasOwnProperty('turkSubmitTo')) mturk_info+="turkSubmitTo=" + params['turkSubmitTo'] + "\n";
                this.mturk_submit=params['turkSubmitTo'];
                this.mturk_info=mturk_info;
            }
        }
        return(params);
    },

    start_request: function() {
        if (this.start_requested) {
            if (server_debug) console.log("Multiple calls to start_request");
            return;
        }
        if (this.demo_mode) {
            start_request_url = this.server_url + 'start/' + this.groupToken + '/demo';
        }
        else if (this.workerId=='') {
            var start_request_url = this.server_url + 'start/' + this.groupToken;
        } else {
            start_request_url = this.server_url + 'start/' + this.groupToken + '/' + this.workerId;
        }
        this.xmlhttp.addEventListener('load', this.start_receive);
        this.xmlhttp.open("GET", start_request_url, true);
        this.xmlhttp.send();
        this.start_requested = true;
    },

    start_receive: function() {
        if (this.start_received || this.config_received) {
            if (server_debug) console.log("Multiple calls to start_receive");
            return;
        }
        if (ServerHelper.xmlhttp.readyState == 4) {
            ServerHelper.start_received = true;
            if (ServerHelper.xmlhttp.status == 200) {
                var response = ServerHelper.xmlhttp.responseText;
                parser = new DOMParser();
                xmlDoc = parser.parseFromString(response,"text/xml");
                //console.log("text: "+response.slice(0,200));
                // the response is an XML object with the session token, workerid,  config file and consent form
                ServerHelper.sessionToken = xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","session")[0].childNodes[0].nodeValue;
                //console.log("session "+ ServerHelper.sessionToken);
                ServerHelper.workerId = xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","workerid")[0].childNodes[0].nodeValue;
                ServerHelper.config_file = xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","config")[0].childNodes[0].nodeValue;
                ServerHelper.consent_string = xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","consent")[0].childNodes[0].nodeValue;
                //console.log("session "+ ServerHelper.sessionToken);
                //console.log("worker "+ServerHelper.workerId);
                // console.log("config "+ServerHelper.config_file.slice(0,200));
                // console.log("consent "+ServerHelper.consent_form.slice(0,200));
                // what happens if the XML isn't parsed properly?
            } else {
                ServerHelper.fatal_error=true;
                ServerHelper.error = ServerHelper.xmlhttp.statusText;
            }
        }
    },


    request_status: function () {
        var url = this.server_url + 'status/' + this.sessionToken + '/' + this.workerId;
        this.xmlhttp = new XMLHttpRequest();
        this.xmlhttp.addEventListener('load', this.get_status);
        this.xmlhttp.open("GET", url, true);
        this.xmlhttp.send();
    },

    get_status: function () {
        if (ServerHelper.xmlhttp.readyState == 4) {
            ServerHelper.status_received = true;
            if (ServerHelper.xmlhttp.status == 200) {
                //ServerHelper.status = ServerHelper.xmlhttp.responseText;
                if (ServerHelper.xmlhttp.responseText == 'None') {
                    ServerHelper.status='None';
                    ServerHelper.status_time='None';
                    ServerHelper.status_since='None';
                } else {
                    var response = ServerHelper.xmlhttp.responseText;
                    parser = new DOMParser();
                    xmlDoc = parser.parseFromString(response,"text/xml");
                    //console.log("text: "+response.slice(0,200));
                    ServerHelper.status=xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","status")[0].childNodes[0].nodeValue;
                    ServerHelper.status_time=xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","uploaddate")[0].childNodes[0].nodeValue;
                    ServerHelper.status_since=Number(xmlDoc.getElementsByTagNameNS("https://www.reberlab.org/","timesince")[0].childNodes[0].nodeValue);
                }
            } else {
                ServerHelper.error = ServerHelper.xmlhttp.statusText;
            }
        }
    },

    upload_data: function (event_type, response_log) {            // start the upload process by requesting the form to get the csrf token
        // stringify response log
        var data = "";
        for (var i = 0; i < response_log.length; i++) {
            data = data + response_log[i] + "\n";
        }

        if (this.upload_in_progress) {
            // queue the next upload file
            this.upload_queue.push([event_type, data]);
            if (server_debug) console.log('queued a ' + event_type);
            return;
        }
        this.event_type = event_type;
        this.response_log = data;
        var url = this.server_url + 'report/' + this.sessionToken;
        this.xmlhttp = new XMLHttpRequest();
        this.xmlhttp.addEventListener('load', this.upload_ready);
        this.xmlhttp.open("GET", url, true);
        this.xmlhttp.send();
        this.upload_in_progress = true;
    },

    upload_from_queue: function () {
        if (this.upload_queue.length == 0) {
            this.upload_in_progress = false;
            return;
        }
        var next_upload = this.upload_queue.pop();
        this.event_type = next_upload[0];
        this.response_log = next_upload[1];          // get the next element

        this.xmlhttp = new XMLHttpRequest();
        var url = this.server_url + 'report/' + this.sessionToken;
        this.xmlhttp.addEventListener('load', this.upload_ready);
        this.xmlhttp.open("GET", url, true);
        this.xmlhttp.send();
    },

    upload_ready: function () { // or just xmlhttp post?
        if (ServerHelper.xmlhttp.readyState != 4) {
            if (server_debug) console.log("Server state " + ServerHelper.xmlhttp.readyState.toString());
            ServerHelper.upload_connection_log+='.';  // adds '.' whenever this is called but server wasn't ready
            return;
        } else if (ServerHelper.xmlhttp.status != 200) { // form request didn't work... should recover
            if (server_debug) console.log("upload error");
            // store a record of response errors
            ServerHelper.upload_connection_log+='status_error_'+ServerHelper.xmlhttp.status.toString()+';';
            terminate(ServerHelper.xmlhttp.statusText); // does this end the program or fail silently?
        }

        // find csrf token
        //console.log("form response "+ServerHelper.xmlhttp.responseText);
        var token_loc = ServerHelper.xmlhttp.responseText.search("csrfmiddlewaretoken");
        if (token_loc < 0) {
            if (server_debug) console.log(ServerHelper.xmlhttp.responseText);
            // this should be logged as well
            ServerHelper.upload_connection_log+='csrf_error;'
        }
        else var csrf_token = ServerHelper.xmlhttp.responseText.slice(token_loc).match("value=\'([^\']*)'")[1];

        var formData = new FormData();
        formData.append("csrfmiddlewaretoken", csrf_token);
        formData.append("eventType", ServerHelper.event_type);
        formData.append("sessionToken", ServerHelper.sessionToken);
        formData.append("dataLog", ServerHelper.response_log);

        ServerHelper.xmlhttp = new XMLHttpRequest();
        ServerHelper.xmlhttp.open("POST", ServerHelper.server_url + 'report/' + ServerHelper.sessionToken);
        ServerHelper.xmlhttp.send(formData);
        if (server_debug) console.log("data sent " + ServerHelper.event_type);
        // log successes
        ServerHelper.upload_connection_log+='data_upload_sent('+ServerHelper.response_log.length.toString()+'_bytes);';

        // report on upload errors here...

        // if there is a queue, start the next upload
        if (ServerHelper.upload_queue != []) {
            ServerHelper.upload_from_queue();
        }
        else ServerHelper.upload_in_progress = false;
    },

    // Create form to submit the final data to mturk
    upload_to_mturk: function(summary) {
        var url = decodeURIComponent(ServerHelper.mturk_submit) + '/mturk/externalSubmit'; // this is supposed to be constructed from URL params...

        // this was assembled initially but not uploaded until the end
        this.upload_data('private',this.mturk_info);

        var form_holder = document.getElementById("formholder");
        if(server_debug) console.log("setting form");
        var mturk_response=summary+';sesssionToken='+this.sessionToken+';groupToken='+this.groupToken+';connection_log='+ServerHelper.upload_connection_log;
        var formString = "<form action=\"" + url + "\" method=\"post\"><input type=\"hidden\" name=\"assignmentId\" value=\"" + cfg['assignmentId'] +
            "\">Press Submit to finish this experiment <input type=\"hidden\" name=\"dataLog\" value=\"" + mturk_response + "\"> <input type=\"submit\" value=\"Submit\"></form>";
        if(server_debug) console.log(formString);
        form_holder.innerHTML = formString;
    },


    // I do not know why the following does not work -- it throws a CORS error, but user clicked button form works
    /*mturk_send_complete: function(assignmentId,dataLog,submitUrl){
        console.log('Attempting submit');
        console.log(assignmentId);
        console.log(submitUrl);
        console.log(dataLog);
        if(submitUrl=='') submitUrl=default_mturk_url;
        var formData = new FormData();
        formData.enctype="text/plain";
        formData.append("assignmentId", assignmentId);
        formData.append("dataLog", dataLog);
        ServerHelper.mturk_x = new XMLHttpRequest();
        ServerHelper.mturk_x.addEventListener('load',ServerHelper.mturk_complete);
        ServerHelper.mturk_x.addEventListener('error',ServerHelper.mturk_error);
        submitUrl=submitUrl+"?assignmentId="+assignmentId+"&summary="+dataLog;
        console.log("to: "+submitUrl);
        ServerHelper.mturk_x.open("POST", submitUrl);
        ServerHelper.mturk_x.send(formData);
        //console.log(formData.getAll('assignmentId'));
        console.log("mturk data sent to "+submitUrl);
    },

    mturk_complete: function() {
        console.log("Loaded");
        console.log(ServerHelper.xmlhttp.readyState);
        console.log(ServerHelper.xmlhttp.status);
        console.log(ServerHelper.xmlhttp.statusText);
        console.log('---');
    },
    mturk_error: function() {
        console.log("Error");
        console.log(ServerHelper.xmlhttp.readyState);
        console.log(ServerHelper.xmlhttp.status);
        console.log(ServerHelper.xmlhttp.statusText);
        console.log('---');
    }*/

};



