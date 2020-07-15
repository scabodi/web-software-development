/* Run once document ready. */
$(function() {
    "use strict";

    // Bind an event handler that handles clicking any link inside #continentMenu.
    $("#continentMenu a").on("click", function(event) {

        // Prevent the default behaviour of clicking a link (changing the page).
        event.preventDefault();

        // Take the target url from the link that was clicked.
        var url = $(this).attr("href");

        // Change the title with id continentName to the text in the clicked link.
        $("#continentName").text($(this).text());

        // Replace the contents of #tableContainer with HTML
        // that is dynamically load from the link's target url.
        $("#tableContainer").load(url);
    });
});
