/**
 * Created by Ben Reuveni on 11/16/2015.
 */


function startFallingStimsExp(params){

    var bns = cfg["exp_control"].bns;
    // checks to see whether we want to "restart" or not. If not, the experiment will always begin from trial 1
    if (cfg["exp_control"].hasOwnProperty('restart') && cfg["exp_control"].restart == 1){
        if (bns === 1){
            trial_count_12 = params['trialCount12'];
            trial_count_34 = params['trialCount34'];
        }
        trialCount = params['trialCount'];
    }else {
        trialCount = 0;
        var trial_count_12 = 0;
        var trial_count_34 = 0;
    }

    // a listener for navigating away from the page. "warn_termination" is in the "Functions" section.
    window.onbeforeunload = warn_termination;

    var current_window_height = window.innerHeight;
    var current_window_width = window.innerWidth;

    // this creates the 3 canvases we will use in the exp.
    var canvas_space = document.getElementById("canvas_holder");
    canvas_space.innerHTML = ( '<canvas id="mainWin" width="600" height="600" style = " position: fixed; margin: 20px 0px 0px 10%;  border: 1px solid black"></canvas> ' +
        '<canvas id="basketWin" width="600" height="100" style="position: fixed; margin: 520px 0px 0px 10%;  z-index: 1; border: 1px solid black"></canvas>' +
        '<canvas id="leverWin" width="600" height="100" style="position: fixed; margin: 400px 0px 0px 10%; z-index: 2"></canvas>');

    var lever_win = document.getElementById('leverWin').getContext("2d"); // creates a window reference.
    var basket_win = document.getElementById('basketWin').getContext("2d"); // creates a window reference.
    var inst_page = document.getElementById("canvas_holder");

    // controls whether information is pushed to the console.
    var debug = 1;

    var canvas_space = document.getElementById("canvas_holder");
    canvas_space.style.float = "";
    canvas_space.style.margin = "auto";

    var win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
    var canvas = document.getElementById('mainWin');
    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    var halfW = winWidth / 2;
    var halfH = winHeight / 2;
    var corrImg = images[cfg["exp_control"].stimList.length-4];
    var incorrImg = images[cfg["exp_control"].stimList.length-3];
    var basket = images[cfg["exp_control"].stimList.length-1];
    var inst_page_1 = images[cfg["exp_control"].stimList.length-6];
    var inst_page_2 = images[cfg["exp_control"].stimList.length-5];

    win.font = "30px Arial";
    win.textAlign = 'center';
    win.fillStyle = "#fFfFfF";

// These variables will end up coming from a .cfg file - These lines need to be modified to refer to the JSON that contains them
    var desired_OST = (cfg["timings"].stimTimeout); // in seconds.
    //var fixateTimeout = cfg["timings"].fixateTimeout;
    var feedbackTimeout = cfg["timings"].feedbackTimeout;
    var itiTimeout = cfg["timings"].itiTimeout;
    var fixateTimeout = 0; // for Falling Stims, this should be 0

    var trialBeforeBreak = cfg["exp_control"].trialBeforeBreak;
    var trialsBeforeTest = cfg["exp_control"].trialBeforeTest;
    var trialsBeforeEnd = cfg["exp_control"].trialBeforeEnd;

    var stimLabels = cfg["exp_control"].stimLabels;
    var stimSF = cfg["stim_params"].SF;
    var stimOri = cfg["stim_params"].Ori;

    if (bns == 1){
        var trialsBeforeP2 = cfg["exp_control"].trialBeforeP2;
        var trialsBeforeP3 = cfg["exp_control"].trialBeforeP3;

        var img_input_p1 = images.slice(0,940);
        var img_input_p2 = images.slice(940, 1881);
        var stimImg_input_1 = cfg["exp_control"].stimOrder.slice(0,940);
        var stimImg_input_2 = cfg["exp_control"].stimOrder.slice(940, 1881);
        var stim_sf_12 = cfg["stim_params"].SF.slice(0,940);
        var stim_sf_34 = cfg["stim_params"].SF.slice(940,1881);
        var stim_ori_12 = cfg["stim_params"].Ori.slice(0,940);
        var stim_ori_34 = cfg["stim_params"].Ori.slice(940,1881);
        var stimLabels_12 = cfg["exp_control"].stimLabels.slice(0,940);
        var stimLabels_34 = cfg["exp_control"].stimLabels.slice(940, 1881);
    }

// (un)comment this block for debugging

    // var trialBeforeBreak = 5;
    //
    // var trialsBeforeP2 = 10;
    // var trialsBeforeP3 = 15;
    // var trialsBeforeTest = 20;
    // var trialsBeforeEnd = 25;
    // var feedbackTimeout = 0.1;
    // var itiTimeout = 0.1;
    // var desired_OST = 1.5; // normally 1.5


// -------------------------------

    // this bit takes a desired on screen time (OST) and translates it into rate of change for the stim.
    var img_size = images[0].height; // Iterates the image based on trialCount
    var stim_rot = (((winHeight - 190 - (img_size/3)) / desired_OST) / 60).toFixed(2);
    stim_rot = Number(stim_rot);


// magic numbers for keeping track of stuff.
    var masterClock = 0;
    var startTime = 0;
    var endTime = 0;
    var introSlide = 0; // controls which intro text to show (iterates each time in "doBegin").
    var block = 1;
    var NACount = 0;
    var catResp = []; //will hold all 1/0 based on cat answers in order to calculate accuracy at the end
    var total_catAcc = 0; // the final number
    var test_Resp = [];
    var test_count = [];
    var test_catAcc = 0;
    var blockRespCat = [];
    var blockAccCat = 0;
    var showFeedback = 1; // controls whether to display feedback or not.
    var showTestText = 0; // controls whether to display test text or break text in onBreak.
    var lever_has_changed = 0;
    var started = false;
    var status_info = ["trial: " + trialCount, "date:" + new Date().toString()];
    var curr_trial = null;
    var curr_sf = null;
    var curr_ori = null;


    var response = {
        "trial": 0,
        "totalTime": 0,
        "stimImg": null,
        "label": null,
        "response": 'NA',
        "feedback": null,
        "hitMiss": null,
        "duration": 0,
        "subj": params["workerId"]
    };

    var stim = {
        "pos_X": halfW,
        "pos_Y": 0,
        "rot": stim_rot,
        "slide_direction": null // this will determine whether the stim will slide left (0) or right (1)
    };

    var keyDict = {
        'd': 1,
        'D': 1,
        'k': 2,
        'K': 2,
        32: 32,
        'NA': 'NA'
    };


    // checks the server to see what trial to begin on (in case someone stopped mid-way).


// data related stuff
    var data = [];
    var currentdateStart = new Date();
    var dateTimeStart = 'Experiment Began: '
        + currentdateStart.getDate() + "/"
        + (currentdateStart.getMonth()+1)  + "/"
        + currentdateStart.getFullYear() + " @ "
        + currentdateStart.getHours() + ":"
        + currentdateStart.getMinutes() + ":"
        + currentdateStart.getSeconds();

    data.push('Lead Investigator: Ben Reuveni');
    data.push('IRB protocol # STU00201660');
    data.push('SessionId is: ' + params["session"]);
    data.push('GroupId is: ' + params["group"]);
    data.push('WorkerID is: ' + params["workerId"]);
    data.push('AssignmentID is: ' + params["assignmentId"]);
    data.push('Fixation Timeout: ' + fixateTimeout);
    data.push('Stimulus Timeout: ' + desired_OST * 1000);
    data.push('Response Timeout: ' + desired_OST * 1000);
    data.push('Feedback Timeout: ' + feedbackTimeout);
    data.push('ITI: ' + itiTimeout);

    data.push('\n\nTrials Before Break: ' + trialBeforeBreak);
    data.push('Trials Before Test: ' + trialsBeforeTest);
    data.push('Trials Before End: ' + trialsBeforeEnd);
    data.push('Total Trials: ' + cfg["exp_control"].stimList.length);

    data.push(dateTimeStart+'\n\n');

    data.push("trial total_time sf ori stimImg label response feedback hit/miss RT block subj_session_token");

    if (trialCount === 0) {
        if (cfg["exp_control"].hasOwnProperty('upload') && cfg["exp_control"].upload == 0) {
            console.log('Not uploading');
            console.log(data);

        }else{
            status_info = ["trial: " + 3, "date:" + new Date().toString()];
            ServerHelper.upload_data('initial', data);
            ServerHelper.upload_data('status', status_info);
        }


    }

    if (desired_OST * 1000 > 1000){
        var s = 's'
    }

// task related text (instructions, break, end, etc.)

        var introText = 'In this experiment, you will be shown a series of circular sinewave gratings.\n\nThese images vary on 2 dimensions: bar thickness and bar orientation. ' +
            'These sinewaves belong to either category A or category B.' +
            '\n\nCategorize each image by pressing "d" for A, or "k" for B.' +
            '\n\nPlease note that you have ' + desired_OST + ' second' + s + ' to make your decision.' +
            '\n\nPress any key to advance.';

        var introText2 = 'Please also note the following:' +
            '\n\nThe Square image is a mask, and is only meant to cover up the circular sinewave. It contains no information about the correct category and can be ignored.' +
            '\n\nYou may only respond while the circular Sinewave grating is on the screen' +
            '\n\nIf you respond with a button other than "d" or "k" it will count as a mistake.\n\nPress any key to begin';

        var testText = '\n\n\n\nThe following block is the final test. You will no longer be given feedback for your choices.' +
            '\n\nPlease press any button to begin.';

        var intervention = "\nIt seems like you're not doing as well as you were in the first block." +
            "\n\nWe have found that people tend to do best in these circumstances when they 'go with their gut' or even guess." +
            "\nTry that out as best you can.\n\nPress any key to continue.";



    var breakText = '';
    var endText = '\n\n\n\nThank you for participating in this study.\n\nPlease inform the researcher that you have finished.';


    /* Functions */

        // changes the direction of the lever based on keypress.
        function doLeverChange(event) {
            endTime = performance.now();
            document.removeEventListener('keydown', doLeverChange, false);
            lever_has_changed = 1;

            var k = String.fromCharCode(event.keyCode);
            if (k === 'd' || k === 'D' || k === 'k' || k === 'K') {

                response.duration = (endTime - startTime) / 1000;
                response.duration = response.duration.toFixed([4]);
                response.response = keyDict[k];
                response.totalTime = endTime / 1000;
                response.totalTime = response.totalTime.toFixed([4]);

                if (k === 'd' || k === 'D') {

                    lever_win.clearRect(0, 0, 600, 100);
                    lever_win.beginPath();
                    lever_win.moveTo(356, 0); //(100,0)
                    lever_win.lineTo(256, 100); // (0,100)
                    lever_win.lineWidth = 2;
                    lever_win.stroke();
                    if (debug === 1) {
                        console.log('in doLever');
                        console.log('state is ' + fsm.current);
                    }

                    stim.slide_direction = 0;

                } else if (k === 'k' || k === 'K') {
                    lever_win.clearRect(0, 0, 600, 100);
                    lever_win.beginPath();
                    lever_win.moveTo(256, 0);
                    lever_win.lineTo(356, 100);
                    lever_win.lineWidth = 2;
                    lever_win.stroke();
                    if (debug === 1) {
                        console.log('in doLever');
                        console.log('state is ' + fsm.current);
                    }
                    stim.slide_direction = 1;
                }
            }
        }


    // this function moves us on from our "breaks".
    function breakOut() {
        document.removeEventListener('keydown', breakOut, false);
        win.clearRect(0,0, winWidth, winHeight); 
        fsm.showFixation();
    }

    function wrapText(context, text, x, y, maxWidth, lineHeight) {
        var cars = text.split("\n");

        for (var ii = 0; ii < cars.length; ii++) {

            var line = "";
            var words = cars[ii].split(" ");

            for (var n = 0; n < words.length; n++) {
                var testLine = line + words[n] + " ";
                var metrics = context.measureText(testLine);
                var testWidth = metrics.width;

                if (testWidth > maxWidth) {
                    context.fillText(line, x, y);
                    line = words[n] + " ";
                    y += lineHeight;
                }
                else {
                    line = testLine;
                }
            }
            context.fillText(line, x, y);
            y += lineHeight;
        }
    }

    function DrawText(text) {
        win.clearRect(0,0, winWidth, winHeight); 
        var maxWidth = winWidth;
        var lineHeight = 35; // defines the spacing between lines.
        var x = halfW; // (canvas.width - maxWidth) / 2;
        var y = halfH * 0.2; // the multiplier here decides how far from the top of the canvas text will start. Smaller === higher up.

        wrapText(win, text, x, y, maxWidth, lineHeight);
    }

    function doBegin() {
        win.clearRect(0,0, winWidth, winHeight);
        document.removeEventListener('keydown', doBegin, false);
        introSlide++;

        // this bit will allow us to display multiple instructions. Just add new "else if" before the "else"
        if (introSlide === 1) {
            document.addEventListener('keydown', doBegin, false);
            //DrawText(introText2);
            win.drawImage(inst_page_2, 0 , 0, canvas.width, canvas.height);
            started = true;
        }

        //else if (introSlide === 2){} // if we need another intro text screen.

        else {
            canvas.style.marginLeft = "10%";
            canvas.height = 600;
            canvas.width = 600;
            basket_win.canvas.style.border = "1px solid black";
            win.font = "30px Arial";
            win.textAlign = 'center';
            win.fillStyle = "#fFfFfF";
            fsm.showFixation();
        }
    }

    function getMousePos1(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        return {
            x: Math.round((evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width),
            y: Math.round((evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height)
        };
    }

    // make a button here!

    function backToMain(evt) {
        var mousePoss = getMousePos1(canvas, evt);
        var message = mousePoss.x + ',' + mousePoss.y;
        if (debug === 1) {
            console.log(message.slice(0, 3));
            console.log(message.slice(4, 8));
        }

        if (200 <= mousePoss.x && mousePoss.x <= 400 && 400 <= mousePoss.y && mousePoss.y <= 475) {
            canvas.removeEventListener('click', backToMain, false);
            window.location = empiricalMainPage;
        }
    }

    function warn_termination() {
        // data and status upload

        if (cfg["exp_control"].hasOwnProperty('upload') && cfg["exp_control"].upload == 0) {
            console.log('Not uploading');
            console.log(data);

        }else {

            ServerHelper.upload_data('nav away. block: ' + block + ', trial: ' + trialCount, data);
            var status_info_unload = ["trial: " + trialCount, "date:" + new Date().toString()];
            ServerHelper.upload_data('status', status_info_unload);


            return "Looks like you're attempting to navigate away.\n\n" +
                "If you're attempting to submit the completed HIT, you can ignore this message.\n\n" +
                "If you are still working on the experiment, if it's not too much trouble, " +
                "please click on 'Stay on this Page' or 'Don't Reload' and then feel free to navigate away.\n\n" +
                "This will allow us to upload any data you've accumulated so far.\n\n" +
                "Thank you!"
        }
        //return "Session not completed yet."
    }

    /* FSM */

    var fsm = StateMachine.create({ // Version 2 self-contained.
        //initial: 'wait',
        events: [
            { name: "start",         from: 'none',                                                 to: 'instructions'},
            { name: 'showFixation',  from: ['break', 'ITI', 'none', 'instructions'],               to: 'fixation' },
            { name: 'showStim',      from: 'fixation',                                             to: 'stim'    },
            { name: 'showFeedback',  from: ['stim'],                                               to: 'feedback' },
            { name: 'showTooSlow',   from: ['stim'],                                               to: 'tooSlow' },
            { name: 'showITI',       from: ['feedback', 'tooSlow', 'stim'],                        to: 'ITI'  },
            { name: 'showBreak',     from: 'ITI',                                                  to: 'break'  },
            { name: 'showFinish',    from: 'ITI',                                                  to: 'end'  }
        ],
        callbacks: {

            oninstructions: function(event, from, to){
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                //alert('The following dialog box will contain your receipt token.\n\nPlease press Ctrl+C to copy it');
                //alert('987654321');
                //DrawText(introText);
                //canvas.style.float = "";
                canvas.style.marginLeft = "10%";
                canvas.height = 700;
                canvas.width = canvas.height*1.7;
                basket_win.canvas.style.border = "none";

                win.drawImage(images[cfg["exp_control"].stimList.length-6], 0 , 0, canvas.width, canvas.height);
                //win.drawImage(inst_page_1, 0 , 0, canvas.width, canvas.height);
                document.addEventListener('keydown', doBegin, false);
            },

            onfixation:  function(event, from, to)  { // show fixate
                startTime = null;
                endTime = null;
                lever_has_changed = 0;
                if (masterClock === 0){
                    masterClock = performance.now();
                }
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                    console.log("NA Count is: " + NACount);
                }
                //win.font = "50px Arial";
                //win.fillText('+', halfH, halfW);
                //win.font = "30px Arial";
                response.trial = trialCount;

                window.setTimeout(function(){
                    win.clearRect(0,0, winWidth, winHeight);
                    fsm.showStim();
                },itiTimeout);
            },

            onstim:  function(event, from, to)      { // show image, wait for key or timeout
                
                if (bns === 1) {
                    if (debug === 1) {
                        console.log("in bns mode");
                        console.log(trialCount);
                        console.log(trialsBeforeP2, trialsBeforeP3);
                        console.log(trialCount < trialsBeforeP2);
                        console.log(trialCount > trialsBeforeP2 && trialCount < trialsBeforeP3);
                        console.log(trialCount > trialsBeforeP3);
                    }
                    if (trialCount < trialsBeforeP2){
                        if (debug === 1) {
                            console.log("in block 1");
                        }
                        img = img_input_p1[trial_count_12];
                        response.stimImg = stimImg_input_1[trial_count_12];
                        response.label = stimLabels_12[trial_count_12];
                        //curr_trial = trial_count_12;
                        curr_sf = stim_sf_12[trial_count_12];
                        curr_ori = stim_ori_12[trial_count_12];
                        trial_count_12++;

                    }else if (trialCount >= trialsBeforeP2 && trialCount < trialsBeforeP3){
                        if (debug === 1) {
                            console.log("in block 2 or 3");
                        }
                        if ( Math.random() > 0.25){
                            if (debug === 1) {
                                console.log("showing 34s");
                            }
                            img = img_input_p2[trial_count_34];
                            response.stimImg = stimImg_input_2[trial_count_34];
                            //curr_trial = trial_count_34;
                            curr_sf = stim_sf_34[trial_count_34];
                            curr_ori = stim_ori_34[trial_count_34];
                            trial_count_34++;

                            if (stimLabels_34[trial_count_34] === 3){
                                response.label = stimLabels_34[trial_count_34] - 1;
                            }else if (stimLabels_34[trial_count_34] === 4){
                                response.label = stimLabels_34[trial_count_34] - 3;
                            }
                        }else{
                            if (debug === 1) {
                                console.log("showing 12s");
                            }
                            img = img_input_p1[trial_count_12];
                            response.stimImg = stimImg_input_1[trial_count_12];
                            response.label = stimLabels_12[trial_count_12];
                            //curr_trial = trial_count_12;
                            curr_sf = stim_sf_12[trial_count_12];
                            curr_ori = stim_ori_12[trial_count_12];
                            trial_count_12++;
                        }
                    }else if (trialCount >= trialsBeforeP3){
                        if (debug === 1) {
                            console.log("in block > 3");
                        }
                        if (Math.random() > 0.35){
                            if (debug === 1) {
                                console.log("showing 34s");
                            }
                            img = img_input_p2[trial_count_34];
                            response.stimImg = stimImg_input_2[trial_count_34];
                            //curr_trial = trial_count_34;
                            curr_sf = stim_sf_34[trial_count_34];
                            curr_ori = stim_ori_34[trial_count_34];
                            trial_count_34++;

                            if (stimLabels_34[trial_count_34] === 3){
                                response.label = stimLabels_34[trial_count_34] - 1;
                            }else if (stimLabels_34[trial_count_34] === 4){
                                response.label = stimLabels_34[trial_count_34] - 3;
                            }
                        }else{
                            if (debug === 1) {
                                console.log("showing 12s");
                            }
                            img = img_input_p1[trial_count_12];
                            response.stimImg = stimImg_input_1[trial_count_12];
                            response.label = stimLabels[trial_count_12];
                            //curr_trial = trial_count_12;
                            curr_sf = stim_sf_12[trial_count_12];
                            curr_ori = stim_ori_12[trial_count_12];
                            trial_count_12++;
                        }
                    }
                }else {
                    if (debug === 1) {
                        console.log("not in bns mode");
                    }
                    img = images[trialCount]; // Iterates the image based on trialCount
                    response.stimImg = cfg["exp_control"].stimOrder[trialCount];
                    response.label = stimLabels[trialCount];
                    //curr_trial = trialCount;
                    curr_sf = stimSF[trialCount];
                    curr_ori = stimOri[trialCount];
                }
                trialCount++;
                lever_win.clearRect(0, 0, 600, 100);
                basket_win.drawImage(basket, 100, 0, 145,100);
                basket_win.drawImage(basket, 369, 0, 145,100);

                // draw lever
                lever_win.beginPath();
                lever_win.moveTo(305, 100); //(50,100)
                lever_win.lineTo(305, 0); //(50,0)
                lever_win.lineWidth = 2;
                lever_win.stroke();

                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                    console.log('trail number: ' + trialCount);
                }

                startTime = performance.now();
                window.requestAnimationFrame(stim_Show);

                function stim_Show() {
                    if (lever_has_changed === 0) {
                        document.addEventListener('keydown', doLeverChange, false);
                    }

                    win.clearRect(0,0, winWidth, winHeight);
                    win.drawImage(img, (stim.pos_X - (img.width/3)/2.3) , stim.pos_Y, img.height/3, img.width/3);


                    // if image is above the critical line, move it down.
                    if (stim.pos_Y < winHeight-190-img.height/3){
                        stim.pos_Y += stim.rot;
                        window.requestAnimationFrame(stim_Show);

                    // if the image has "hit" the lever, slide it the appropriate way OR if no button was pressed, "too slow"
                    }else if(stim.pos_Y > winHeight-190-img.height/3 && stim.pos_Y < winHeight-50-img.height/3){

                        if (stim.slide_direction === 0){
                            stim.pos_Y += stim.rot;
                            stim.pos_X -= stim.rot;
                            window.requestAnimationFrame(stim_Show);
                        }else if (stim.slide_direction === 1){
                            stim.pos_Y += stim.rot;
                            stim.pos_X += stim.rot;
                            window.requestAnimationFrame(stim_Show);
                        }else if (stim.slide_direction === null){
                            stim.pos_Y = 0;
                            stim.pos_X = halfW;
                            stim.slide_direction = null;
                            fsm.showTooSlow();
                        }

                    // if the image is done "sliding", make it drop straight down.
                    }else if (stim.pos_Y > winHeight-50-img.height/3 && stim.pos_Y < winHeight-5-img.height/3 ){
                        stim.pos_Y += stim.rot;
                        window.requestAnimationFrame(stim_Show);

                    // once it settles, move on.
                    }else{
                        stim.pos_Y = 0;
                        stim.pos_X = halfW;
                        stim.slide_direction = null;
                        fsm.showFeedback();
                    }
                }
            },

            ontooSlow:  function(event, from, to)  { // show fixate
                endTime = performance.now();
                win.clearRect(0,0, winWidth, winHeight);
                win.fillText('Too Slow!', halfH, halfW);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                response.totalTime  = endTime / 1000;
                response.totalTime  = response.totalTime.toFixed(4);
                response.hitMiss = "NA";
                response.response = 'NA';
                response.feedback = 'NA';
                response.duration = 'NA';
                NACount++;
                window.setTimeout(function() {
                    win.clearRect(0,0, winWidth, winHeight);
                    fsm.showITI();
                },itiTimeout);
            },


            onfeedback:  function(event, from, to)  { // show feedback
                win.clearRect(0,0, winWidth, winHeight);

                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }

                // scores the response
                if (response.response === 1 || response.response === 2 || response.response === 'NA' ) {

                    if (debug === 1) {
                        console.log('response was ' + response.response);
                        console.log('label is ' + response.label);
                        console.log('in doFeedback');
                        console.log('state is ' + fsm.current);
                        console.log('keydown was: ' + response.response);
                        console.log('rt was: ' + response.duration);
                    }

                    if (response.response === 'NA') {
                        response.hitMiss = "NA";
                        response.feedback = 'NA';
                        if (debug === 1) {
                            console.log('resp was NA');
                            console.log('state is ' + fsm.current);
                        }
                        fsm.showITI();

                    }else if (response.response === response.label) {
                        if (debug === 1) {
                            console.log('hit');
                            console.log('state is ' + fsm.current);
                        }
                        response.feedback = 1;
                        response.hitMiss = "hit";
                        catResp.push(1);
                        blockRespCat.push(1);


                    }else if (response.response !== response.label) {
                        if (debug === 1) {
                            console.log('miss');
                            console.log('state is ' + fsm.current);
                        }
                        response.feedback = 0;
                        response.hitMiss = "miss";
                        catResp.push(0);
                        blockRespCat.push(0);



                    } else {
                        if (debug === 1) {
                            console.log("wrong key was pressed");
                        }
                        response.duration = (endTime - startTime) / 1000;
                        response.duration = response.duration.toFixed([4]);
                        response.response = keyDict[k];
                        response.totalTime = endTime / 1000;
                        response.totalTime = response.totalTime.toFixed([4]);
                        response.feedback = 'NA';
                    }
                }

                // actually displays the feedback.
                if (response.feedback === 1) {
                    if (showFeedback === 1){
                        win.drawImage(corrImg, halfW-((img.width/3)/2)+5 , (winHeight-95), img.width/3, img.height/3);

                        window.setTimeout(function () {
                            win.clearRect(0, winHeight-95, winHeight, winWidth);
                            fsm.showITI();
                        }, feedbackTimeout);
                    }else{
                        test_Resp.push(1);
                        fsm.showITI();
                    }

                }else if (response.feedback === 0) {
                    if (showFeedback === 1) {
                        win.drawImage(incorrImg, halfW-((img.width/3)/2)+5 , (winHeight-95), img.width/3, img.height/3);

                        window.setTimeout(function () {
                            win.clearRect(0, winHeight-95, winHeight, winWidth);
                            fsm.showITI();
                        }, feedbackTimeout);
                    }else{
                        test_Resp.push(0);
                        fsm.showITI();
                    }
                }
            },


            onITI: function(event, from, to) { // show ITI

                win.clearRect(0,0, winWidth, winHeight);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                data.push((response.trial+1) + " " + response.totalTime + " " + curr_sf + " " + curr_ori + " "
                    + response.stimImg + " " + response.label + " " + response.response + " " + response.feedback + " "
                    + response.hitMiss + " " + response.duration + " " + block + " " + response.subj);

                response.response = 'NA';
                window.setTimeout(function(){
                    win.clearRect(0,0, winWidth, winHeight); 
                    if (trialCount === trialsBeforeEnd){
                        fsm.showFinish();
                    }else if (trialCount % trialsBeforeTest === 0){
                        showFeedback = 0;
                        showTestText = 1;
                        test_count = 0;
                        fsm.showBreak();
                    }else if (trialCount % trialBeforeBreak === 0) {
                        fsm.showBreak();

                    }else{
                        fsm.showFixation();
                    }

                },itiTimeout);
            },

            onbreak: function(event, from, to){
                document.addEventListener('keydown', breakOut, false);
                win.clearRect(0,0, winHeight, winWidth);
                if (showTestText === 1){
                    DrawText(testText);
                    status_info = ["trial: " + trialCount, "date:" + new Date().toString()];

                    if (cfg["exp_control"].hasOwnProperty('upload') && cfg["exp_control"].upload == 0) {
                        console.log('Not uploading');
                        console.log(data);
                    }else {
                        ServerHelper.upload_data('partial. block: ' + block + ', trial: ' + trialCount, data);
                        ServerHelper.upload_data('status', status_info);

                    }
                    block++;
                    showTestText = 0;
                }else if (showTestText === 0) {

                    for (x = 0; x < blockRespCat.length; x++) {
                        blockAccCat += blockRespCat[x];
                    }

                    var breakText = '\n\nPlease feel free to take a break.' +
                        '\n\nIn the last block, you got ' + blockAccCat + ' trials correct during this block' +
                        '\n\nPress any key to continue.';

                    DrawText(breakText);
                    if (bns === 1 && trialCount === trialsBeforeP3){
                        DrawText(intervention);
                    }
                    status_info = ["trial: " + trialCount, "trial12: " + trial_count_12, "trial34: " + trial_count_34, "date:" + new Date().toString()];

                    if (cfg["exp_control"].hasOwnProperty('upload') && cfg["exp_control"].upload == 0) {
                        console.log('Not uploading');
                        console.log(data);
                    }else {
                        ServerHelper.upload_data('partial. block: ' + block + ', trial: ' + trialCount, data);
                        ServerHelper.upload_data('status', status_info);
                    }
                    block++;
                    blockRespCat = [];
                    blockAccCat = 0;
                    if (debug === 1) {
                        console.log('state is ' + fsm.current);
                    }
                }
            },

            onend: function(event, from, to){
                win.clearRect(0,0, winWidth, winHeight); 
                if (debug === 1) {
                    console.log(data);
                }
                var currentdateEnd = new Date();
                var dateTimeEnd = 'Experiment Ended: '
                    + currentdateEnd.getHours() + ":"
                    + currentdateEnd.getMinutes() + ":"
                    + currentdateEnd.getSeconds();
                data.push(dateTimeEnd);

                for (x=0; x < test_Resp.length; x++){
                    test_catAcc += test_Resp[x];
                }
                test_catAcc = (test_catAcc / (test_Resp.length)) * 100;
                if (debug === 1) {
                    console.log('Test Acc is: ' + test_catAcc);
                    console.log(test_Resp.length)
                }


                for (x=0; x < catResp.length; x++){
                    total_catAcc += catResp[x];
                }
                total_catAcc = (total_catAcc / (catResp.length)) * 100;
                if (debug === 1) {
                    console.log('Total Acc is: ' + total_catAcc);
                }

                console.log('sending data');
                status_info = ["trial: " + trialCount, "trial12: " + trial_count_12, "trial34: " + trial_count_34, "date:" + new Date().toString()];

                if (cfg["exp_control"].hasOwnProperty('upload') && cfg["exp_control"].upload == 0) {
                    console.log('Not uploading');
                    console.log(data);
                }else {
                    ServerHelper.upload_data('status', status_info);
                    ServerHelper.upload_data('complete. NAs: ' + NACount + ', CatAcc: ' + total_catAcc.toFixed(2) + '%', data);
                }




                window.onbeforeunload = null;

                // decides whether to show a "Green" - You're Good, or "Red" You're Bad end text.

                if (total_catAcc < 52 || NACount > 10) {
                    win.fillStyle = 'red';
                    endText = 'Thank you for participating in this study.\n\n' +
                        'Your Categorization accuracy was: ' + Math.round(total_catAcc) + '%.\n\n' +
                        'We will need to review your results before approving payment.\n\n' +
                        'Thank you for participating.'
                } else {
                    win.fillStyle = 'green';
                    endText = 'Thank you for participating in this study.\n\n' +
                        'Your Categorization accuracy was: ' + Math.round(total_catAcc) + '%.\n\n' +
                        'Great job!'
                }

                DrawText(endText);


                // handles mTurk submission.

                var submitURL = document.URL;
                var params = parse_url(submitURL); // function in server.js
                var mturk_form = document.getElementById("mturk_form");

                if(params.hasOwnProperty('assignmentId') && params['assignmentId']!=''){
                    // Create form to submit the final data to mturk

                    var url = LIVE_MTURK;
                    if (debug === 1) {
                        console.log(url);
                        console.log("setting form");
                    }

                    var formString = "<form action=\"" + url + "\" method=\"POST\"><input type=\"hidden\" name=\"assignmentId\" value=\"" + params['assignmentId'] +
                        "\">\n\nPress Submit to finish this experiment <input type=\"hidden\" name=\"dataLog\" " +
                        "value=\" Total Cat Acc is: " + total_catAcc.toFixed(2) + "%, Last Block Acc is: " + test_catAcc.toFixed(2) + "%, NAs: " + NACount +"\"> <input type=\"submit\" value=\"Submit\"></form>";


                    mturk_form.style.marginLeft = '35%';
                    mturk_form.style.marginTop = '10px';
                    mturk_form.style.paddingTop = '50px';
                    mturk_form.style.paddingBottom = '50px';
                    mturk_form.style.fontSize = "30px";
                    mturk_form.style.color = "yellow";
                    mturk_form.innerHTML = formString;
                }
            }
        }
    });

    //basket.src = 'https://www.reberlab.org/images/basket-brown/basket-brown.png';
    fsm.start();
}