// Exercise 2.3 Javascript file  //
// Read the instructions.html //

//some helpful debug code

$("#javascript_start").html("[OK] Started executing the javascript file");
$("#javascript_end").html("[WAITING]...this far we haven't reached the end... Maybe you should check out <a href='https://developer.mozilla.org/fi/docs/Tools'>Firefox DevTools</a>?");

// ADD YOUR CODE BETWEEN THESE LINES //

$("a[href$='.pdf']").addClass("pdf");
$("a[href$='.zip'], a[href$='.xyz']").addClass("download");

// ADD YOUR CODE BETWEEN THESE LINES //

//some helpful debug code

$("#javascript_end").html("[OK] The end of your javascript file was reached. (meaning there were no huge errors) Hopefully your code works too! ");
