


document.addEventListener("DOMContentLoaded", function() {
    let historyStack = [];



    function updateDisplay() {
        // Update the display of the navigation stack
        const historyElement = document.getElementById('history');
        historyElement.innerHTML = ''; // Clear current history display

        historyStack.forEach((path, index) => {
            const pathElement = document.createElement('span');
            pathElement.textContent = path;
            pathElement.className = 'history-item';
            pathElement.onclick = () => loadFromHistory(index);
            historyElement.appendChild(pathElement);
        });
    }

    function loadFromHistory(index) {
        // Load the selected history item and truncate history after that
        historyStack = historyStack.slice(0, index + 1);
        const path = historyStack[index];
        fetchItems(path);
        updateDisplay();
    }



    // When the user clicks on <span> (x), close the modal
    document.querySelectorAll('.close').forEach(closeButton => {
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                document.getElementById('myModal').style.display = "none";
                document.getElementById('versionModal').style.display = "none";
    
            });
        }
    });

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        var modal = document.getElementById('myModal');
        if (event.target === modal) {
            modal.style.display = "none";
        }
        modal = document.getElementById('versionModal');
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
    // Fetch and display the initial list of items on page load
    fetchItems('');

    function fetchItems(path,add) {
        fetch('/get_items/' + path)
            .then(response => response.json())
            .then(data => displayItems(data, path))
            .catch(error => console.error('Error:', error));
           // Add the new path and update the display
        if(add)
            historyStack.push(path);
        updateDisplay();
    
    }

    function displayItems(items, currentPath) {
        const container = document.getElementById('repository-container');
        container.innerHTML = ''; // Clear existing content

        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'item';

            div.textContent = item.replaceAll('\\','/').split('/').pop(); // Display only the last part of the path

            // Add click event listener for each item
            div.addEventListener('click', function() {
                if (item.endsWith('.jar')) {
                    // Handle JAR file click
                    showJarContents(item);
                } else {
                    // Handle directory click
                    fetchItems(item,true);
                }
            });

            container.appendChild(div);
        });
    }

    function showJarContents(jarPath) {
        fetch('/library/' + jarPath)
            .then(response => response.json())
            .then(data => {
                if (data.files && data.files.length > 0) {
                    // Create content for the modal
                    let content = data.files.map(file => `<li>${file}</li>`).join('');
                    content = `<ul>${content}</ul>`;
    
                    // Display the modal with the content
                    showModal(content);
                } else {
                    // Handle the case where there are no files or an error
                    showModal('No .java files found or an error occurred.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showModal('Error fetching JAR contents.');
            });
    }
    
    function showModal(content) {
        const modal = document.getElementById('myModal');
        const modalContent = document.getElementById('modalContent');
        modalContent.innerHTML = content;
        modal.style.display = "block";
    }
    
});
document.addEventListener('keydown', function(event) {
    if (event.altKey  && event.key === 'p') {
        document.getElementById('versionModal').style.display = 'block';
    }
});

// Function to publish version
function publishVersion() {
    const version = document.getElementById('versionInput').value;
    fetch('/run_gradle_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({version: version}),
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById('versionModal').style.display = "none";
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('WebSocket connected!');
});

socket.on('gradle_status', function(data) {
    if(data.status === 'Done') {
        // Notify the user
        alert("Gradle task is completed!");
    }

});
socket.on('test', function(data) {
    if(data.status === 'Done') {
        // Notify the user
        alert("Gradle task is completed!");
    }

});
