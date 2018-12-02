
window.onload = function() {
    handles = [];
    form_handles = document.getElementsByName('selected_handles')[0];
    console.log(form_handles);

    // Assign event listener to table rows
    handleRows = document.getElementsByClassName('handles')[0].getElementsByTagName('tr');
    for (var i = 0; i < handleRows.length; i++) {
        handleRows[i].addEventListener('click', function(e) {
            this.style.background = 'pink';
            // Get handle
            handle = this.firstElementChild.textContent;
            handles.push(handle);
            form_handles.value = JSON.stringify(handles);
        });
    }
   
}