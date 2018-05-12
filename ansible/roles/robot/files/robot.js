#!/usr/bin/env nodejs

const request = require('request');
const mqtt = require('mqtt');
const http = require('http');
const fs = require('fs');

const robot = module.exports = {
  messaging: mqtt.connect('mqtt://192.168.0.10'),
  starting: setTimeout(function() {
    robot.messaging.publish('raspberry/status', 'START');
    http.createServer(robot.handler).listen(8888);
  }, 3E3),
  handler: function(request, response) {
    robot.messaging.publish('raspberry/status', ' GET');
    response.writeHead(200, {
      'Content-Type': 'text/html',
    });
    response.end(`<!doctype html>
<html lang="en">
  <head>
    <meta name="charset" value="utf-8">

    <title> Raspberry Robots </title>

    <script type="text/javascript">

    </script>
    <style type="text/css">

    </style>
  </head>
  <body>

  </body>
</html>`);

  },
};