/**
 * Created by drlemur on 8/24/2015.
 */

// Cue, lane and animation functions for SISL, SeVi

// Helper function for x,y,z, distance
function distance3(p1,p2){
    return Math.sqrt(((p1[0]-p2[0])*(p1[0]-p2[0]))+((p1[1]-p2[1])*(p1[1]-p2[1]))+((p1[2]-p2[2])*(p1[2]-p2[2])))
}

// DATA STRUCTURES: lane, cue, anim, speed_adj

// lane holds all the lane information on which the cues move -- start, end and target locations, cue display, etc.
var lane = function(start,target,delta,color,size,pad_color,pad_size) {
    this.start=start;
    this.target=target;
    this.total_distance=distance3(start,target);
    this.delta=delta;
    this.end=[0,0,0];
    for(var i=0;i<3;i++) this.end[i]=start[i]+delta[i];
    this.cue_color=color;
    this.cue_size=size;
    this.target_size=pad_size;
    this.target_color=pad_color;
    this.key='';
    this.add_letter=false;
    this.draw_pad=function() {
        ctx.beginPath();
        ctx.fillStyle= this.target_color;
        ctx.arc(this.target[0], this.target[1], this.target_size, 0, Math.PI*2, true);
        ctx.closePath();
        ctx.stroke();

        if(this.add_letter==true){
            ctx.font = this.letter_size.toString()+"px Arial";
            ctx.fillStyle= this.letter_color;
            ctx.textAlign="center";
            ctx.fillText(this.target_letter,this.letter_x,this.letter_y);
        }
    };
    this.add_letter=function(x,y,color,size,letter) {
        this.add_letter=true;
        this.letter_x=x;
        this.letter_y=y;
        this.letter_color=color;
        this.letter_size=size;
        this.target_letter=letter;
    };
    this.distance=function(pos){
        // determine distance from pos to target as a fraction of the travel distance
        d=distance3(pos,[this.target[0],this.target[1],this.target[2]]);
        return d/this.total_distance;
    }
}

// cue holds all the information about the moving cues on the screen, many of this variables are set from the lane it is in
// update with cue based velocity instead of percent of way to finish
var cue = function() {
    this.active=false;
    this.pos=[0,0,0]; // (x,y,z)
    this.radius=25; // these defaults (size, color) shouldn't get used -- launch sets these values from lane
    this.color='blue';
    this.cue_lane=0;
    this.scored=false;
    this.score_miss=true;
    this.trial_num=0;
    this.last_move=0;
    this.velocity=[0,0,0]; // (dx, dy, dz)
    this.draw=function() {
        ctx.beginPath();
        ctx.arc(this.pos[0], this.pos[1], this.radius*(this.pos[2]/100.0), 0, Math.PI*2, true);
        ctx.closePath();
        ctx.fillStyle = this.color;
        ctx.fill();
    }
    this.move=function() {  //new_pos) {
        var curr = window.performance.now();
        var elap = curr - this.last_move; // time since last update in ms
        this.pos[0] += this.velocity[0] * elap;
        this.pos[1] += this.velocity[1] * elap;
        this.pos[2] += this.velocity[2] * elap;

        // check for off-screen
        if (this.pos[0] > lane_set[this.cue_lane].end[0] ||
                this.pos[1] > lane_set[this.cue_lane].end[1] ||
                this.pos[2] > lane_set[this.cue_lane].end[2]) {
            this.active = false;
            if(this.score_miss==true && this.scored==false) {
                this.scored = true;
                score_response('miss', -1, this.cue_lane, [this.trial_num]);
            }
        }

        // update last move, current target distance
        this.last_move = curr;
        this.distance=lane_set[this.cue_lane].distance(this.pos); // fractional distance from current position to target pad
    }

    this.launch=function(lane_num,launch_time,trial,travel_time) {
        this.active=true;
        this.scored=false;
        this.last_move=launch_time;
        this.cue_lane=lane_num;
        this.trial_num=trial;
        this.radius=lane_set[this.cue_lane].cue_size;
        if (typeof shuffle_list == 'undefined' || shuffle_list[current_cue]==0){
            this.color=lane_set[this.cue_lane].cue_color;
        }
        else if (shuffle_list[current_cue]==1){
         this.color='red';
        }
        this.pos[0]=lane_set[this.cue_lane].start[0];
        this.pos[1]=lane_set[this.cue_lane].start[1];
        this.pos[2]=lane_set[this.cue_lane].start[2];
        // velocity in pixels per ms
        this.velocity[0]=(lane_set[this.cue_lane].delta[0])/travel_time;
        this.velocity[1]=(lane_set[this.cue_lane].delta[1])/travel_time;
        this.velocity[2]=(lane_set[this.cue_lane].delta[2])/travel_time;
    }
    this.adjust_speed=function(speed_fraction) {
        //var ov=this.velocity[1];
        this.velocity[0]*=speed_fraction;
        this.velocity[1]*=speed_fraction;
        this.velocity[2]*=speed_fraction;
        //console.log(ov,this.velocity[1],speed_fraction);
    }
}

// depends on cue_set being a global variable for the current list of active cues
function launch_cue(lane_num,launch_time,trial,scoreMiss){
    for (var i=0;i<cue_set.length;i++){ // re-use inactive cue elements
        if(cue_set[i].active==false){
            cue_set[i].launch(lane_num,launch_time,trial,current_speed*1000.0);
            cue_set[i].score_miss=scoreMiss;
            return;
        }
    }
    var new_cue = new cue();
    new_cue.launch(lane_num,launch_time,trial,current_speed*1000.0);
    new_cue.score_miss=scoreMiss;
    cue_set.push(new_cue);
}

// other animated objects on the canvas that aren't moving cues or pads
// On screen elements to support:
// # trials, num_correct, num_incorrect, seq_correct, foil_correct
// # percent_correct, percent_correct_seq, percent_correct_foil, sspa
// # score, streak, longest_streak, current_item
// -- progress bars

function time_report(s){ // turn seconds into a Xm Xs string; if >1 hr, return Xh Xm string
    if(s>3600) {
        var hours=Math.floor(s/3600);
        return hours.toFixed(0)+"h "+Math.floor((s-(hours*3600))/60).toFixed(0)+"m";
    }
    return Math.floor((s/60)).toFixed(0)+"m "+(s%60).toFixed(0)+"s"
}

var anim = function(anim_type,frames,args) {
    this.anim_type = anim_type;
    this.anim_args = args;
    this.frame_count = 0;
    this.max_frames = frames;
    this.active = true;
    this.dynamic = false;
    this.text_size=24;
    this.draw = function () { // return function is false if this item is done, true if will continue to be animated
        if(this.active==false) return false;
        if(this.max_frames>=0 && this.frame_count>this.max_frames) {
            this.active=false;
            return false;
        }
        if(this.anim_type == 'flash-pos' || this.anim_type == 'flash-neg') { // pos/neg feedback flashes
            px=lane_set[this.anim_args[0]].target[0];
            py=lane_set[this.anim_args[0]].target[1];
            sz=lane_set[this.anim_args[0]].cue_size;
            ctx.beginPath();
            ctx.arc(px, py, sz, 0, Math.PI*2, true);
            ctx.closePath();
            ctx.fillStyle=this.anim_args[1];
            ctx.fill();
            this.frame_count++;
        }
        else if(this.anim_type=='text'){ // these elements all depend on the stats object existing and having the right information
            var text='';
            // implement other on screen elements
            // 'speed','speed_info','seq_correct','foil_correct','seq_pc','foil_pc','streak','sspa'
            if(this.anim_args[2]=='speed') text="Speed "+current_speed.toFixed(2);
            else if(this.anim_args[2]=='speed_info') text=Speeder.speed_correct_counter.toString()+" correct of "+Speeder.speed_trials_counter.toString();
            else if(this.anim_args[2]=='seq_correct') text="Seq correct "+stats.seq_correct.toString();
            else if(this.anim_args[2]=='seq_trials') text="Seq trials "+stats.seq_trials.toString();
            else if(this.anim_args[2]=='foil_correct') text="Foil correct "+stats.foil_correct.toString();
            else if(this.anim_args[2]=='foil_trials') text="Foil trials "+stats.foil_trials.toString();
            else if(this.anim_args[2]=='seq_pc') text="Seq % "+stats.seq_pc.toFixed(2);
            else if(this.anim_args[2]=='foil_pc') text="Foil % "+stats.foil_pc.toFixed(2);
            else if(this.anim_args[2]=='streak') text="Streak "+stats.streak.toString();
            else if(this.anim_args[2]=='longest_streak') text="Longest streak "+stats.longest_streak.toString();
            else if(this.anim_args[2]=='sspa') text="SSPA "+stats.sspa.toFixed(2);
            else if(this.anim_args[2]=='fps') text="FPS "+stats.fps.toFixed(1);
            else if(this.anim_args[2]=='score') text="Score "+stats.score.toFixed(0);
            else if(this.anim_args[2]=='time_today') text="Training time "+time_report(stats.time_today);  //time_today max_length_today length length_pc
            else if(this.anim_args[2]=='max_length_today') text="Longest "+stats.max_length_today.toFixed(0);
            else if(this.anim_args[2]=='length') text="Current length "+stats.current_length.toFixed(0);
            else if(this.anim_args[2]=='length_pc') {
                if(isNaN(stats.pc)) text="Correct at this length ---%";
                else text="Correct at this length "+stats.pc.toFixed(0)+'%';
            }
            else if(this.anim_args[2]=='trials_today') text="Trials today "+stats.trials_today.toFixed(0);
            else text='Unknown '+this.anim_args[2]; // add other elements here
            ctx.font = this.text_size.toString()+"px Arial";
            ctx.fillStyle='black';
            ctx.textAlign='left';
            ctx.fillText(text,this.anim_args[0],this.anim_args[1]);
        } else if(this.anim_type=='float-text') {
            ctx.textAlign='center';
            ctx.fillStyle=this.anim_args[3];
            ctx.font=this.anim_args[4];
            ctx.fillText(this.anim_args[0],this.anim_args[1],this.anim_args[2]);
            this.frame_count++;
        }
        return this.dynamic; // if a dynamic item is being animated, return true; this used to wait to terminate block
    }
    this.add_text = function(x,info_type,text_size) {
        var y=100;
        for(var i=0;i<anim_list.length;i++){
            if(anim_list[i].anim_type=='text') {
                y=y+this.text_size;
            }
        }
        this.max_frames = -1;
        this.anim_args=[x,y,info_type];
        this.text_size=text_size;
    }
    this.float_text = function(text,x,y,color,font,frames) { // could allow context variables like color, size, etc
        this.anim_args='float-text';
        this.frame_count=0;
        this.max_frames=frames;
        this.active=true;
        this.dynamic=true;
        this.anim_args=[text,x,y,color,font];
    }
}
