$(document).ready(function() {

  $("#myform").bind("submit", function(event){
    event.preventDefault();

    var date = $("#date").val();
    console.log("Form sent with date = "+date);

     $("#currencies").find("tr").remove();

    $.getJSON("https://acos.cs.hut.fi/wsd-currency/"+date+"?callback=?",
      function(data) {
        console.log(typeof(data));

        $.each(data, function(k, v) {
            console.log(k+" : "+ v);
            $("#currencies").append("<tr><td>"+k+"</td><td>"+v+"</td></tr>");
        });
    });

  });
});
