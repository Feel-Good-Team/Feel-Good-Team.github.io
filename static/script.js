/* script.js */

/* When the madlib form is submitted, run this function */
$("#madlibForm").submit(function() {
    
    /* Our beginning madlib story (is empty) */
    var madlibStory = ""

    /* Start Validations */

    /* Get text from "name" input field. */
    var nameValue = $("#madlibForm input[name='name']").val();
    
    /* If the value in the text input field is empty */
    if(nameValue === "") {

        /* pop up an alert screen saying the form is invalid */
        alert("Form is invalid");

        /* Don't load a new page after clicking submit */
        return false;

    }

    /* If the value in the text input field is not empty, set that
        as the madlib story */
    else {
        madlibStory = nameValue;
    }

    /* ADD MORE VALIDATIONS HERE AND ADD TO THE STORY */



    /* END VALIDATIONS */

    /* If all validations pass, add the story to the page */
    $("#madlibStory").html(madlibStory);
    
    /* Don't load a new page after clicking submit */
    return false;
});




