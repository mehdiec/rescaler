let checkStreamlit = setInterval(function () {
    if (typeof streamlit !== "undefined") {
        // Your code that uses streamlit.sendBack
        clearInterval(checkStreamlit);
    }
}, 500);  // Checks every 500 milliseconds

document.addEventListener('click', function (event) {
    ['suggestion-list'].forEach(id => {
        const suggestionList = document.getElementById(id);
        const inputElement = suggestionList.previousElementSibling;
        if (event.target !== inputElement) {
            suggestionList.innerHTML = "";
        }
    });
});
console.log(document.getElementById('suggestion-list'));
console.log(document.getElementById('project_folder'));
function addFocusEventListener(id, listId) {
    document.getElementById(id).addEventListener('focus', function () {
        getSuggestions(id, listId);
    });
}



async function getSuggestions(inputId, listId) {
    const input = document.getElementById(inputId).value;
    console.log(input)
    const response = await fetch('http://localhost:5001/autocomplete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ partial_path: input }),
    });

    const data = await response.json();
    const suggestionList = document.getElementById(listId);
    suggestionList.innerHTML = "";

    data.suggestions.forEach((suggestion) => {
        const listItem = document.createElement('li');
        listItem.innerText = suggestion.split("/").pop();
        listItem.onclick = function () { selectSuggestion(suggestion, inputId, listId); };
        suggestionList.appendChild(listItem);
    });
}

function selectSuggestion(suggestion, inputId, listId) {
    document.getElementById(inputId).value = suggestion + "/";
    getSuggestions(inputId, listId); // Call getSuggestions again after selecting a suggestion
}



function populateCheckboxes(subFolders) {
    const checkboxContainer = document.getElementById('checkbox-container');
    checkboxContainer.innerHTML = '';  // Clear existing checkboxes

    subFolders.forEach(folder => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = folder;
        checkbox.value = folder;

        const label = document.createElement('label');
        label.htmlFor = folder;
        label.appendChild(document.createTextNode(folder));
        checkbox.addEventListener('change', function () {
            toggleTab(folder, this.checked);
        });

        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(label);
        checkboxContainer.appendChild(document.createElement('br'));
    });
}

function sendToStreamlit() {
    const button_zar = document.getElementById('zarrify_button');
    const div_all = document.getElementById('all');
    button_zar.innerHTML = "";


    const project_folder = document.getElementById('project_folder').value;
    console.log("Sending data:", JSON.stringify({ project_folder }));
    fetch('http://127.0.0.1:5001/zarrify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_folder })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            populateCheckboxes(data.sub_folders);
            button_zar.innerHTML = '<button onclick="sendToStreamlit()">Zarrify</button>';
        });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
}

function toggleTab(folder, isChecked) {
    const tabsContainer = document.getElementById('tabs-container');

    if (isChecked) {
        // Create a new tab if the checkbox is checked
        const newTab = document.createElement('div');
        newTab.id = `tab-${folder}`;
        newTab.className = 'tab';
        newTab.innerHTML = `<span>${folder}</span>`;
        tabsContainer.appendChild(newTab);
    } else {
        // Remove the tab if the checkbox is unchecked
        const existingTab = document.getElementById(`tab-${folder}`);
        if (existingTab) {
            tabsContainer.removeChild(existingTab);
        }
    }
}
