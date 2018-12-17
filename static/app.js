
window.onload = function() {
    handles = [];
    inputHandles = document.getElementsByName('selected_handles')[0];
    selectedContactsList = document.getElementById('selectedContactsList');

    // Assign event listener to table rows
    handleRows = document.getElementsByClassName('handles')[0].getElementsByTagName('tr');
    for (var i = 0; i < handleRows.length; i++) {
        handleRows[i].addEventListener('click', function(e) {
            // Get row
            var row = this.children;

            // Set styling based on previous styling
            if (this.classList.contains('selected')) {
                // If already styled as "selected", remove styling 
                this.classList.remove('selected');
                // Remove text from selected contacts list
                for (var i in selectedContactsList.children) {
                    var item = selectedContactsList.children[i];
                    if (item.textContent == row[1].textContent) {
                        selectedContactsList.removeChild(item);
                    }
                }
            } else {
                // Otherwise, style as "selected"
                this.classList.add('selected');
                // Add text to selected contacts list
                var contact = document.createElement('li');
                contact.textContent = row[1].textContent;
                selectedContactsList.appendChild(contact);
            }

            // Get handle
            handle = row[0].textContent;
            handles.push(handle);
            inputHandles.value = JSON.stringify(handles);
        });
    }
   
}