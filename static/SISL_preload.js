/**
 * Created by PJR on 8/3/2015.
 */

// global variables for preload
preload_state='pre_start';
preload_start=window.performance.now();
var debug_preload=true;

function preload_draw() {
    if (preload_state == 'pre_start') {
        if (debug_preload) console.log("In pre_start");
        if (debug_preload) console.log("Group " + cfg['group'] + ", workerid=[" + ServerHelper.workerId + "]");
        preload_state = 'start_wait';
        ServerHelper.start_request();
    } else if(preload_state=='start_wait'){
        if(ServerHelper.start_received) {
            if(ServerHelper.fatal_error) {
                if (debug_preload) console.log(ServerHelper.error);
                preload_state='done_preload';
                return;
            }
            if (debug_preload) console.log("Got config info, sessionToken= "+ServerHelper.sessionToken);
            // process configuration information into variables
            parse_config();
            cfg_adjust();
            if (ServerHelper.consent_string!='') {
                console.log("Consent:");
                console.log(ServerHelper.consent_string);
                try {
                    consent_object = JSON.parse(ServerHelper.consent_string);
                    ServerHelper.consent_form = consent_object['consent_form'];
                } catch (e) {
                    console.log("error");
                    console.log(e);
                    ServerHelper.consent_form={};
                }
            } else {
                consent_form={};
            }
            preload_state='load_images';
        }
    } else if(preload_state=='load_images'){
        preload_images();
        if(ServerHelper.demo_mode || cfg['demo_mode']=='true') {
            // don't continue with preload -- no status or consent needed
            if (debug_preload) console.log("Demo mode, done with preload");
            start();
            return true;
        }
        preload_state='log_config';
    } else if(preload_state=='log_config') {
        if (config_parsed) { // don't continue until ready
            // put config into the response log to start
            response_log.push("Experiment app: " + _version);
            response_log.push("Source URL: " + document.URL);
            response_log.push("Run on " + new Date());
            response_log.push("");
            //for (key in cfg) { // config will be logged by empirical so this is probably not necessary
            //    response_log.push(key + ": " + cfg[key]);
            //}
            response_log.push("##########");
            preload_state = 'request_status';
        }
    } else if(preload_state=='request_status') {
        ServerHelper.request_status();
        preload_state='wait_status';
    } else if(preload_state=='wait_status') {
        if (ServerHelper.status_received) {
            if (debug_preload) console.log("Status received");
            // parse status
            if(ServerHelper.status!='' && ServerHelper.status!='None') {
                console.log(ServerHelper.status);
                console.log(ServerHelper.status_time);
                console.log(ServerHelper.status_since);
                t=ServerHelper.status.split(/\s+/);
                for(var i=0;i<t.length;i++) {
                    if(t[i]=='Trial:' && (i+1)< t.length) {
                        cfg['status-trials']=Number(t[i+1].trim());
                        if (debug_preload) console.log("Planning restart at trial "+cfg['status-trials'])
                        i++;
                    }
                    else if(t[i]=='Speed:' && (i+1)< t.length) {
                        cfg['status-speed']=Number(t[i+1].trim());
                        if (debug_preload) console.log("Planning restart at speed "+cfg['status-speed'])
                        i++;
                    }
                }
            }
            preload_state='done_preload';
        }
    } else if(preload_state=='done_preload') {
        // return without relaunching preload_draw
        if (debug_preload) {
            console.log("state: "+preload_state);
            console.log("Back to preload_experiment");
        }
        start(); // turning control back over to start the main app
        return;
    } else {
        if (debug_preload) console.log("Unknown state "+preload_state);
    }

    var elap=Math.floor((window.performance.now()-preload_start)/100.0); // 10ths of seconds since start
    var canvas = document.getElementById("mainWin");
    ctx.clearRect(0,0, canvas.width, canvas.height);
    if(elap<20) ctx.fillText("Loading...",canvas.width/2,canvas.height/2);
    else ctx.fillText("Loading slowly... "+(elap/10.0).toString(),canvas.width/2,canvas.height/2);
    requestId = window.requestAnimationFrame(preload_draw);
}


function preload_experiment(){
    preload_start=window.performance.now();
    console.log("Starting preload "+preload_state)
    ctx.font = "24px Arial";
    ctx.fillStyle='black';
    ctx.textAlign="center";
    //requestId=window.requestAnimationFrame(preload_draw);
    preload_draw();
}

// preloads the images -- but doesn't actually wait for load since it is not really needed for SISL
function preload_images(){
    var img_name_list=[];
    var im = new Image();

    ServerHelper.image_url+="sisl_images/"; // this could be drawn from config file to allow for image directories
    for(var i=0;i<session.length;i++) {
        if(session[i][0]=='Break:' && !contains(session[i][1],img_name_list)){
            img_name_list.push(session[i][1]);
        }
    }
    for(i=0;i<img_name_list.length;i++){
        im = new Image();
        im.src = ServerHelper.image_url+img_name_list[i];
        images[img_name_list[i]]=im;
    }
}



// SISL specific cfg processing and translation from .py coordinates (PsychoPy) to .js (canvas HTML5)
//  These also apply for SeVi

var cfg_strings=['key_list','letter_color', 'feedback', 'feedback_remove_cue', 'progress_bar', 'fixation_info', 'results_file', 'on_screen_feedback', 'trigrams_held_out']; // config tokens not to be converted to numbers
var cfg_colors=['background_color','cue_colors','target_color','letter_color','feedback_pos_color','feedback_neg_color']; // fixation

// .cfg parameters not yet processed
//   fixation point
//   progress bar
//   text feedback

// utilities for parse_config, contains and hex translation for colors
function contains(s,string_list){
    for(var i=0;i<string_list.length;i++){
        if (string_list[i]==s) {
            return(true);
        }
    }
    return(false);
}

function dec2hex(dec){
    hex=Number(parseInt(dec,10)).toString(16);
    if(hex.length==1) return("0"+hex);
    return(hex);
}

function convert_colors(tokens){
    var color_list=[];
    for(var i=0; i<tokens.length; i++) {
        // color format possibilities -- #aabbcc, color-name or 3 floats [-1.0,1.0]
        r=parseFloat(tokens[i]);
        if (isNaN(r)) {
            color_list.push(tokens[i]);
        } else {
            r=(r+1.0)*127.5;
            if (tokens.length > (i + 1)) {
                i++;
                g = (parseFloat(tokens[i])+1.0)*127.5;
                i++;
                b = (parseFloat(tokens[i])+1.0)*127.5;
            }
            else {
                g=r; b=r;
            }
            // scale from [-1.0, 1.0] to [#00, FF]
            color='#'+dec2hex(r)+dec2hex(g)+dec2hex(b);
            color_list.push(color);
        }
    }
    return(color_list);
}

// sets up the cfg array, which is global
function parse_config() {
    var config=ServerHelper.config_file;
    var j=0;
    var t=[];
    var args=[];
    var a='';
    var in_session_struct=false;

    if(config_parsed){  // don't re-parse if already loaded
        if (debug_preload) console.log("Attempted reparse of config...")
        return;
    } else {
        if (debug_preload) console.log("Config length: "+config.length)
    }

    // some initial cfg settings; should probably scale to window size; also set within SISL.html
    var canvas = document.getElementById("mainWin");
    //cfg['text_height']=20; // for on screen score elements
    //cfg['text_size']=18;
    //cfg['height']=canvas.height;
    //cfg['width']=canvas.width;

    // parse config
    var lines = config.split('\n');
    for (var i=0;i<lines.length;i++) {
        t=lines[i].trim().split(' ');
        if (lines[i][0]!='#' && t.length>0 && t[0].trim()!='') {
            args=[];
            if(t[0]=='session_begin{'){
                in_session_struct=true;
                // add preload images as the first session structure state
                session.push(["Preload:"]);
            }
            else if(t[0]=='}session_end') {
                in_session_struct = false;
            }
            else if(in_session_struct){
                // if in session struct, trim all the arguments and add to session structure list
                for(j=0;j<t.length;j++){
                    a=t[j].trim();
                    if(a.length>0) args.push(a);
                }
                session.push(args);
            }
            else { // otherwise add to cfg object
                if (contains(t[0], cfg_strings)) { // don't convert the parameters to numbers, keep as strings
                    for (j = 1; j < t.length; j++) {
                        a = t[j].trim();
                        if (a.length > 0) {
                            if (a.length == 1) args.push(a.toUpperCase()); // convert single keys to uppercase
                            else args.push(a);
                        }
                    }
                } else if (contains(t[0], cfg_colors)) {
                    args = convert_colors(t.slice(1)); // parse color information
                } else { // convert to numbers
                    for (j = 1; j < t.length; j++) args.push(Number(t[j].trim()));
                }
                // add args to cfg object, appending if this key already exists
                if (cfg.hasOwnProperty(t[0])) cfg[t[0]] = cfg[t[0]].concat(args);
                else {
                    if (args.length == 1) cfg[t[0]] = args[0]; // if only one value, don't store as list
                    else cfg[t[0]] = args;
                }
            }
        }
    }

    // parse session structure separately
    config_parsed=true;
}


function cfg_adjust(){ // modify parameters from PsychoPy structure to browser coordinates
    // Fill in z parameters if missing
    if(server_debug) console.log("In cfg adjust");
    if(cfg.hasOwnProperty('start_z')==false){
        cfg['start_z']=[];
        cfg['delta_z']=[];
        cfg['target_z']=[];
        for (i=0;i<cfg['num_keys'];i++) {
            cfg['start_z'].push(100);
            cfg['delta_z'].push(0);
            cfg['target_z'].push(100);
        }
    }

    // convert coordinate frame from PsychoPy to browser
    var scale=0.6; // perhaps proportional to layout size??

    // scale and change diameter to radius
    cfg['cue_size']=cfg['cue_size']*0.5*scale;
    cfg['target_diameter']=cfg['target_diameter']*0.5*scale;

    for (var i=0;i<cfg['num_keys'];i++) {
        cfg['start_x'][i]=(cfg['start_x'][i]*scale+layout.cue_area/2.0);
        cfg['target_x'][i]=(cfg['target_x'][i]*scale+layout.cue_area/2.0);
        cfg['delta_x'][i]=cfg['delta_x'][i]*scale;
        cfg['delta_y'][i]=cfg['delta_y'][i]*-1*scale;
        cfg['start_y'][i]=((layout.height/2.0)-cfg['start_y'][i])*scale;
        cfg['target_y'][i]=((layout.height/2.0)-cfg['target_y'][i])*scale;
        cfg['letter_x'][i]=(cfg['letter_x'][i]*scale+layout.cue_area/2.0);
        cfg['letter_y'][i]=(layout.height/2.0-cfg['letter_y'][i])*scale;
    }

    // font placement correction for onscreen letters
    cfg['letter_size']=cfg['letter_size']*scale;
    for(i=0;i<cfg['num_keys'];i++) cfg['letter_y'][i]=cfg['letter_y'][i]+cfg['letter_size']*2.0;
}


function old_preload_draw(){
    if(preload_state=='pre_group'){
        console.log("In pre-group");
        // get the session token
        // to do: check if demo -- add /demo to url request
        if(cfg.hasOwnProperty('demo')) {
            if (debug_preload) console.log("Demo mode: group token");
            workerId = 'demo';
        }else if(cfg.hasOwnProperty('workerId')) {
            workerId = cfg['workerId'];
        }else { //Tue Nov 17 2015 14:54:01 GMT-0600 (Central Standard Time)
            var d= new Date().toString().replace(/\S+\s(\S+)\s(\d+)\s(\d+)\s(\d+):(\d+):(\d+)\s.*/,'$2$1$3_$4$5$6');
            workerId='NoId_'+ d;
        }
        if (debug_preload) console.log("Group "+cfg['group']+", requesting sessiontoken for "+workerId);
        ServerHelper.group_session_request(cfg['group'],workerId);
        preload_state='group_wait';
    } else if(preload_state=='group_wait'){
        if(ServerHelper.group_session_received) {
            preload_state='pre_session';
            if(ServerHelper.sessionToken == 'Error:') {
                if (debug_preload) console.log(ServerHelper.xmlhttp.responseText);
                var t=ServerHelper.xmlhttp.responseText.split(' ');
                if(t[1]=='duplicate') {
                    terminate("It appears you have already done this study;If you think this message is in error;please contact the Experimenter");
                    return;
                }
                console.log(t[1]);
                terminate("Unable to establish session from server;Check your internet connection or contact the Experimenter");
                return; // terminate shouldn't kick back here but just in case
            }
            cfg['sessionToken']=ServerHelper.sessionToken;
            if (debug_preload) console.log("Got session: "+cfg['sessionToken'])
        }
    } else if(preload_state=='pre_session'){
        // to do: check if demo -- add /demo to url request
        if(cfg.hasOwnProperty('demo')) {
            if (debug_preload) console.log("Demo mode: session token");
            ServerHelper.request_config(cfg['sessionToken']+'/demo');
        }
        else {
            ServerHelper.request_config(cfg['sessionToken']);
        }
        preload_state='session_wait';
    } else if(preload_state=='session_wait'){
        if(ServerHelper.config_received){
            preload_state='load_images';
            parse_config();
            cfg_adjust();
        }
    } else if(preload_state=='load_images'){
        preload_images();
        if(demo_mode || cfg['demo_mode']=='true') {
            // don't continue with preload -- no status or consent needed
            if (debug_preload) console.log("Demo mode, done with preload");
            start();
            return true;
        }
        preload_state='log_config';
    } else if(preload_state=='log_config') {
        if (config_parsed) { // don't continue until ready
            // put config into the response log to start
            response_log.push("Experiment app: " + _version);
            response_log.push("Source URL: " + document.URL);
            response_log.push("Run on " + new Date());
            response_log.push("");
            if(cfg.hasOwnProperty('prompt')){
                console.log("Getting workerID");
                if (cfg['prompt']==1 || cfg['prompt']=='1'){
                    // prompt for name
                    workerId = prompt("Please enter your SONA participant ID number","NoId_" + d);
                    name_ok = /^[a-z0-9_]+$/i.test(workerId);
                    while (!name_ok) {
                        workerId = prompt("User id can only have numbers, letters, underscore:","NoId_" + d);
                        name_ok = /^[a-z0-9_]+$/i.test(workerId);
                    }
                }response_log.push("SubjectID: " + workerId);
                }
            for (key in cfg) {
                response_log.push(key + ": " + cfg[key]);
            }
            response_log.push("##########");
            preload_state = 'request_status';
        }
    } else if(preload_state=='request_status') {
        ServerHelper.request_status(cfg['sessionToken']);
        preload_state='wait_status';
    } else if(preload_state=='wait_status') {
        if (ServerHelper.status_received) {
            if (debug_preload) console.log("Status received");
            // parse status
            if(ServerHelper.status!='') {
                console.log(ServerHelper.status);
                t=ServerHelper.status.split(/\s+/);
                for(var i=0;i<t.length;i++) {
                    if(t[i]=='Trial:' && (i+1)< t.length) {
                        cfg['status-trials']=Number(t[i+1].trim());
                        if (debug_preload) console.log("Planning restart at trial "+cfg['status-trials'])
                        i++;
                    }
                    else if(t[i]=='Speed:' && (i+1)< t.length) {
                        cfg['status-speed']=Number(t[i+1].trim());
                        if (debug_preload) console.log("Planning restart at speed "+cfg['status-speed'])
                        i++;
                    }
                }
            }
            preload_state='request_consent';
        }
    } else if(preload_state=='request_consent') {
        if (debug_preload) console.log("Requesting consent form");
        ServerHelper.request_consent_form(cfg['sessionToken']);
        preload_state = 'wait_consent';
    } else if(preload_state=='wait_consent') {
        if (ServerHelper.consent_received) {
            if (debug_preload) console.log("Got consent form");
            if(ServerHelper.status=='None') consent_form={};
            else {
                try {
                    form = JSON.parse(ServerHelper.status);
                    consent_form = form['consent_form'];
                } catch(e) {
                    consent_form={};
                }
            }
            //console.log(consent_form);
            start();                                      // externally defined in the main app as handler to transition to main draw loop
            return true;
        }
    } else {
        if (debug_preload) console.log("Unknown state "+preload_state);
    }

    var elap=Math.floor((window.performance.now()-preload_start)/100.0); // 10ths of seconds since start
    var canvas = document.getElementById("mainWin");
    ctx.clearRect(0,0, canvas.width, canvas.height);
    if(elap<20) ctx.fillText("Loading...",canvas.width/2,canvas.height/2);
    else ctx.fillText("Loading slowly... "+(elap/10.0).toString(),canvas.width/2,canvas.height/2);
    requestId = window.requestAnimationFrame(preload_draw);
}