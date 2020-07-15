$(document).ready(function() {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    'use strict';
    $(window).on('message', function(evt) {
      var data = evt.originalEvent.data;
      var gameiframe = document.getElementById('gameiframe');
      var id = '{{ session.id}}';
      console.log(data);
      if (data.messageType == "SAVE") {
        $.ajax(
          {
            type:"POST",
            url: "/updategame/",
            data : {
              sessionid : id,
              content : JSON.stringify(data)
            },
            headers: {'X-CSRFToken': csrftoken},
            success: function( data )
            {
              alert("Game saved!");
            }
        })
      }
      else if (data.messageType == "LOAD_REQUEST") {
        $.ajax(
          {
            url: "/updategame/",
            data : {
              sessionid : id,
              content : JSON.stringify(data)
            },
            headers: {'X-CSRFToken': csrftoken},
            success: function( data )
            {
              var msg = {
                messageType: "LOAD",
                gameState: JSON.parse(data)
              };
              gameiframe.contentWindow.postMessage(msg, "*");
              alert("Gamestate loaded from the database!");
            }
        })
      }
      else if (data.messageType == "SCORE") {
        $.ajax(
          {
            type:"POST",
            url: "/updategame/",
            data:{
              sessionid : id,
              content : JSON.stringify(data)
            },
            headers: {'X-CSRFToken': csrftoken},
            success: function( data )
            {
              console.log("Score submitted");
            }
        })
      }
      else if (data.messageType == "SETTING") {
        gameiframe.style.width = data.options.width;
        gameiframe.style.height = data.options.height;
      }
      else {
        var msg =  {
          messageType: "ERROR",
          info: "Reading messageType failed!"
        };
        gameiframe.contentWindow.postMessage(msg, "*");
      }
    });
  });