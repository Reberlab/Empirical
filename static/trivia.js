/**
 * Created by paulj on 4/28/2016.
 */


var trivia_state='';

var TriviaDatabase=[];  // list of questions
var QuestionList=[];
var trivia_trial=0;
var current_question=0;
var answer_order=[1,2,3,4];
var answer_ypos=[0,0,0,0];
var current_highlighted=0;
var verbose=true;
var feedback_onset=window.performance.now();
var question_onset=window.performance.now();
var trivia_start=window.performance.now();

var trivia_duration=180;

var trivia_db_requested=false;
var trivia_db_loaded=false;

// layout is externally defined
// cts is externally defined

function parseCSV(str) {
    var r=[];
    var quote=false;
    for(var col=c=0;c<str.length;c++) {
        var cc = str[c], nc = str[c+1];
        r[col]=r[col] || '';
        if(cc=='"' && quote && nc=='"') {r[col]+=cc; ++c; continue;}
        if(cc=='"') { quote=!quote; continue;}
        if(cc==',' && !quote) {++col; continue;}
        r[col]+=cc;
    }
    return(r);
}

function parse_database(db_string) {
    // decrypt?
    lines=db_string.split('\n');
    for(var i=0; i<lines.length; i++) {
        q = parseCSV(lines[i]);
        if (q.length >= 7 && q[2] != '') {
            TriviaDatabase.push(q.slice(2, 7));
        }
        //if (i<10) {
        //    console.log(i + ' '+ q);
        //}
    }
    if (verbose) {
        console.log("Loaded db");
        console.log(TriviaDatabase.length + " questions");
    }
    return true;
}

function load_trivia_db() {
    if(!trivia_db_requested) {
        db_url = ServerHelper.image_url + 'Trivia_db/Trivia_dec2015.csv';
        ServerHelper.xmlhttp.addEventListener('load', db_loaded);
        ServerHelper.xmlhttp.open("GET", db_url, true);
        ServerHelper.xmlhttp.send();
    } else {
        console.log("Repeated db load request");
    }
}

function db_loaded() {
    if (ServerHelper.xmlhttp.readyState == 4) {
        if (ServerHelper.xmlhttp.status == 200) {
            database_string = ServerHelper.xmlhttp.responseText;
            if(parse_database(database_string)) {
                trivia_db_loaded=true;
                for(var i=0;i<TriviaDatabase.length;i++) QuestionList.push(i);
                QuestionList=shuffle(QuestionList);
            }
        } else {
            ServerHelper.error = ServerHelper.xmlhttp.statusText;
        }
    }
}

function trivia_draw () {
    var curr_time=window.performance.now();

    // main draw loop
    layout.clear();

    if(trivia_state=='get_db') {
        // get trivia db (& decrypt)
        load_trivia_db();
        trivia_db_requested=true;
        trivia_state='wait_db';
        console.log("trivia_draw");
    } else if(trivia_state=='wait_db') {
        welcome_message();
        ctx.font = "20px Arial";
        ctx.fillText("Loading db", layout.cue_area / 2.0, layout.height / 2 + 450);
        if(trivia_db_loaded) {
            //console.log("Loaded, ready");
            next_question();
            trivia_state='ready';
        }
    } else if(trivia_state=='ready') {
        // print welcome message, press key to begin
        welcome_message();
    } else if (trivia_state=='question' || trivia_state=='confirm') {
        // display question and options, wait for response -- check for time-out
        draw_question(show_answer=false);
    } else if(trivia_state=='feedback') {
        // check answer, display feedback -- wait feedback time
        draw_question(show_answer=true);
        if((curr_time-feedback_onset)>5000) session_state='iti';
    } else if(trivia_state=='iti') {
        // add time to time counter
        next_question(); // move to next question
        if (trivia_state!='complete') start_question();  // initialize next question state
    } else if(trivia_state=='complete') {
        // today's session is completed
        window.cancelAnimationFrame(requestId);
        window.removeEventListener("keydown",trivia_keypress);
        requestId = window.requestAnimationFrame(return_main);
        return;
    }
    requestId = window.requestAnimationFrame(trivia_draw);
}

function check_answer() {
    if(answer_order[current_highlighted-1]==1) return true;
    return false;
}

function start_question() {
    trivia_state='question';
    question_onset=window.performance.now();
    current_highlighted=0;
}

function start_feedback() {
    feedback_onset=window.performance.now();
    trivia_state='feedback';
}

function next_question() {
    //current_question=Math.floor(Math.random()*TriviaDatabase.length);
    // check for repeats, don't use question 0 (it's the column headers)
    current_question = QuestionList[trivia_trial];
    trivia_trial++;
    //console.log(TriviaDatabase[current_question]);
    //console.log(answer_order);

    current_highlighted = 0;
    answer_order = shuffle(answer_order);

    // check for session is over...
    elap = (window.performance.now() - trivia_start) / 1000.0;
    if (elap > trivia_duration) trivia_state = 'complete';
    else if(verbose) console.log("Elapsed: "+elap);
}        


function trivia_keypress(e) {
    var k = String.fromCharCode(e.keyCode);
    if(trivia_state=='ready') {
        // press any key to continue
        start_question();
    } else if(trivia_state=='question') {
        // get selected answer, session_state='confirm'
        // check if key on answer key list
        for(var i=0;i<cfg['answer_keys'].length;i++) {
            if(cfg['answer_keys'][i]==k) {
                current_highlighted=i+1;
                trivia_state='confirm';
                return;
            }
        }
    } else if(trivia_state=='confirm') {
        // rekey answer or press Enter, session_state='feedback'
        if(e.keyCode==13) { // enter pressed
            start_feedback();
            return;
        }
        for(var i=0;i<cfg['answer_keys'].length;i++) {
            if(cfg['answer_keys'][i]==k) {
                if(current_highlighted==(i+1)) {
                    start_feedback();
                    return;
                } else {
                    trivia_state='question'; // return to question state, pre-confirm
                    current_highlighted=0;
                    return;
                }
            }
        }
    } else if(trivia_state=='feedback') {
        // Enter to jump to next question
        if(e.keyCode==13) { // enter pressed
            trivia_state='iti';
        }
    }
}

function welcome_message() {
    ctx.textAlign = "center";
    ctx.fillStyle = 'black';
    ctx.font = "24px Arial";
    ctx.fillText("Lets do a few minutes of trivia questions", layout.cue_area / 2.0, layout.height / 2 - 150);
    ctx.fillText("Select the answer you think is correct", layout.cue_area / 2.0, layout.height / 2 - 100);
    ctx.fillText("Then press enter to confirm or repeat the key", layout.cue_area / 2.0, layout.height / 2 - 70);
    ctx.fillText("After you answer, you can press Enter to continue", layout.cue_area / 2.0, layout.height / 2 - 40);
    ctx.fillText("Press any key to begin", layout.cue_area / 2.0, layout.height / 2);
}

function wrapped_lines(s,max_len) {
    var lines=[];
    var curr_wid=0;
    var n=0;
    var w=s.split(' ');
    lines[0]=w[0];
    for(i=1;i<w.length;i++) {
        curr_wid=ctx.measureText(lines[n]+' '+w[i]).width;
        if(curr_wid<max_len){
            lines[n]+=(' '+w[i]);
        } else {
            n++;
            lines[n]=w[i];
            //console.log("Breaking line, "+curr_wid+' '+max_len);
        }
        if(n>5) {
            console.log(">5 lines");
            return(lines);
        }
    }
    return(lines);
}

// formatting -- change colors of question, number, answer text?
//   boxes around answers to show click zone?
function draw_question(show_answer) {
    var y=0;
    var linelen=layout.cue_area-(layout.left*2);

    q = TriviaDatabase[current_question];
    ctx.textAlign = "left";
    ctx.fillStyle = cfg['question_color'];
    ctx.font = cfg['question_size'].toString()+"px Arial";
    var line_height=cfg['question_size']*1.25;
    // word wrap
    lines=wrapped_lines(q[0],linelen);
    for(var i=0;i<lines.length;i++) {
        ctx.fillText(lines[i], layout.left, layout.top+i*line_height);
    }
    y=layout.top+lines.length*line_height+cfg['question_spacing'];
    ctx.font = cfg['answer_size'].toString()+"px Arial";
    line_height=cfg['answer_size']*1.25;
    for (var a = 0; a < 4; a++) {
        if(y>layout.height) {
            console.log("Off bottom of screen");
            return;
        }
        // letter/number answer options
        // box around answer
        lines=wrapped_lines((a+1).toString()+". "+q[answer_order[a]],linelen);
        ctx.strokeRect(layout.left-5,y-line_height,linelen+10,lines.length*line_height+cfg['answer_spacing']/2);
        answer_ypos[a]=y+((lines.length-1)*line_height)/2.0;
        if(show_answer) {
            if (current_highlighted == (a + 1)) {
                if(check_answer()==true) ctx.fillStyle = cfg['correct_bkg'];
                else ctx.fillStyle = cfg['incorrect_bkg'];
            }
            else {
                if(check_answer()==false && answer_order[a]==1) ctx.fillStyle = cfg['highlighted_bkg'];
                else ctx.fillStyle = cfg['answer_bkg'];
            }
        } else {
            if (current_highlighted == (a + 1)) ctx.fillStyle = cfg['highlighted_bkg'];
            else ctx.fillStyle = cfg['answer_bkg'];
        }
        ctx.fillRect(layout.left-5,y-line_height,linelen+10,lines.length*line_height+cfg['answer_spacing']/2);
        //if(verbose){
        //    console.log(layout.left-5,y-line_height,linelen+10,lines.length*line_height+cfg['answer_spacing']/2);
        //}
        for(i=0;i<lines.length;i++) {
            if(show_answer) {
                if (current_highlighted == (a + 1)) {
                    if(check_answer()==true) ctx.fillStyle = cfg['correct_color'];
                    else ctx.fillStyle = cfg['incorrect_color'];
                }
                else {
                    if(check_answer()==false && answer_order[a]==1) ctx.fillStyle = cfg['highlighted_color'];
                    else ctx.fillStyle = cfg['answer_color'];
                }
            } else {
                if(current_highlighted==(a+1)) ctx.fillStyle=cfg['highlighted_color'];
                else ctx.fillStyle=cfg['answer_color'];
            }
            ctx.fillText(lines[i], layout.left, y);
            y+=line_height;
        }
        y+=cfg['answer_spacing'];
    }
    if(show_answer) {
        ctx.textAlign = "center";
        ctx.font = cfg['question_size'].toString()+"px Arial";
        if(check_answer()==true) {
            // positive feedback at bottom of page
            ctx.fillStyle = cfg['correct_bkg'];
            ctx.fillText("Correct!", (layout.cue_area/2), layout.height-100);
            ctx.fillText("Press Enter to continue", (layout.cue_area/2), layout.height-70);
        } else {
            // negative feedback at bottom of page
            ctx.fillStyle = cfg['incorrect_bkg'];
            ctx.fillText("Not quite.", (layout.cue_area/2), layout.height-100);
            ctx.fillText("Press Enter to continue", (layout.cue_area/2), layout.height-70);
        }
    }
    if(verbose) verbose=false;
}

function start_trivia() {
    console.log("Starting trivia");
    trivia_state='get_db';

    // formatting variables
    layout.left=50;
    layout.cue_area=600;
    layout.top=100;
    cfg['background_color']='white';
    cfg['question_color']='black';
    cfg['answer_color']='black';
    cfg['answer_bkg']='white';
    cfg['highlighted_color']='white';
    cfg['highlighted_bkg']='blue';
    cfg['correct_color']='white';
    cfg['correct_bkg']='green';
    cfg['incorrect_color']='white';
    cfg['incorrect_bkg']='red';

    // Font sizes
    cfg['question_size']=24;
    cfg['answer_size']=22;
    cfg['question_spacing']=25;
    cfg['answer_spacing']=15;
    cfg['time_size']=24;

    // Response keys
    cfg['answer_keys']=['1', '2', '3', '4'];

    trivia_start=window.performance.now();
    console.log("launching trivia_draw");
    window.addEventListener("keydown",trivia_keypress,false);
    requestId = window.requestAnimationFrame(trivia_draw);
    return;
}