/**
 * Created by Ben on 11/16/2015.
 */


function startFallingStimsExp(params){

    var read_before_accepting = document.getElementById("read_before_accepting");
    read_before_accepting.innerHTML="";


    var debug = 1;

// this creates the 3 canvases we will use in the exp.

    var current_window_height = window.innerHeight;
    var current_window_width = window.innerWidth;



    var canvas_space = document.getElementById("canvas_holder");
    canvas_space.innerHTML = ( '<canvas id="mainWin" width="600" height="600" style = " position: fixed; margin: 0px 0px 0px 35%; z-index: 1; border: 1px solid black"></canvas> ' +
        '<canvas id="basketWin" width="600" height="100" style="position: fixed; margin: 500px 0px 0px 35%;  z-index: 2; border: 1px solid black"></canvas>' +
        '<canvas id="leverWin" width="600" height="100" style="position: fixed; margin: 380px 0px 0px 35%; z-index: 3"></canvas>');

    var lever_win = document.getElementById('leverWin').getContext("2d"); // creates a window reference.
    var basket_win = document.getElementById('basketWin').getContext("2d"); // creates a window reference.

    var inst_page = document.getElementById("canvas_holder");

    var canvas_space = document.getElementById("canvas_holder");
    canvas_space.style.float = "";
    canvas_space.style.margin = "auto";

    var win = document.getElementById('mainWin').getContext("2d"); // creates a window reference.
    var canvas = document.getElementById('mainWin');
    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    var halfW = winWidth / 2;
    var halfH = winHeight / 2;
    var empiricalMainPage = "http://www.reberlab.org/";
    var corrImg = images[cfg["exp_control"].stimList.length-4];
    var incorrImg = images[cfg["exp_control"].stimList.length-3];
    var basket = images[cfg["exp_control"].stimList.length-1];
    var inst_page_1 = images[cfg["exp_control"].stimList.length-6];
    var inst_page_2 = images[cfg["exp_control"].stimList.length-5];


    win.font = "30px Arial";
    win.textAlign = 'center';
    win.fillStyle = "#fFfFfF";

// These variables will end up coming from a .cfg file - These lines need to be modified to refer to the JSON that contains them
    var desired_OST = cfg["timings"].stimTimeout; // in seconds.
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


// (un)comment this block for debugging

    var trialBeforeBreak = 10;
    var trialsBeforeTest = 40;
    var trialsBeforeEnd = 5;
    //var desired_OST = 1.5;

// -------------------------------

    // this bit takes a desired on screen time (OST) and translates it into rate of change for the stim.
    var img_size = images[0].height; // Iterates the image based on trialCount
    var stim_rot = (((winHeight - 190 - (img_size/3)) / desired_OST) / 60).toFixed(2);
    stim_rot = Number(stim_rot);


// magic numbers for keeping track of stuff.
    var masterClock = 0;
    var startTime = 0;
    var endTime = 0;
    var trialCount = 0;
    var introSlide = 0; // controls which intro text to show (iterates each time in "doBegin").
    var block = 1;
    var NACount = 0;
    var catResp = []; //will hold all 1/0 based on cat answers in order to calculate accuracy at the end
    var catAcc = 0; // the final number
    var blockRespCat = [];
    var blockAccCat = 0;
    var showFeedback = 1; // controls whether to display feedback or not.
    var showTestText = 0; // controls whether to display test text or break text in onBreak.
    var lever_has_changed = 0;


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

    data.push('SessionId is: ' + params["sessionToken"]);
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
                    console.log('in doLever');
                    console.log('state is ' + fsm.current);

                    stim.slide_direction = 0;

                } else if (k === 'k' || k === 'K') {
                    lever_win.clearRect(0, 0, 600, 100);
                    lever_win.beginPath();
                    lever_win.moveTo(256, 0);
                    lever_win.lineTo(356, 100);
                    lever_win.lineWidth = 2;
                    lever_win.stroke();
                    console.log('in doLever');
                    console.log('state is ' + fsm.current);

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
        }

        //else if (introSlide === 2){} // if we need another intro text screen.

        else {

            canvas.style.marginLeft = "35%";
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

                canvas.style.marginTop = "0px";
                canvas.style.marginLeft = "24%";
                canvas.height = 600;
                canvas.width = canvas.height*1.7;
                basket_win.canvas.style.border = "none";

                win.drawImage(inst_page_1, 0 , 0, canvas.width, canvas.height);
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

                response.trial = trialCount;

                window.setTimeout(function(){
                    win.clearRect(0,0, winWidth, winHeight);
                    fsm.showStim();
                },itiTimeout);
            },

            onstim:  function(event, from, to)      { // show image, wait for key or timeout
                img = images[trialCount]; // Iterates the image based on trialCount
                response.stimImg = cfg["exp_control"].stimOrder[trialCount];

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
                    console.log('trail number: ' +trialCount);
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
                console.log('total time till Too Slow was: ' + (endTime - startTime) );
                win.clearRect(0,0, winWidth, winHeight);
                win.fillText('Too Slow!', halfH, halfW);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                response.totalTime  = endTime / 1000;
                response.totalTime  = response.totalTime.toFixed(4);
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

                    response.label = stimLabels[trialCount];

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
                        console.log('resp was NA');
                        console.log('state is ' + fsm.current);
                        fsm.showITI();

                    }else if (response.response === response.label) {
                        console.log('hit');
                        response.feedback = 1;
                        response.hitMiss = "hit";
                        catResp.push(1);
                        blockRespCat.push(1);
                        console.log('state is ' + fsm.current);

                    }else if (response.response !== response.label) {
                        console.log('miss');
                        response.feedback = 0;
                        response.hitMiss = "miss";
                        catResp.push(0);
                        blockRespCat.push(0);
                        console.log('state is ' + fsm.current);


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
                        fsm.showITI();
                    }
                }
            },


            onITI: function(event, from, to) { // show ITI

                win.clearRect(0,0, winWidth, winHeight);
                if (debug === 1) {
                    console.log('state is ' + fsm.current);
                }
                data.push((response.trial+1) + " " + response.totalTime + " " + stimSF[trialCount] + " " + stimOri[trialCount] + " "
                    + response.stimImg + " " + response.label + " " + response.response + " " + response.feedback + " "
                    + response.hitMiss + " " + response.duration + " " + block + " " + response.subj);

                response.response = 'NA';
                trialCount++;
                window.setTimeout(function(){
                    win.clearRect(0,0, winWidth, winHeight); 
                    if (trialCount === trialsBeforeEnd){
                        fsm.showFinish();
                    }
                    else if (trialCount % trialBeforeBreak === 0){
                        fsm.showBreak();

                    }else if (trialCount % trialsBeforeTest === 0){
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

                    for (x = 0; x < blockRespCat.length; x++) {
                        blockAccCat += blockRespCat[x];
                    }

                    var breakText = '\n\nPlease feel free to take a break.' +
                        '\n\nIn the last block, you got ' + blockAccCat + ' trials correct on the categorization task' +
                        '\n\nPress any key to continue.';

                    DrawText(breakText);
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
                lever_win.clearRect(0, 0, 600, 100);
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



                // decides whether to show a "Green" - You're Good, or "Red" You're Bad end text.

                    win.fillStyle = 'green';
                    endText = 'This is the end of the Demo.\n\n' +
                        "If you'd like to participate please keep in mind that the total experiment takes approximately 1 hour.\n\n" +
                        "Also, if you have already participated in a similar version, please do Not accept this HIT as we will not" +
                        "be able to use your data again."

                DrawText(endText);
            }
        }
    });

    //basket.src = 'https://www.reberlab.org/images/basket-brown/basket-brown.png';
    fsm.start();
}