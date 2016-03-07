/*Created by Ben Reuveni on 6/25/2015.*/

function startVisCatDemo(params){

    //if (params !== undefined) {
        //var canvas_space = document.getElementById("canvas_holder");
        //canvas_space.style.float = "";
        //canvas_space.style.margin = "auto";
        //canvas_space.style.margin = "20px";
    //}
    var inst_slide_1 = new Image();
    var inst_slide_2 = new Image();
    var inst_slide_3 = new Image();
    var inst_slide_4 = new Image();
    var inst_slide_5 = new Image();
    var inst_slide_6 = new Image();
    var inst_ready = 0;


    var trialsBeforeEnd = 15;



    //if (params !== undefined) {
        //var trail_image = '';
        //trial_design.innerHTML = trail_image;
    //}
    var win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
    var canvas = document.getElementById('mainWin');
    canvas.style.float = "";
    canvas.style.margin = "auto";

    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    win.font = "30px Arial";
    //win.textAlign = 'center';
    win.fillStyle = "#fFfFfF";
    var halfW = winWidth / 2;
    var halfH = winHeight / 2;
    var debug = 0;
    var empiricalMainPage = "http://reberlab.org/";


// These variables will end up coming from a .cfg file - These lines need to be modified to refer to the JSON that contains them

    var fixateTimeout = cfg["timings"].fixateTimeout;
    var stimTimeout = cfg["timings"].stimTimeout;
    var dualTaskTimeout = cfg["timings"].dualTaskTimeout;
    var maskTimeout = cfg["timings"].maskTimeout;
    var feedbackTimeout = cfg["timings"].feedbackTimeout;
    var itiTimeout = cfg["timings"].itiTimeout;
    var dualTaskPromptTimeout = cfg["timings"].dualTaskPromptTimeout;



    var trialBeforeBreak = 100;
    var trialsBeforeTest = 100;


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

        var introText = "This is the main experiment, it will look exactly like the demo you just took except that now the sine-waves will vary " +
           "from trial to trial, and have definite correct and incorrect answers." +
           "\n\nThe experiment consists of " + trialsBeforeEnd  + " trials in total, and you will receive breaks every " + trialBeforeBreak +" trials. The experiment will take approximately an hour" +
           "\n\nPlease note that if you fail to respond on enough trials, we will not be able to use your data and you will not be paid. " +
           "If you try your best and engage with the experiment, there should be no issues.";

        var introText2 = '\n\n\n Please note, it is up to you to figure out what the criteria for "A" or "B" are.' +
            '\n\nIn some cases, you may not be sure what category the sine-wave belongs to. In these cases, it is OK to guess rather than to not respond.';


        var introText3 = 'As a reminder:' +
            '\n\nThe Square image is a mask, and is only meant to cover up the circular sine-wave. It contains no information about the correct category and can be ignored.' +
            '\n\nYou may only respond after the numbers have been shown and while the circular sine-wave grating is on the screen' +
            '\n\nIf you respond with a button other than "d" or "k" it will count as a mistake.\n\nPress any key to begin';

        var testText = '\n\n\n\nThe following block is the final test. You will no longer be performing the Numerical Decision task, and you will no longer be given feedback for your choices.' +
            '\n\nPlease press any key to begin.';

    }

    var breakText = '';
    var endText = '\n\n\n\nThank you for completing this brief demo.\n\n Click the box below to begin the real experiment.';


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
                clearTimeout(stim_Show);
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

    function doBegin(){
        win.clearRect(0, 0, winHeight, winWidth);
        document.removeEventListener('keydown', doBegin, false);
        introSlide++;

        // this bit will allow us to display multiple instructions. Just add new "else if" before the "else"
        if (introSlide === 1){
            document.addEventListener('keydown', doBegin, false);

            win.drawImage(inst_slide_2, 0, 0, canvas.width, canvas.height);
            //DrawText(introText2);
        }else if (introSlide === 2){

            document.addEventListener('keydown', doBegin, false);
            //DrawText(introText3);
                win.drawImage(inst_slide_3, 0, 0, canvas.width, canvas.height);

        }else if (introSlide === 3){

            document.addEventListener('keydown', doBegin, false);
            //DrawText(introText3);
                win.drawImage(inst_slide_4, 0, 0, canvas.width, canvas.height);

        }else if (introSlide === 4){

            document.addEventListener('keydown', doBegin, false);
            //DrawText(introText3);
                win.drawImage(inst_slide_5, 0, 0, canvas.width, canvas.height);

        }else if (introSlide === 5){

            document.addEventListener('keydown', doBegin, false);
            //DrawText(introText3);
                win.drawImage(inst_slide_6, 0, 0, canvas.width, canvas.height);

        }
        //else if (introSlide === 2){} // if we need another intro text screen.

        else{
            canvas.height = 600;
            canvas.width = 600;

            //canvas_space.innerHTML = '<canvas id="mainWin" width="600" height="600"></canvas>';
            //win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
            win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
            canvas = document.getElementById('mainWin');
            winHeight = mainWin.height;
            winWidth = mainWin.width;
            win.font = "30px Arial";
            win.textAlign = 'center';
            win.fillStyle = "#fFfFfF";
            halfW = winWidth / 2;
            halfH = winHeight / 2;



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

    function toMainExp(evt) {
        var mousePoss = getMousePos1(canvas, evt);
        var message = mousePoss.x + ',' + mousePoss.y;
        if (debug === 1) {
            console.log(message.slice(0, 3));
            console.log(message.slice(4, 8));
        }

        if (200 <= mousePoss.x && mousePoss.x <= 400 && 400 <= mousePoss.y && mousePoss.y <= 475) {
            canvas.removeEventListener('click', toMainExp, false);
            startVisCatExp(params);
        }
    }



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

                //canvas = document.getElementById("mainWin");

                //var reqs = document.getElementById('reqs');
                //reqs.style.fontSize = '16px';
                //reqs.style.font-size = '16px';

                canvas.height = 700;
                canvas.width = canvas.height*1.7;

                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                //alert('The following dialog box will contain your receipt token.\n\nPlease press Ctrl+C to copy it');
                //alert('987654321');
                //DrawText(introText);
                win.drawImage(inst_slide_1, 0, 0, canvas.width, canvas.height);

                document.addEventListener('keydown', doBegin, false);
            },

            onfixation:  function(event, from, to)  { // show fixate
                //reqs.style.font-size = 16px;
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
                    win.font = (fLeft[trialCount]+20) + "px Arial";
                    //win.font = '100px Arial';
                    win.fillText(nLeft[trialCount], (halfH - (img.height / 2) - 35), (halfW - (img.width / 2))+150);
                    win.font = (fRight[trialCount]+20) + "px Arial";
                    //win.font = '60px Arial';
                    win.fillText(nRight[trialCount], (halfH - (img.height / 2) + 325), (halfW - (img.width / 2))+150);
                    win.font = "30px Arial";


                    whiteoutMask = window.setTimeout(function(){
                        win.fillRect((halfH - (img.width / 2) - 80 ), (halfW - (img.height / 2))+75, 75, 90);
                        win.fillRect((halfH - (img.width / 2) + 300), (halfW - (img.height / 2))+75, 75, 90);

                    },dualTaskTimeout+200);


                    dualTaskInterval = window.setTimeout(function () {
                        win.clearRect((halfH - (img.width / 2) - 90 ), (halfW - (img.height / 2))+72, 88, 98);
                        win.clearRect((halfH - (img.width / 2) + 290), (halfW - (img.height / 2))+72, 88, 98);
                        }, dualTaskTimeout+400);

                    stim_Show = window.setTimeout(function () {
                        win.font = "40px Arial";
                        win.fillText("d    or    k", (halfH - (img.height / 2) + 139), (halfW - (img.width / 2))-50);
                        win.font = "30px Arial";
                        win.drawImage(img, (halfH - (img.height / 2)), (halfW - (img.width / 2)), img.height, img.width);
                        startTime = performance.now();
                        document.addEventListener('keydown', doFeedback, false);

                        }, 600);
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

                if (params["demo"] !== 1) {
                    win.clearRect(0, 0, winHeight, winWidth);
                    canvas.addEventListener('click', toMainExp, false);
                    DrawText(endText);
                    win.beginPath();
                    win.rect(180, 400, 250, 75);
                    win.stroke();
                    win.fillText("Start Experiment.", 305, 445);
                }else{
                    win.clearRect(0, 0, winHeight, winWidth);
                    endText = '\n\n\n\nThank you for completing this brief demo.';
                    DrawText(endText);
                }
            }

        }
    });
        var imgDir = cfg["exp_control"].imgPath;


     inst_slide_1.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide1.PNG';
     inst_slide_2.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide2.PNG';
     inst_slide_3.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide3.PNG';
     inst_slide_4.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide4.PNG';
     inst_slide_5.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide5.PNG';
     inst_slide_6.src = 'https://reberlab.org/images/Num_Stroop_Instructions/Slide6.PNG';

    inst_slide_1.onload=function(){inst_ready++};
    inst_slide_2.onload=function(){inst_ready++};
    inst_slide_3.onload=function(){inst_ready++};
    inst_slide_4.onload=function(){inst_ready++};
    inst_slide_5.onload=function(){inst_ready++};
    inst_slide_6.onload=function(){inst_ready++};

    window.requestAnimationFrame(inst_is_ready);

    function inst_is_ready(){
        if (inst_ready == 6) {
            fsm.start();
        } else {
            var wait = '\n\n\n\n\n\n\nPlease wait while we optimize settings...';
            win.textAlign = 'center';
            DrawText(wait);
            window.requestAnimationFrame(inst_is_ready);

        }
    }


}