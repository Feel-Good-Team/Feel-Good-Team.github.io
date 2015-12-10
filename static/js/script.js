//NOTE: None of this code is needed -- I used it to create my dictionary lists and to test if the inputs were being
//read in correctly from the form.

//When the submit button is clicked, this function calls 'getCheckedBoxes' to create dictionaries for each category
//NOTE: For example, checkBoxesFood could theoretically be passed to the backend.
//If the user selected 'pizza' and 'dessert', checBoxesFood would look like {"food", ["pizza", "dessert"]}
function submitForms() {
    //need to remove these
	var checkedBoxesFood = getCheckedBoxes("food");
	printCheckedList(checkedBoxesFood, "food");
	var checkedBoxesMusic = getCheckedBoxes("music");
	printCheckedList(checkedBoxesMusic, "music");
	var checkedBoxesPets = getCheckedBoxes("pets");
	printCheckedList(checkedBoxesPets, "pets");
	var checkedBoxesGIFs = getCheckedBoxes("gifs");
	printCheckedList(checkedBoxesGIFs, "gifs");
}


//Create dictionaries for each category
function getCheckedBoxes(chkboxName) {
  var checkboxes = document.getElementsByName(chkboxName);
  var checkboxesChecked = {};			//This is the dictionary
  checkboxesChecked[chkboxName] = [];	//This is the values list (like ["pizza", "dessert"] in the example above)

  //Loop through all checkedboxes for this category and push them into the values list
  for (var i=0; i<checkboxes.length; i++) {
     if (checkboxes[i].checked) {
        checkboxesChecked[chkboxName].push(checkboxes[i].value);
     }
  }
  return checkboxesChecked;
}

//Print out all values selected for each category (this function is used to double check if the dictionary was created correctly).
function printCheckedList(checkedBoxesList, chkboxName) {
	for (var i in checkedBoxesList) {
		alert("This is all the selections for " + chkboxName);
		alert("Key: " + i);
	    alert("Values: " + checkedBoxesList[i]);
	}
}




