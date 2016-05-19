/*Created by Ben Reuveni on 6/25/2015.*/

/*
    This module preloads images as well as offers a button to start the appropriate experiment.
    It is accomplished by setting "preLoad_done" and/or "readyToStart" to "true" which is then referenced
    in the <exp.html> using a requestAnimationFrame to continuously evaluate.

    The function accepts 2 parameters:
        1) imgList - An array of strings corresponding to image file names to be loaded.
        2) imgDir - a string corresponding to the particular experiment folder that contains the appropriate images.

    Once img_preload is done loading images, it sets preLoad_done to true (line ~ 221)

    If you choose to use the clickToStart() function, when it is finished creating the button, it will set
    readyToStart to true.
*/

// these variables must be outside any functions in order to be global.
var images = [];
var preLoad_done = false;
var cfg = null;
var readyToStart = false;


function img_preload(imgList, imgDir) { // image_list[], image_dir; url to retrieve from is ServerHelper.image_url+image_dir

    var elem = document.getElementById('mainWin');
    // Check the canvas support with the help of browser

    var context = elem.getContext('2d');

    var debug = 0;
    var imgPath = ServerHelper.image_url + imgDir;


    // imgList should be an array of strings corresponding to the image files you'd like to load of the form
    // " "stim_7_0.598649_46.124084.png" " - again, note the " " around the string.

    // This should be an int corresponding to the total number of images to load.
    var totalImages = imgList.length+5;
    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    var halfW = winWidth / 4;
    var halfH = winHeight / 2.2;
    var loadedCount = 0;
    var pleaseWait = "Please wait while images are being loaded.";
    var pleaseWait2 = "If the next screen contains a grey box with ";
    var pleaseWait3 = "an outline, please refresh the page (F5).";
    var img_check = 1;
    var img_checked = 0;
    var articulating_splines = "Articulating Splines";
    var clickToBegin = "Click to begin";

    // the following progress bar functions are described here:
    // http://mag.splashnology.com/article/how-to-create-a-progress-bar-with-html5-canvas/478/

    function roundRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.arc(x + width - radius, y + radius, radius, -Math.PI / 2, Math.PI / 2, false);
        ctx.lineTo(x + radius, y + height);
        ctx.arc(x + radius, y + radius, radius, Math.PI / 2, 3 * Math.PI / 2, false);
        ctx.closePath();
        ctx.fill();
    }

    function progressLayerRect(ctx, x, y, width, height, radius) {
        ctx.save();
        // Define the shadows
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        ctx.shadowBlur = 5;
        ctx.shadowColor = '#666';

        // first grey layer
        ctx.fillStyle = 'rgba(189,189,189,1)';
        roundRect(ctx, x, y, width, height, radius);

        // second layer with gradient
        // remove the shadow
        ctx.shadowColor = 'rgba(0,0,0,0)';
        var lingrad = ctx.createLinearGradient(0, y + height, 0, 0);
        lingrad.addColorStop(0, 'rgba(255,255,255, 0.1)');
        lingrad.addColorStop(0.4, 'rgba(255,255,255, 0.7)');
        lingrad.addColorStop(1, 'rgba(255,255,255,0.4)');
        ctx.fillStyle = lingrad;
        roundRect(ctx, x, y, width, height, radius);

        ctx.restore();
    }

    function progressBarRect(ctx, x, y, width, height, radius, max) {
        // deplacement for chord drawing
        var offset = 0;
        ctx.beginPath();
        if (width < radius) {
            offset = radius - Math.sqrt(Math.pow(radius, 2) - Math.pow((radius - width), 2));
            // Left angle
            var left_angle = Math.acos((radius - width) / radius);
            ctx.moveTo(x + width, y + offset);
            ctx.lineTo(x + width, y + height - offset);
            ctx.arc(x + radius, y + radius, radius, Math.PI - left_angle, Math.PI + left_angle, false);
        }
        else if (width + radius > max) {
            offset = radius - Math.sqrt(Math.pow(radius, 2) - Math.pow((radius - (max - width)), 2));
            // Right angle
            var right_angle = Math.acos((radius - (max - width)) / radius);
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + width, y);
            ctx.arc(x + max - radius, y + radius, radius, -Math.PI / 2, -right_angle, false);
            ctx.lineTo(x + width, y + height - offset);
            ctx.arc(x + max - radius, y + radius, radius, right_angle, Math.PI / 2, false);
            ctx.lineTo(x + radius, y + height);
            ctx.arc(x + radius, y + radius, radius, Math.PI / 2, 3 * Math.PI / 2, false);
        }
        else {
            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + width, y);
            ctx.lineTo(x + width, y + height);
            ctx.lineTo(x + radius, y + height);
            ctx.arc(x + radius, y + radius, radius, Math.PI / 2, 3 * Math.PI / 2, false);
        }
        ctx.closePath();
        ctx.fill();

        // shadow on the right
        if (width < max - 1) {
            ctx.save();
            ctx.shadowOffsetX = 1;
            ctx.shadowBlur = 1;
            ctx.shadowColor = '#666';
            if (width + radius > max)
                offset = offset + 1;
            ctx.fillRect(x + width, y + offset, 1, total_height - offset * 2);
            ctx.restore();
        }
    }

    function progressText(ctx, x, y, width, height, radius, max) {
        ctx.save();
        ctx.fillStyle = 'white';
        var text = Math.floor(width / max * 100) + "%";
        var text_width = ctx.measureText(text).width;
        var text_x = x + width - text_width - radius / 2;
        if (width <= radius + text_width) {
            text_x = x + radius / 2;
        }
        ctx.fillText(text, text_x, y + 22);
        ctx.restore();
    }

    // Define the size and position of indicator
    //var i = 0;
    //var res = 0;
    //var context = null;
    var total_width = 300;
    var total_height = 34;
    var initial_x = halfW;
    var initial_y = halfH;
    var radius = total_height / 2;
    var percentIncrement = (total_width / totalImages); // a modifier to ensure that progress is always maxed at 100%


    function preloadMain() {

        // Gradient of the progress
        var progress_lingrad = context.createLinearGradient(0, initial_y + total_height, 0, 0);
        progress_lingrad.addColorStop(0, '#4DA4F3');
        progress_lingrad.addColorStop(0.4, '#ADD9FF');
        progress_lingrad.addColorStop(1, '#9ED1FF');
        context.fillStyle = progress_lingrad;

        // Text's font for "Please wait" note
        context.font = "24px Verdana";
        context.fillText(pleaseWait, 50, 120);
        context.fillText(pleaseWait2, 50, 170);
	context.fillText(pleaseWait3, 50, 220);

        // Text's font of the progress
        context.font = "16px Verdana";

        // Create the animation
        preload();
    }

    // This function preloads images.
    function preload() {

            var img = images[loadedCount];
            if (typeof(img) === "undefined") {
                img = images[loadedCount] = new Image();
            }
            if (loadedCount * percentIncrement < total_width + 10) {
                img.onload = function () {
                    if (debug === 1) {
                        console.log('imgLoaded is not done');
                    }
                    if (loadedCount + 1 < totalImages) {
                        img.src = this.src;
                    }

                    if (loadedCount * percentIncrement < total_width + 0.1) {
                        draw(loadedCount * percentIncrement);
                    }

                };
                if (loadedCount < totalImages) {
                    var source = imgPath + imgList[loadedCount];
                    source = source.replace(/([^:]\/)\/+/g, "$1");
                    img.src = source;
                    images[loadedCount] = img;
                }
            }
    }


    function draw(count) {
	    loadedCount++;
        // Clear the layer
        context.clearRect(initial_x - 10, initial_y - 5, total_width + 20, total_height + 15);
        progressLayerRect(context, initial_x, initial_y, total_width, total_height, radius);
        progressBarRect(context, initial_x, initial_y, count, total_height, radius, total_width);
        progressText(context, initial_x, initial_y, count, total_height, radius, total_width);

        // stop the animation when it reaches 100%
        // makes the progress bar clickable when it reaches 100%
        if (count+1 >= total_width) {
            if (debug === 1) {
                console.log(percentIncrement);
                console.log('draw is done');
                console.log(images.length);
                console.log(totalImages);
            }


            function check_img_load() {
                //console.log('checking image ' + images[images.length - img_check].src);
                //console.log('image complete ' + images[images.length - img_check].onload);

                //window.setInterval(function () {

                if (img_check < 20 && images[images.length - img_check].complete) {
                    img_check++;
                    img_checked++;
                }

                if (img_checked >= 13) {

                    window.setTimeout(function () {
                        var progress = context.createLinearGradient(0, initial_y + total_height, 0, 0);
                        progress.addColorStop(0, '#4DA4F3');
                        progress.addColorStop(0.4, '#ADD9FF');
                        progress.addColorStop(1, '#9ED1FF');
                        context.fillStyle = progress;
                        context.fillRect(halfW + (total_width / 4) - 5, (initial_y + total_height) - 28, 170, 20);
                    }, 1000);

                    window.setTimeout(function () {
                        context.fillStyle = "yellow";
                        context.fillText(clickToBegin, halfW + (total_width / 3.3), initial_y + total_height - 12);
                    }, 1005);

                    preLoad_done = true;
                } else {
                    window.requestAnimationFrame(check_img_load);
                }
            }
            window.setTimeout(function() {
                context.fillStyle = "yellow";
                context.fillText(articulating_splines, halfW + (total_width / 4), initial_y + total_height - 12);
            },0)

            if (img_check < 20) {
                window.requestAnimationFrame(check_img_load);
            }
        } else {
            if (debug === 1) {
                console.log('loading with ' + count);
            }
            preload(imgList);
            }
        }
    preloadMain();
}



function clickToStart() {
    var canvas3 = document.getElementById('mainWin');
    var context1 = canvas3.getContext('2d');
    var articulating_splines = "Articulating Splines"
    var clickToBegin = "Click to begin";
    var winHeight = mainWin.height;
    var winWidth = mainWin.width;
    var halfW = winWidth / 4;
    var halfH = winHeight / 2.2;
    var debug = 0;
    var total_width = 300;
    var total_height = 34;
    var initial_x = halfW;
    var initial_y = halfH;
    var radius = total_height / 2;

    var elem = document.getElementById('mainWin');
    var context = elem.getContext('2d');



    canvas3.addEventListener('click', click_event, false);
    // new function starts here
    // tracks mouse position.
    function getMousePos(canvas, evt) {
        var rect = canvas.getBoundingClientRect();
        return {
            x: Math.round((evt.clientX - rect.left) / (rect.right - rect.left) * canvas.width),
            y: Math.round((evt.clientY - rect.top) / (rect.bottom - rect.top) * canvas.height)
        };
    }

    // listens for a mouse click. If they clicked the button, invokes the main experiment.
    function click_event(evt) {
        var mousePos = getMousePos(canvas3, evt);
        var message = mousePos.x + ',' + mousePos.y;
        y = canvas3.width/2.0-220;
        x = canvas3.width/2.0;
        if (debug === 1) {
            console.log(message.slice(0, 3));
            console.log(message.slice(4, 8));
        }
        if (halfW <= mousePos.x && mousePos.x <= halfW + total_width && halfH <= mousePos.y && mousePos.y <= halfH + total_height) {
            canvas3.removeEventListener('click', click_event, false);
            if (debug === 1) {
                console.log(images[-1].src);
            }
            readyToStart = true;
        }
    }
}