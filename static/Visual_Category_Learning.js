/*Created by Ben Reuveni on 6/25/2015.*/

function startVisCatExp(params){
    var canvas_space = document.getElementById("canvas_holder");
    canvas_space.style.float = "";
    canvas_space.style.margin = "auto";
    //canvas_space.style.margin = "20px";

    var trail_image = '';
    trial_design.innerHTML = trail_image;
    var win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
    var canvas = document.getElementById('mainWin');
    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    win.font = "30px Arial";
    win.textAlign = 'center';
    win.fillStyle = "#fFfFfF";
    var halfW = winWidth / 2;
    var halfH = winHeight / 2;
    var debug = 1;
    var empiricalMainPage = "http://reberlab.org/";


// These variables will end up coming from a .cfg file - These lines need to be modified to refer to the JSON that contains them

    var fixateTimeout = cfg["timings"].fixateTimeout;
    var stimTimeout = cfg["timings"].stimTimeout;
    var dualTaskTimeout = cfg["timings"].dualTaskTimeout;
    var maskTimeout = cfg["timings"].maskTimeout;
    var feedbackTimeout = cfg["timings"].feedbackTimeout;
    var itiTimeout = cfg["timings"].itiTimeout;
    var dualTaskPromptTimeout = cfg["timings"].dualTaskPromptTimeout;

    var feedback = cfg["timings"].feedback;
    //var trialBeforeBreak = cfg["exp_control"].trialBeforeBreak;
    //var trialsBeforeTest = cfg["exp_control"].trialBeforeTest;
    //var trialsBeforeEnd = cfg["exp_control"].trialBeforeEnd;

    var trialBeforeBreak = 11;
    var trialsBeforeTest = 5;
    var trialsBeforeEnd = 2;

    var stimLabels = cfg["exp_control"].stimLabels;
    var stimSF = cfg["stim_params"].SF;
    var stimOri = cfg["stim_params"].Ori;



    var corrImg = images[cfg["exp_control"].stimList.length-3];
    var incorrImg = images[cfg["exp_control"].stimList.length-2];
    var mask = images[cfg["exp_control"].stimList.length-1];


    var dualTask = cfg["dual_task"].dualTask;
    var dualTaskInitial = dualTask;
    var nRight = cfg["dual_task"].nRight;
    var nLeft = cfg["dual_task"].nLeft;
    var fRight = cfg["dual_task"].fRight;
    var fLeft = cfg["dual_task"].fLeft;
    var dualTaskPrompt = cfg["dual_task"].dualTask_prompt;
    var dualTaskNow = 0;


    var masterClock = 0;
    var startTime = 0;
    var endTime = 0;
    var trialCount = 0;
    var introSlide = 0; // controls which intro text to show (iterates each time in "doBegin").
    var block = 1;
    var NACount = 0;
    var catResp = []; //will hold all 1/0 based on cat answers in order to calculate accuracy at the end
    var dtResp = []; //will hold all 1/0 based on dual task answers in order to calculate accuracy at the end
    var catAcc = 0; // the final number
    var dtAcc = 0; // the final number
    var blockRespDT = [];
    var blockAccDT = 0;
    var blockRespCat = [];
    var blockAccCat = 0;


    var data = [];
    var currentdateStart = new Date();
    var dateTimeStart = 'Experiment Began: '
        + currentdateStart.getDate() + "/"
        + (currentdateStart.getMonth()+1)  + "/"
        + currentdateStart.getFullYear() + " @ "
        + currentdateStart.getHours() + ":"
        + currentdateStart.getMinutes() + ":"
        + currentdateStart.getSeconds();

    data.push('SessionId is: ' + params["sessionToken"]);
    data.push('WorkerID is: ' + params["workerId"]);
    data.push('AssignmentID is: ' + params["assignmentId"]);
    data.push('Fixation Timeout: ' + fixateTimeout);
    data.push('Stimulus Timeout: ' + stimTimeout);
    data.push('Dual Task Number Timeout: ' + dualTaskTimeout);
    data.push('Response Timeout: ' + stimTimeout);
    data.push('Dual Task Response Timeout: ' + dualTaskPromptTimeout);
    data.push('Feedback Timeout: ' + feedbackTimeout);
    data.push('ITI: ' + itiTimeout);

    data.push('\n\nTrials Before Break: ' + trialBeforeBreak);
    data.push('Trials Before Test: ' + trialsBeforeTest);
    data.push('Trials Before End: ' + trialsBeforeEnd);
    data.push('Total Trials: ' + cfg["exp_control"].stimList.length);

    data.push(dateTimeStart+'\n\n');

    data.push("trial total_time sf ori stimImg label response feedback hit/miss RT dualTaskPrompt dualTaskLabel " +
        "dualTaskResponse dualTaskFeedback dualTaskHitMiss dualTaskDuration block subj_session_token");

    ServerHelper.upload_data('initial', data);

    var showFeedback = 1; // controls whether to display feedback or not.
    var showTestText = 0; // controls whether to display test text or break text in onBreak.
    var response = {
        "trial": 0,
        "totalTime": 0,
        "stimImg": null,
        "label": null,
        "response": null,
        "feedback": null,
        "hitMiss": null,
        "duration": 0,

        "dualTasknLeft": null,
        "dualTasknRight": null,
        "dualTaskfLeft": null,
        "dualTaskfRight": null,
        "dualTaskPrompt": null,
        "dualTaskLabel": null,
        "dualTaskResponse": null,
        "dualTaskFeedback": null,
        "dualTaskHitMiss": null,
        "dualTaskDuration": null,
        "subj": params["workerId"]
    };

    var keyDict = {
        'd': 1,
        'D': 1,
        'k': 2,
        'K': 2,
        32: 32,
        'NA': 'NA'
    };

    var dualTaskDict = {
        1: 'Value?',
        2: 'Size?'
    };

    if (stimTimeout > 1000){
        var s = 's'
    }

    if (dualTask === 0){
        var introText = 'In this experiment, you will be shown a series of circular sinewave gratings.\n\nThese images vary on 2 dimensions: bar thickness and bar orientation. ' +
            'These sinewaves belong to either category A or category B.' +
            '\n\nCategorize each image by pressing "d" for A, or "k" for B.' +
            '\n\nPlease note that you have ' + stimTimeout / 1000 + ' second' + s + ' to make your decision.' +
            '\n\nPress any key to advance.';

        var introText2 = 'Please also note the following:' +
            '\n\nThe Square image is a mask, and is only meant to cover up the circular sinewave. It contains no information about the correct category and can be ignored.' +
            '\n\nYou may only respond while the circular Sinewave grating is on the screen' +
            '\n\nIf you respond with a button other than "d" or "k" it will count as a mistake.\n\nPress any key to begin';

        var testText = '\n\n\n\nThe following block is the final test. You will no longer be given feedback for your choices.' +
            '\n\nPlease press any button to begin.';

    }else if (dualTask === 1){

        var introText = "This experiment consists of " + trialsBeforeEnd  + " trials in total, and you will receive breaks every " + trialBeforeBreak +" trials. " +
           "\n\nPlease note that if you fail to respond on enough trials, we will not be able to use your data and you will not be paid. " +
           "\n\nIf you try your best and engage with the experiment, there should be no issues." +
            "\n\nPress any key to continue.";

        var introText2 = '\n\n\n Please remember, it is up to you to figure out what the criteria for "A" or "B" are.' +
            '\n\nIn some cases, you may not be sure what category the "circle" belongs to. In these cases, it is OK to guess rather than to not respond.' +
            '\n\nPress any key to begin.';


        var introText3 = 'As a reminder:' +
            '\n\nThe Square image is a mask, and is only meant to cover up the circular sine-wave. It contains no information about the correct category and can be ignored.' +
            '\n\nYou may only respond after the numbers have been shown and while the circular sine-wave grating is on the screen' +
            '\n\nIf you respond with a button other than "d" or "k" it will count as a mistake.\n\nPress any key to begin';

        var testText = '\n\n\n\nThe following block is the final test. You will no longer be performing the Numerical Decision task, and you will no longer be given feedback for your choices.' +
            '\n\nPlease press any key to begin.';

    }

    var breakText = '';
    var endText = '\n\n\n\nThank you for participating in this study.\n\nPlease inform the researcher that you have finished.';


    /* Functions */

    function doFeedback(event){
        endTime = performance.now();
        document.removeEventListener('keydown', doFeedback, false);

        var k = String.fromCharCode(event.keyCode);
        if (k === 'd' || k === 'D' || k === 'k' || k === 'K'){
            if (dualTaskNow === 0) {
                clearTimeout(picTimeout);
                clearTimeout(dualTaskInterval);
                clearTimeout(stim_Show);
            }else if (dualTaskNow === 1) {
                clearTimeout(dualTaskPromptInterval);
            }

            if (dualTaskNow === 0) {
                response.label = stimLabels[trialCount];
                response.duration = (endTime - startTime) / 1000;
                response.duration = response.duration.toFixed([4]);
                response.response = keyDict[k];
                response.totalTime = endTime / 1000;
                response.totalTime = response.totalTime.toFixed([4]);
            }
            else if (dualTaskNow === 1){

                response.label = stimLabels[trialCount];
                response.dualTaskDuration = (endTime - startTime) / 1000;
                response.dualTaskDuration = response.dualTaskDuration.toFixed([4]);
                response.dualTaskResponse = keyDict[k];

                response.dualTasknLeft = nLeft[trialCount];
                response.dualTasknRight = nRight[trialCount];
                response.dualTaskfLeft = fLeft[trialCount];
                response.dualTaskfRight = fRight[trialCount];
                response.dualTaskPrompt = dualTaskPrompt[trialCount];

                if (response.dualTaskPrompt === 1){
                    if (response.dualTasknLeft > response.dualTasknRight){
                        response.dualTaskLabel = 1;
                    }else if (response.dualTasknLeft < response.dualTasknRight){
                        response.dualTaskLabel = 2;
                    }
                }else if (response.dualTaskPrompt === 2){
                    if (response.dualTaskfLeft > response.dualTaskfRight){
                        response.dualTaskLabel = 1;
                    }else if (response.dualTaskfLeft < response.dualTaskfRight){
                        response.dualTaskLabel = 2;
                    }
                }
            }

            if (debug === 1) {
                console.log(k);
                console.log('in doFeedback');
                console.log('keydown was: ' + response.response);
                console.log('rt was: ' + response.duration);
            }
            if (dualTaskNow === 0) {
                if (response.response === response.label) {
                    response.feedback = 1;
                    response.hitMiss = "hit";
                    catResp.push(1);
                    blockRespCat.push(1);
                    fsm.showMask();
                } else if (response.response !== response.label) {
                    response.feedback = 0;
                    response.hitMiss = "miss";
                    catResp.push(0);
                    blockRespCat.push(0);
                    fsm.showMask();
                } else if (response.response === 'NA') {
                    response.hitMiss = "NA";
                    response.feedback = 'NA';
                    fsm.showITI();
                }
            }else if (dualTaskNow === 1){
                if (response.dualTaskResponse === response.dualTaskLabel) {
                    response.dualTaskFeedback = 1;
                    response.dualTaskHitMiss = "hit";
                    dtResp.push(1);
                    blockRespDT.push(1);
                    fsm.showFeedback(response.dualTaskFeedback);
                } else if (response.dualTaskResponse !== response.dualTaskLabel) {
                    response.dualTaskFeedback = 0;
                    response.dualTaskHitMiss = "miss";
                    blockRespDT.push(0);
                    dtResp.push(0);
                    fsm.showFeedback(response.dualTaskFeedback);
                } else if (response.dualTaskResponse === 'NA') {
                    response.dualTaskHitMiss = "NA";
                    response.dualTaskFeedback = 'NA';
                    fsm.showITI();
                }
            }
        }else{
            if (debug === 1) {
                console.log("wrong key was pressed");
            }
            if (dualTaskNow === 0) {
                if (debug === 1) {
                    console.log("saving normal variables");
                }
                response.duration = (endTime - startTime) / 1000;
                response.duration = response.duration.toFixed([4]);
                response.response = keyDict[k];
                response.totalTime = endTime / 1000;
                response.totalTime = response.totalTime.toFixed([4]);
                response.feedback = 'NA';
            }else if (dualTaskNow === 1) {
                if (debug === 1) {
                    console.log("saving dualTask variables.");
                }
                response.dualTaskDuration = (endTime - startTime) / 1000;
                response.dualTaskDuration = response.dualTaskDuration.toFixed([4]);
                response.dualTaskResponse = keyDict[k];
                response.totalTime = endTime / 1000;
                response.totalTime = response.totalTime.toFixed([4]);
                response.dualTaskFeedback = 'NA';
            }
        }
    }

    // this function moves us on from our "breaks".
    function breakOut() {
        document.removeEventListener('keydown', breakOut, false);
        win.clearRect(0, 0, winHeight, winWidth);
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
        win.clearRect(0, 0, winHeight, winWidth);
        var maxWidth = winWidth;
        var lineHeight = 35; // defines the spacing between lines.
        var x = halfW; // (canvas.width - maxWidth) / 2;
        if (dualTaskNow === 0) {
            var y = halfH * 0.2; // the multiplier here decides how far from the top of the canvas text will start. Smaller === higher up.
        }else if (dualTaskNow === 1){
            var y = halfH;
        }
        wrapText(win, text, x, y, maxWidth, lineHeight);
    }

    function doBegin() {
        win.clearRect(0, 0, winHeight, winWidth);
        document.removeEventListener('keydown', doBegin, false);
        introSlide++;

        // this bit will allow us to display multiple instructions. Just add new "else if" before the "else"
        if (introSlide === 1) {
            document.addEventListener('keydown', doBegin, false);
            DrawText(introText2);
        }

        //else if (introSlide === 2){} // if we need another intro text screen.

        else {
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

    //// spacebar: 32, pageup: 33, pagedown: 34, end: 35, home: 36
    //var scroll_keys = {32: 1};
    //
    //function preventDefault(e) {
    //  e = e || window.event;
    //  if (e.preventDefault)
    //      e.preventDefault();
    //  e.returnValue = false;
    //}
    //
    //function preventDefaultForScrollKeys(e) {
    //    if (scroll_keys[e.keyCode]) {
    //        preventDefault(e);
    //        return false;
    //    }
    //}
    //
    //function disableScroll() {
    //  if (window.addEventListener) // older FF
    //      window.addEventListener('DOMMouseScroll', preventDefault, false);
    //  window.onwheel = preventDefault; // modern standard
    //  window.onmousewheel = document.onmousewheel = preventDefault; // older browsers, IE
    //  window.ontouchmove  = preventDefault; // mobile
    //  document.onkeydown  = preventDefaultForScrollKeys;
    //}
    //
    //function enableScroll() {
    //    if (window.removeEventListener)
    //        window.removeEventListener('DOMMouseScroll', preventDefault, false);
    //    window.onmousewheel = document.onmousewheel = null;
    //    window.onwheel = null;
    //    window.ontouchmove = null;
    //    document.onkeydown = null;
    //}
    //
    //disableScroll();

    /* FSM */

    var fsm = StateMachine.create({ // Version 2 self-contained.
        //initial: 'wait',
        events: [
            { name: "start",         from: 'none',                                                 to: 'instructions'},
            { name: 'showFixation',  from: ['break', 'ITI', 'none', 'instructions'],               to: 'fixation' },
            { name: 'showStim',      from: 'fixation',                                             to: 'stim'    },
            { name: 'showMask',      from: 'stim',                                                 to: 'mask'    },
            { name: 'showFeedback',  from: ['stim', 'mask', 'dualTask'],                           to: 'feedback' },
            { name: 'showTooSlow',   from: ['stim', 'dualTask'],                                   to: 'tooSlow' },
            { name: 'showDualTask',  from: ['feedback', 'tooSlow'],                                to: 'dualTask' },
            { name: 'showITI',       from: ['feedback', 'tooSlow'],                                to: 'ITI'  },
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
                DrawText(introText);
                document.addEventListener('keydown', doBegin, false);
            },

            onfixation:  function(event, from, to)  { // show fixate
                startTime = null;
                endTime = null;
                if (masterClock === 0){
                    masterClock = performance.now();
                }
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                    console.log("NA Count is: " + NACount);
                }
                win.font = "50px Arial";
                win.fillText('+', halfH, halfW);
                win.font = "30px Arial";
                response.trial = trialCount;

                window.setTimeout(function(){
                    win.clearRect(0, 0, winHeight, winWidth);
                    fsm.showStim();
                },fixateTimeout);
            },

            onstim:  function(event, from, to)      { // show image, wait for key or timeout
                img = images[trialCount]; // Iterates the image based on trialCount

                response.stimImg = cfg["exp_control"].stimOrder[trialCount];

                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                    console.log('trail number: ' +trialCount);
                }
                //win.drawImage(img, (halfH - (img.height / 4)), (halfW - (img.width / 4)), img.height/2, img.width/2);
                if (dualTask === 1) {

                        win.font = (fLeft[trialCount] + 20) + "px Arial";
                        //win.font = '100px Arial';
                        win.fillText(nLeft[trialCount], (halfH - (img.height / 2) - 35), (halfW - (img.width / 2)) + 150);
                        win.font = (fRight[trialCount] + 20) + "px Arial";
                        //win.font = '60px Arial';
                        win.fillText(nRight[trialCount], (halfH - (img.height / 2) + 325), (halfW - (img.width / 2)) + 150);
                        win.font = "30px Arial";


                        whiteoutMask = window.setTimeout(function () {
                            win.fillRect((halfH - (img.width / 2) - 80 ), (halfW - (img.height / 2)) + 75, 75, 90);
                            win.fillRect((halfH - (img.width / 2) + 300), (halfW - (img.height / 2)) + 75, 75, 90);

                        }, dualTaskTimeout + 200);


                        dualTaskInterval = window.setTimeout(function () {
                            win.clearRect((halfH - (img.width / 2) - 90 ), (halfW - (img.height / 2)) + 72, 88, 98);
                            win.clearRect((halfH - (img.width / 2) + 290), (halfW - (img.height / 2)) + 72, 88, 98);
                        }, dualTaskTimeout + 400);

                        stim_Show = window.setTimeout(function () {
                            win.font = "40px Arial";
                            win.fillText("d    or    k", (halfH - (img.height / 2) + 139), (halfW - (img.width / 2)) - 50);
                            win.font = "30px Arial";
                            win.drawImage(img, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height, img.width);
                            startTime = performance.now();
                            document.addEventListener('keydown', doFeedback, false);
                        }, 600);

                }else {
                    stim_Show = window.setTimeout(function () {
                        win.font = "40px Arial";
                        win.fillText("d    or    k", (halfH - (img.height / 2) + 139), (halfW - (img.width / 2)) - 50);
                        win.font = "30px Arial";
                        win.drawImage(img, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height, img.width);
                        startTime = performance.now();
                        document.addEventListener('keydown', doFeedback, false);
                    }, 0);
                }

                picTimeout = window.setTimeout(function(){
                    win.clearRect(0, 0, winHeight, winWidth);
                    document.removeEventListener('keydown', doFeedback, false);
                    fsm.showTooSlow();
                },stimTimeout);
            },

            ontooSlow:  function(event, from, to)  { // show fixate
                endTime = performance.now();
                win.fillText('Too Slow!', halfH, halfW);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                response.totalTime  = endTime / 1000;
                response.totalTime  = response.totalTime.toFixed([4]);
                response.response = 'NA';
                response.feedback = 'NA';
                response.duration = 'NA';
                NACount++;
                window.setTimeout(function(){
                win.clearRect(0, 0, winHeight, winWidth);
                    if (dualTaskNow === 0){
                        fsm.showDualTask();
                    }else if (dualTaskNow === 1) {
                        fsm.showITI();
                    }
                },itiTimeout);
            },

            onmask: function(event, from, to){
                win.clearRect(0, 0, winHeight, winWidth);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                win.drawImage(mask, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height , img.width);
                window.setTimeout(function(){
                    win.clearRect(0, 0, winHeight, winWidth);
                    fsm.showFeedback(response.feedback);
                },maskTimeout);
            },


            onfeedback:  function(event, from, to, corr)  { // show feedback
                win.clearRect(0, 0, winHeight, winWidth);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                if (corr === 1) {

                    if (showFeedback === 1){
                        win.drawImage(corrImg, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height, img.width);

                        window.setTimeout(function () {
                            win.clearRect(0, 0, winHeight, winWidth);
                            if (dualTaskNow === 0) {
                                fsm.showDualTask();
                            }else if (dualTaskNow === 1){
                                fsm.showITI();
                            }
                        }, feedbackTimeout);
                    }else{
                        fsm.showITI();
                    }

                }else if (corr === 0) {

                    if (showFeedback === 1) {

                        win.drawImage(incorrImg, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height, img.width);

                        window.setTimeout(function () {
                            win.clearRect(0, 0, winHeight, winWidth);
                            if (dualTaskNow === 0) {
                                fsm.showDualTask();
                            }else if (dualTaskNow === 1){
                                fsm.showITI();
                            }
                        }, feedbackTimeout);
                    }else{
                        fsm.showITI();
                    }
                }
            },

            ondualTask: function(event, from, to) { //do Dual Task
                win.clearRect(0, 0, winHeight, winWidth);
                dualTaskNow = 1;
                startTime = null;
                endTime = null;
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                    console.log('Prompt is: ' +dualTaskPrompt[trialCount]);
                }

                startTime = performance.now();
                DrawText(dualTaskDict[dualTaskPrompt[trialCount]]);
                document.addEventListener('keydown', doFeedback, false);

                dualTaskPromptInterval = window.setTimeout(function(){
                    win.clearRect(0, 0, winHeight, winWidth);
                    document.removeEventListener('keydown', doFeedback, false);
                    fsm.showTooSlow();
                },dualTaskPromptTimeout);
            },

            onITI: function(event, from, to) { // show ITI
                dualTaskNow = 0;
                win.clearRect(0, 0, winHeight, winWidth);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                data.push((response.trial+1) + " " + response.totalTime + " " + stimSF[trialCount] + " " + stimOri[trialCount] + " "
                    + response.stimImg + " " + response.label + " " + response.response + " " + response.feedback + " "
                    + response.hitMiss + " " + response.duration + " " + response.dualTaskPrompt + " " + response.dualTaskLabel
                    + " " + response.dualTaskResponse + " " + response.dualTaskFeedback + " " + response.dualTaskHitMiss
                    + " " + response.dualTaskDuration + " " + block + " " + response.subj);

                trialCount++;
                window.setTimeout(function(){
                    win.clearRect(0, 0, winHeight, winWidth);
                    if (trialCount === trialsBeforeEnd){
                        fsm.showFinish();
                    }
                    else if (trialCount % trialBeforeBreak === 0){
                        fsm.showBreak();
                    }else if (trialCount % trialsBeforeTest === 0){
                        dualTask = 0;
                        showFeedback = 0;
                        showTestText = 1;
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
                    ServerHelper.upload_data('partial. block: '+ block ,data);
                    block++;

                    showTestText = 0;
                }else if (showTestText === 0) {

                    for (x = 0; x < blockRespDT.length; x++) {
                        blockAccDT += blockRespDT[x];
                    }

                    for (x = 0; x < blockRespCat.length; x++) {
                        blockAccCat += blockRespCat[x];
                    }

                    var breakText = '\n\nPlease feel free to take a break.' +
                        '\n\nIn the last block, you got ' + blockAccDT + ' trials correct on the numerical decision task' +
                        ' and ' + blockAccCat + ' trials correct on the categorization task' +
                        '\n\nPress any key to continue.';
                    
                    
                    DrawText(breakText);
                    ServerHelper.upload_data('partial. block: ' + block, data);
                    block++;
                    blockRespDT = [];
                    blockAccDT = 0;
                    blockRespCat = [];
                    blockAccCat = 0;
                    if (debug === 1) {
                        console.log('state is ' + fsm.current);
                    }
                }
            },

            onend: function(event, from, to){
                win.clearRect(0, 0, winHeight, winWidth);
                if (debug === 1) {
                    console.log(data);
                }
                var currentdateEnd = new Date();
                var dateTimeEnd = 'Experiment Ended: '
                    + currentdateEnd.getHours() + ":"
                    + currentdateEnd.getMinutes() + ":"
                    + currentdateEnd.getSeconds();
                data.push(dateTimeEnd);

                for (x=0; x < catResp.length; x++){
                    catAcc += catResp[x];
                }
                catAcc = (catAcc / (catResp.length)) * 100;
                if (debug === 1) {
                    console.log('Total Acc is: ' + catAcc);
                }
                for (x=0; x < dtResp.length; x++){
                    dtAcc += dtResp[x];
                }
                dtAcc = (dtAcc / (dtResp.length)) * 100;

                ServerHelper.upload_data('complete. NAs: ' + NACount + ', CatAcc: ' + catAcc + '%' + ', DTAcc: '+ dtAcc + '%', data);

                if (dualTaskInitial === 0) {
                    if (catAcc < 52 || dtAcc < 52 || NACount > 10) {
                        win.fillStyle = 'red';
                        endText = 'Thank you for participating in this study.\n\n' +
                            'Your Categorization accuracy was: ' + Math.round(catAcc) + '%.\n\n' +
                            'We will need to review your results before approving payment.\n\n' +
                            'Thank you for participating.'
                    } else {
                        win.fillStyle = 'green';
                        endText = 'Thank you for participating in this study.\n\n' +
                            'Your Categorization accuracy was: ' + Math.round(catAcc) + '%.\n\n' +
                            'Great job!'
                    }
                }else if (dualTaskInitial === 1){
                    if (catAcc < 60 || dtAcc < 70 || NACount > 10) {
                        win.fillStyle = 'red';
                        endText = 'Thank you for participating in this study.\n\n' +
                            'Your Categorization accuracy was: ' + Math.round(catAcc) + '%.\n\n' +
                            'Your Dual Task accuracy was: ' + Math.round(dtAcc) + '%.\n\n' +
                            'We will need to review your results before approving payment.\n\n' +
                            'Thank you for participating.'
                    } else {
                        win.fillStyle = 'green';
                        endText = 'Thank you for participating in this study.\n\n' +
                            'Your Categorization accuracy was: ' + Math.round(catAcc) + '%.\n\n' +
                            'Your Dual Task accuracy was: ' + Math.round(dtAcc) + '%.\n\n' +
                            'Great job!'
                    }
                }

                DrawText(endText);

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
                    //var dataSummary = "Cat Acc is: " + catAcc + "%, DT Acc is: " + dtAcc + "%, NAs: " + NACount;

                    var formString = "<form action=\"" + url + "\" method=\"POST\"><input type=\"hidden\" name=\"assignmentId\" value=\"" + params['assignmentId'] +
                        "\">\n\nPress Submit to finish this experiment <input type=\"hidden\" name=\"dataLog\" " +
                        "value=\" Cat Acc is: " + catAcc + "%, DT Acc is: " + dtAcc + "%, NAs: " + NACount +"\"> <input type=\"submit\" value=\"Submit\"></form>";

                    //var formString = "<form action=\"" + url + "\" method=\"post\"><input type=\"hidden\" name=\"assignmentId\" value=\"" + params['assignmentId'] +
                    //    "\">\n\nPress Submit to finish this experiment <input type=\"hidden\" name=\"dataLog\" " +
                    //    "value=\" Cat Acc is: " + catAcc + "%, DT Acc is: " + dtAcc + "%, NAs: " + NACount +"\">;
                    mturk_form.style.fontSize = "30px";
                    mturk_form.style.color = "yellow";
                    mturk_form.innerHTML = formString;
                }

            }
        }
    });

    fsm.start();
}