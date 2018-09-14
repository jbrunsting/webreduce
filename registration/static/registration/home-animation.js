var canvas = $("#home-animation");
var width = screen.width;
var height = screen.height;
canvas.width(width);
canvas.height(height);
var ctx = canvas[0].getContext("2d");
ctx.canvas.width = width;
ctx.canvas.height = height;

shapes = [];

function sind(a) {
    return Math.sin(a / 180 * Math.PI);
}

function cosd(a) {
    return Math.cos(a / 180 * Math.PI);
}

var CIRCLE = 1;
var SQUARE = 2;
var TRIANGLE = 3;
var GRAVITY_OFFSET = 50;

ctx.strokeStyle = "#FFFFFF"

function Shape(type, size, x, y, vx, vy, vrot, delay) {
    var rot = 0;
    var initx = x;
    var inity = y;
    var initvx = vx;
    var initvy = vy;
    var initvrot = vrot;
    shape = {};

    shape.handlePointGravity = function(px, py, gravity) {
        if (delay > 0) {
            return;
        }

        var dx = px - x;
        var dy = py - y;
        var distance = Math.sqrt(dx*dx, dy*dy) + GRAVITY_OFFSET;
        var force = Math.pow(gravity / distance, 2);
        var fx = (dx / distance) * force;
        var fy = (dy / distance) * force;
        vx += fx;
        vy += fy;
    }

    // Treats line as if it extends forever
    shape.handleLineGravity = function(lx1, ly1, angle, gravity) {
        if (delay > 0) {
            return;
        }

        var l1dx = x - lx1;
        var l1dy = y - ly1;
        var angleFromL1 = Math.atan(l1dy / l1dx);
        var angleBetween = angle - angleFromL1;
        var distanceFromOrigin = Math.sqrt(l1dx * l1dx + l1dy * l1dy);
        var distance = Math.sin(angleBetween) * distanceFromOrigin;
        var scaledDistance = distance / 15;
        var force = gravity * scaledDistance / Math.pow(Math.abs(scaledDistance) + 1, 2);
        var forceAngle = angle + (90 * Math.PI / 180);
        var fx = Math.cos(forceAngle) * force;
        var fy = Math.sin(forceAngle) * force;
        vx += fx;
        vy += fy;
    }

    shape.step = function() {
        if (delay > 0) {
            delay -= 1;
            return;
        }

        if (vy > 200) {
            vy = 200;
        } else if (vy < -200) {
            vy = -200;
        }

        x += vx / 60;
        y += vy / 60;
        rot += vrot / 60;

        if (x < -size || x > width + size || y < -size || y > height + size) {
            x = initx;
            y = inity;
            vx = initvx;
            vy = initvy;
            vrot = initvrot;
        }

        if (rot < 0) {
            rot += 360;
        } else if (rot > 360) {
            rot -= 360;
        }
    }

    shape.draw = function() {
        if (delay > 0) {
            return;
        }

        ctx.translate(x + size / 2, y + size / 2);
        ctx.rotate(rot * Math.PI / 180);
        ctx.beginPath();
        switch (type) {
            case CIRCLE:
                ctx.arc(-size / 4, -size / 4, size / 2, 0, 2 * Math.PI); break;
            case SQUARE:
                ctx.rect(-size / 2, -size / 2, size, size);
                break;
            case TRIANGLE:
                var hyp = size;
                var height = cosd(30) * hyp;
                ctx.beginPath();
                ctx.moveTo(0, -height / 2);
                ctx.lineTo(0 + sind(30) * hyp, height / 2);
                ctx.lineTo(0 - sind(30) * hyp, height / 2);
                ctx.lineTo(0, -height / 2);
        }
        ctx.rotate(-rot * Math.PI / 180);
        ctx.translate(-x - size / 2, -y - size / 2); 
        ctx.stroke();
    }

    return shape;
}

function rand(min, max) {
    return Math.random() * (max - min) + min;
}

var minsize = 8;
var maxsize = 12;
var miny = 350;
var maxy = 550;
var minvx = 150;
var maxvx = 200;
var minvy = -15;
var maxvy = 15;
var minrotv = -20;
var maxrotv = 20;
var mindelay = 0;
var maxdelay = 60 * width / minvx;
var types = [CIRCLE, SQUARE, TRIANGLE];
var count = 200;

for (var i = 0; i < count; ++i) {
    var size = rand(minsize, maxsize);
    var x = -size;
    var y = rand(miny, maxy);
    var vx = rand(minvx, maxvx);
    var vy = rand(minvy, maxvy);
    var rotv = rand(minrotv, maxrotv);
    var delay = rand(mindelay, maxdelay);
    delay += Math.pow(rand(0, 15), 2);
    var type = types[Math.floor(rand(0, types.length))]

    shape = Shape(type, size, x, y, vx, vy, rotv, delay);
    if (Math.random() < 0.2) {
        shape.addToFeed = true;
    }
    shapes.push(shape);
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, width, height);
    shapes.forEach(function(shape) {
        shape.handleLineGravity(0, 450, 0, 15);
        if (shape.addToFeed) {
            shape.handlePointGravity(width / 3, 0, 100);
        }
        shape.step();
        shape.draw();
    });
}

if (width >= 1024) {
    animate();
}
