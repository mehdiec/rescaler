// const htmlTemplate = ` 
// <form>
//   <label for="dt">dt:</label>
//   <input type="number" step="0.01" id="dt" name="dt"><br>

//   <label for="zoom-level">Zoom Level:</label>
//   <input type="number" step="0.01" id="zoom-level" name="zoom-level">
  
//   <label for="binning">Binning:</label>
//   <input type="number" step="0.01" id="binning" name="binning"><br>

//   <label for="n_digits">n_digits:</label>
//   <input type="number" id="n_digits" name="n_digits"><br>

//   <label for="temperature">Temperature:</label>
//   <input type="number" id="temperature" name="temperature"><br>

//   <label for="box_size">Box Size:</label>
//   <select id="box_size" name="box_size">
//     <option value="small">Small</option>
//     <option value="medium">Medium</option>
//     <option value="large">Large</option>
//   </select><br>

//   <label for="fraction">Fraction:</label>
//   <input type="text" placeholder="int/int" id="fraction" name="fraction"><br>

//   <label for="quantity">Quantity:</label>
//   <select id="quantity" name="quantity">
//     <option value="option1">Option 1</option>
//     <option value="option2">Option 2</option>
//     <!-- Add more options here -->
//   </select><br>

//   <label for="timing">Timing:</label>
//   <input type="text" placeholder="int h int" id="timing" name="timing"><br>

// </form> 
// `
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
            handleCheckboxToggle(folder, this.checked);
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
    const mainContent = document.querySelector('.main-content');
    const mainPageButton = document.getElementById('main-page-button'); // Get the main page button

    if (sidebar.style.width === '0px' || !sidebar.style.width) {
        sidebar.style.width = '25%';
        sidebar.style.padding = '20px';
        mainContent.style.marginLeft = '25%';
        mainPageButton.style.display = 'none'; // Hide the main page button
    } else {
        sidebar.style.width = '0px';
        sidebar.style.padding = '0';
        mainContent.style.marginLeft = '0';
        mainPageButton.style.display = 'block'; // Show the main page button
    }
}


 

// Define the form HTML template here

const htmlTemplateMap = `
  <form>
    <label for="dt">les Anaimals:</label>
    <input type="number" step="0.01" id="dt" name="dt"><br>
    <!-- Add other form elements here -->
  </form>
`;

let lastChecked = null;  // Keep track of the last checked radio button

function toggleTab(folder, isChecked) {
    const htmlTemplate = `
  <form>
    <label for="attribute1">Attribute 1:</label>
    <input type="text" id="attribute1" name="attribute1"><br>
    <label for="attribute2">Attribute 2:</label>
    <input type="text" id="attribute2" name="attribute2"><br>
    <!-- Add other form elements here -->
    <button type="button" onclick="copyAttributes('${folder}')">Copy Attributes</button>
    <button type="button" onclick="validateAndSend('${folder}')">Validate and Send</button>
  </form>
`;
    const tabset = document.getElementById('tabset');
    const tabPanels = document.getElementById('tab-panels');

    const generatedId = `tab-${folder}`;  // Generate a unique ID

    if (isChecked) {
        // Create new tab radio input and label if checkbox is checked
        const newInput = document.createElement('input');
        newInput.type = 'radio';
        newInput.name = 'tabset';
        newInput.id = generatedId;
        newInput.setAttribute('aria-controls', folder);
        newInput.addEventListener('click', function () {
            if (this === lastChecked) {
                this.checked = false;  // Uncheck if already checked
                lastChecked = null;     // Reset lastChecked
            } else {
                lastChecked = this;     // Update lastChecked
            }
        });

        const newLabel = document.createElement('label');
        newLabel.htmlFor = generatedId;
        newLabel.innerText = folder;
 
        // Create new tab panel as a section
        const newPanel = document.createElement('section');
        newPanel.className = 'tab-panel';
        newPanel.id = folder;
        // Add HTML template to the new tab panel
        newPanel.innerHTML = htmlTemplate;

        tabset.appendChild(newInput);
        tabset.appendChild(newLabel);
        tabPanels.appendChild(newPanel);
        const panels = document.querySelectorAll('.tab-panel');
        panels.forEach(panel => {
            panel.style.display = 'none'; // hide all panels
          });
    } else {
        // Remove the tab radio input and label if checkbox is unchecked
        const existingInput = document.getElementById(generatedId);
        const existingLabel = document.querySelector(`label[for='${generatedId}']`);
        const existingPanel = document.getElementById(folder);

        if (existingInput && existingLabel && existingPanel) {
            tabset.removeChild(existingInput);
            tabset.removeChild(existingLabel);
            tabPanels.removeChild(existingPanel);
        }
    }
}
 

 

// Combine both functions to handle checkbox toggle
function handleCheckboxToggle(folder, isChecked) {
    toggleTab(folder, isChecked); 
}
function addNewTabPanel() {
    const tabset = document.getElementById('tabset');
    const tabPanels = document.getElementById('tab-panels');
    const map_string = 'map_parameter';  // Unique ID
    const generatedId = `tab-${map_string}`;  // Generate a unique ID

    if (mapParameterTabExists) {
        // If the tab already exists, toggle its visibility
        const existingPanel = document.getElementById(generatedId);
        existingPanel.style.display = existingPanel.style.display === 'none' ? 'flex' : 'none';
        return;  // Exit the function here
    }

    // Create new tab radio input and label
    const newInput = document.createElement('input');
    newInput.type = 'radio';
    newInput.name = 'tabset';
    newInput.id = generatedId;
    newInput.setAttribute('aria-controls', map_string);
    newInput.addEventListener('click', function () {
        if (this === lastChecked) {
            this.checked = false;
            lastChecked = null;
        } else {
            lastChecked = this;
        }
    });

    const newLabel = document.createElement('label');
    newLabel.htmlFor = generatedId;
    newLabel.innerText = map_string;

    // Create new tab panel as a section
    const newPanel = document.createElement('section');
    newPanel.className = 'tab-panel';
    newPanel.id = map_string;
    newPanel.style.display = 'flex';  // Make sure it's visible
    // Add HTML template to the new tab panel
    newPanel.innerHTML = htmlTemplateMap;

    // Append new elements to the DOM
    tabset.appendChild(newInput);
    tabset.appendChild(newLabel);
    tabPanels.appendChild(newPanel);

    mapParameterTabExists = true;  // Set the flag to true
}


document.addEventListener("DOMContentLoaded", function() {
    const tabset = document.getElementById('tabset');
    tabset.addEventListener('change', function(e) {
      const id = e.target.getAttribute('aria-controls');
      const panels = document.querySelectorAll('.tab-panel');
      
      panels.forEach(panel => {
        panel.style.display = 'none'; // hide all panels
      });
      
      const activePanel = document.getElementById(id);
      if (activePanel) {
        activePanel.style.display = 'flex'; // show the selected panel
      }
    });
  });
  let mapParameterTabExists = false;  // Flag to indicate if the map_parameter tab exists or not
 
  function toggleCollapse(elementId) {
    const element = document.getElementById(elementId);
    if (element.style.maxHeight) {
      element.style.maxHeight = null;
    } else {
      element.style.maxHeight = '33vh';  // You can adjust this value
    }
  }
   

function copyAttributes(folder) {
    // Logic to copy attributes to other animals.
    // You can access the form elements by their IDs or names
    console.log("Copy attributes for folder:", folder);
}

function validateAndSend(folder) {
    // Logic to validate the parameters and send them to the backend
    // You can access the form elements by their IDs or names
    console.log("Validate and send data for folder:", folder);
}

function runSelection() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const selectedValues = Array.from(checkboxes).map(checkbox => checkbox.value);

    console.log("Selected checkboxes: ", selectedValues);
}
