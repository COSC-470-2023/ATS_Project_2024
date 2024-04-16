console.log("Script loaded!");

// SIDEBAR
const hamburger = document.querySelector("#toggle-btn");

hamburger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

// --------------------------- CHANGE CONFIGURTAION PAGE ---------------------------------------------------

function dynamicModal(title, modalId) {
  if (modalId === "remove-modal") {
    $("#remove-modal .modal-header h5").text(title);
    $("#remove-modal .modal-footer .btn-primary").text(title);
  } else if (modalId === "add-modal") {
    $("#add-modal .modal-header h5").text(title);
    $("#add-modal .modal-footer .btn-primary").text(title);
  }
}

// Function to filter through stock list
function searchList(context) {
  var inputId = context === 'remove' ? 'searchInputRemove' : 'searchInputAdd';
  var input = document.getElementById(inputId);
  var filter = input.value.toUpperCase();
  var ul = context === 'remove' ? document.querySelector("#remove-modal ul") : document.querySelector("#add-modal ul");
  var li = ul.getElementsByTagName("li");

  for (var i = 0; i < li.length; i++) {
    var txtValue = li[i].textContent || li[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}

// Function to query stocks from the config file
function getStocks(context) {
  fetch('/configuration/get_config', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(stocksInfo => {
      const configCard = context === 'config' ? document.getElementById("config-stock-list") : document.getElementById('stockList')
      //clear any existing list items
      configCard.innerHTML = '';
      // Loop through each stock and create a list item for each
      stocksInfo.forEach(stock => {
        const label = document.createElement('li');
        label.classList.add('checkbox');

        if (context === 'modal') {
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.name = 'stocksToRemove';
          checkbox.value = stock.symbol;
          label.appendChild(checkbox);
        }

        label.appendChild(document.createTextNode(`${stock.symbol} - ${stock.name}`));
        configCard.appendChild(label);
      });
    })
    .catch(error => console.error('Error fetching stocks:', error));
}

// Function to remove selected stocks in the config file
function removeStocks() {
  // Get all selected checkboxes
  var checkboxes = document.querySelectorAll('input[name="stocksToRemove"]:checked');
  var symbols = Array.from(checkboxes).map(function (checkbox) {
    return checkbox.value;
  });

  fetch('/configuration/remove_config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ symbols: symbols })
  })
    .then(response => {
      if (response.ok) {
        getStocks('modal');
        getStocks('config');
      } else {
        console.error('Error removing stocks');
      }
    })
    .catch(error => console.error('Error removing stocks:', error));
}

// Function to display available stocks from the API
function displayAvailableStocks() {
  // Display loading sign
  availableStockList.innerHTML = '';
  document.getElementById('loadingIndicator').style.display = 'block';

  fetch('/configuration/compare_stocks', {
    method: 'GET', 
    headers: {
      'Content-Type': 'application/json'
    },
  })
    .then(response => {
      // Hide loading sign regardless of response status
      document.getElementById('loadingIndicator').style.display = 'none';

      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Failed to fetch available stocks');
      }
    })
    .then(data => {
      if (data && Array.isArray(data.not_common_stocks)) {
        var stockList = document.getElementById('availableStockList');
        stockList.innerHTML = '';

        // Populate stock list with checkboxes
        data.not_common_stocks.forEach(stock => {
          var listItem = document.createElement('li');
          var checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.value = stock.symbol;
          listItem.appendChild(checkbox);
          listItem.appendChild(document.createTextNode(`${stock.symbol} - ${stock.name}`));
          stockList.appendChild(listItem);
        });
      } else {
        throw new Error('Available stocks not found in response data');
      }
    })
    .catch(error => console.error('Error fetching available stocks:', error));
}

// Function to add selected stocks in the config file
function addSelectedStocks() {
  var maxSelected = 10; 
  var selectedStocks = [];
  var checkboxes = document.querySelectorAll('#availableStockList input[type="checkbox"]:checked');

  if (checkboxes.length > maxSelected) {
    alert('You can only select a maximum of ' + maxSelected + ' stocks at a time.');
    return;
  }

  checkboxes.forEach(checkbox => {
    var symbol = checkbox.value;
    var name = checkbox.nextSibling.textContent.trim().split(' - ')[1]; // Extract name from text
    selectedStocks.push({ symbol: symbol, name: name });
  });

  // Send selected stocks to the server
  fetch('/configuration/add_stocks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ selected_stocks: selectedStocks })
  })
  .then(response => {
    if (response.ok) {
      return response.json();
      getStocks('config');
    } else {
      throw new Error('Failed to add selected stocks');
    }
  })
  .then(data => {
    console.log('Selected stocks added successfully:', data);
    getStocks('config');

  })
  .catch(error => console.error('Error adding selected stocks:', error));
}


// --------------------------- JOB SCHEDULING PAGE ---------------------------------------------------

// job scheduling - data file  drop down
function selectItem(item) {
  var selectedText = item.textContent;
  document.getElementById("dropdownMenuButton").textContent = selectedText;
}

// job scheduling - default setting or custom setting checkbox - border on or off
function defaultBorder() {
  var checkbox = document.getElementById("default-checkbox");
  var defaultSetting = document.getElementById("default-setting");

  // If checkbox is checked, add border class, otherwise remove it
  if (checkbox.checked) {
    defaultSetting.classList.add("border-on-checkbox");
  } else {
    defaultSetting.classList.remove("border-on-checkbox");
  }
}

function customBorder() {
  var checkbox = document.getElementById("custom-checkbox");
  var defaultSetting = document.getElementById("custom-setting");

  // If checkbox is checked, add border class, otherwise remove it
  if (checkbox.checked) {
    defaultSetting.classList.add("border-on-checkbox");
  } else {
    defaultSetting.classList.remove("border-on-checkbox");
  }
}

//changes the current jobscheduling on change of option in the dropdown
function jobSelectorOnChange() {
  const DOWMap = {
    "0": "SUN",
    "1": "MON",
    "2": "TUE",
    "3": "WED",
    "4": "THU",
    "5": "FRI",
    "6": "SAT",
  }
  const jobSelector = document.getElementById("jobType");
  const currentSchedule = JSON.parse(document.getElementById("currentSchedule").textContent);
  const updateValues = event => {
    let jobValues = currentSchedule.find(job => job.name == jobSelector.value)
    if (jobValues.hour != null) {
      document.getElementById("currentTime").innerHTML = jobValues.hour + ":" + jobValues.minute.toString().padStart(2, '0');
    } else {
      document.getElementById("currentTime").innerHTML = "hourly";
    }

    let weekDays = jobValues.day ?? '*';
    console.log(weekDays)
    if (weekDays != '*'){
      weekDays = weekDays.map(x => DOWMap[String(x).trim()]);
      weekDays = weekDays.join(",");
    }

    document.getElementById("currentDOW").innerHTML = weekDays;
    document.getElementById("currentDOM").innerHTML = jobValues.month ?? '*';
  };
  jobSelector.onchange = updateValues;
  updateValues();
}

//logic for the input selector to check if "*" is in the crontab
function selectOptions(selectElementId, value, isWildcard) {
  let selectElement = document.getElementById(selectElementId);
  Array.from(selectElement.options).forEach(option => {
      if (isWildcard) {
          option.selected = true;
          // Select all options if wildcard is true (*)
      } else {
          option.selected = option.value === value;
          // Select option if value matches
      }
  });
}

//updates the custom job fields with the defaults if default is selected.
function inputJobSelectorOnChange() {
  const jobSelector = document.getElementById("inputJobType");
  const currentSchedule = JSON.parse(document.getElementById("currentSchedule").textContent) ;
  const updateValues = event => {
    let defaultButtonSelected = document.getElementById("default-checkbox");
    if (defaultButtonSelected.checked) {
      let jobValues = currentSchedule.find(job=>job.name==jobSelector.value);
      let defaultValues = jobValues.default.split(" ");

      //time string processing and setting
      document.getElementById("time").value = defaultValues[1].toString().padStart(2, '0') + ":" + defaultValues[0].toString().padStart(2, '0');
      
      let dayOfWeekWildcard = defaultValues[4] === '*';
      //if a * is present then deal with it
      selectOptions('dayOfWeek', defaultValues[4], dayOfWeekWildcard);

      let dayOfMonthWildcard = defaultValues[2] === '*';
      //if a * is present then deal with it
      selectOptions('dayOfMonth', defaultValues[2], dayOfMonthWildcard);
    }
  };
  jobSelector.onchange = updateValues;
  updateValues();
}

//sets the logic for the default custom radioboxes
function defaultButtonReset(){
  //for some reason If the input fields are not pulled into a variable like this it doesn't work on my machine...
  //also swapping to using const now as requested.
  const defaultCheckbox = document.getElementById("default-checkbox");
  const customCheckbox = document.getElementById("sched-checkbox");
  const timeInput = document.getElementById('timeInput');
  const repeatMethodInput = document.getElementById('repeatMethodInput');
  const repeatContainerInput = document.getElementById('repeatContainer');
  
  //Update visibility based on default/custom radiobutton
  function toggleInputVisibility() {
    if (defaultCheckbox.checked) {
      timeInput.style.display = 'none';
      repeatMethodInput.style.display = 'none';
      repeatContainerInput.style.display = 'none';

      //When the default button is checked again it resets the input fields
      inputJobSelectorOnChange();

    } else if (customCheckbox.checked) {
      repeatMethodInput.style.display = 'block';
      timeInput.style.display = 'block';
      repeatContainerInput.style.display = 'block';
    }
  }

  //Add event listener for default and custom. Must have custom or swapping options wont display blocks
  defaultCheckbox.addEventListener("change", toggleInputVisibility);
  customCheckbox.addEventListener("change", toggleInputVisibility);

  //Set initial visibility state when page loads
  toggleInputVisibility();
}


function repeatSelectorOnChange() {
  const repeatSelectors = document.getElementById("JobSchedulingForm").RepeatMethod; //dont worry about it...
  console.log(repeatSelectors);

  let repeatContainer = document.getElementById("repeatContainer");

  const updateValues = event => {
    repeatContainer.classList.add(event.target.dataset.show);
    repeatContainer.classList.remove(event.target.dataset.hide);
  };
  for (radio of repeatSelectors) {
    radio.onchange = updateValues;
  }
}

// --------------------------- DOWNLOAD DATA PAGE ---------------------------------------------------

function datepicker() {
  // Set end date to tomorrow, to handle ensure all date collected on the current day can be downloaded
  let today = new Date();
  today.setDate(today.getDate() + 1)
  
  $(function () {
    $('input[name="daterange"]').daterangepicker({
      startDate: new Date(new Date().getFullYear() - 3, 0, 1),
      endDate: today,
      minDate: new Date(new Date().getFullYear() - 3, 0, 1),
      opens: "center",
      locale: {
        format: "YYYY-MM-DD",
      },
    });
  });
}

function selectAllData(button) {
  var checkboxes;

  if (button.id === "data-selectAll-Btn") {
    checkboxes = $("#data-list .checkbox");
  } else if (button.id === "field-selectAll-Btn") {
    checkboxes = $("#lookup-field-list .checkbox, #value-field-list .checkbox");
  } else {
    return;
  }

  // Check if any of the checkboxes are already checked
  var checked = checkboxes.is(":checked");

  // Toggle the checkboxes
  checkboxes.prop("checked", !checked);
}

function resetAll() {
  location.reload();
}

document.addEventListener("DOMContentLoaded", function () {
  //Finds out what page it's on and runs that page's logic
  if (window.location.href.indexOf("data-export") != -1) {
    exportpage()
  } else if (window.location.href.indexOf("job-scheduling") != -1) {
    jobSelectorOnChange();
    repeatSelectorOnChange();
    inputJobSelectorOnChange();
    defaultButtonReset()
  } else if (window.location.href.indexOf("configuration") != -1) {
    getStocks('config');
  }
});

//moved the functionality out of main
function exportpage() {
  // Call function to populate lists on initial page load
  onDataChange();
  // Add event listener to the select dropdown
  const selectData = document.getElementById("select-data");
  selectData.addEventListener("change", onDataChange);

  // Add event listener to the radio buttons
  const radioButtons = document.querySelectorAll('input[name="data-type"]');
  radioButtons.forEach((radioButton) => {
    radioButton.addEventListener("change", onDataTypeChange);
  });
}


// Function to dynamically update data item list (Stock, Index, Bonds, etc...) based on selection.
function onDataChange() {
  // Update field list based on data selection
  onDataTypeChange();

  const selected_entity = document.getElementById("select-data").value;
  const entity_identifier =
    selected_entity === "Bonds" ? "treasuryName" : "symbol";
  let item_field_name = "";

  // Disable radio buttons if selected entity is "Bonds" or "company-info"
  const radioButtonElements = document.querySelectorAll('input[name="data-type"]');
  radioButtonElements.forEach(radioButton => {
    radioButton.disabled = selected_entity === "Bonds" || selected_entity === "company-info";
  });

  // Determine name field
  switch (selected_entity) {
    case "Companies":
      item_field_name = "companyName";
      break;
    case "company-info":
      item_field_name = "companyName";
      break;
    case "Indexes":
      item_field_name = "indexName";
      break;
    case "Commodities":
      item_field_name = "commodityName";
      break;
  }

  fetch("/data-export/get-data-list", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      selected_entity: selected_entity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Update the data list with the received items
      const dataList = document.getElementById("data-list");
      dataList.innerHTML = "";

      data.items.forEach((item) => {
        const li = document.createElement("li");

        if (selected_entity === "Bonds") {
          li.innerHTML = `<input type="checkbox" name="data-item" id="${item[entity_identifier]
            }" value="${item[entity_identifier]}" class="checkbox" />
                        <label for="${item[entity_identifier]}">${item[entity_identifier]
            }</label>`;
        } else {
          li.innerHTML = `<input type="checkbox" name="data-item" id="${item[entity_identifier]
            }" value="${item[entity_identifier]}" class="checkbox" />
                        <label for="${item[entity_identifier]}">${item[entity_identifier]
            } - ${item[item_field_name]}</label>`;
        }

        dataList.appendChild(li);
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Function to handle the dynamic loading of fields based on data type selection (Realtime or Historical)
function onDataTypeChange() {
  const selected_data_type = document.querySelector(
    'input[name="data-type"]:checked'
  ).value;
  const selected_entity = document.getElementById("select-data").value;

  fetch("/data-export/get-field-list", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      selected_data_type: selected_data_type,
      selected_entity: selected_entity,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Update the field list with the received fields from the lookup table
      const lookupFieldList = document.getElementById("lookup-field-list");
      lookupFieldList.innerHTML = "";

      // Add lookup table fields to list
      const lookupHeader = document.createElement("h6");
      const lookupHeaderText = document.createTextNode("Lookup Fields:");
      lookupHeader.appendChild(lookupHeaderText);
      lookupFieldList.appendChild(lookupHeader);

      data.lookup_fields.forEach((field) => {
        const li = document.createElement("li");
        li.innerHTML = `<input type="checkbox" name="lookup-field-item" id="${field}" value="${field}" class="checkbox" checked/>
                      <label for="${field}">${field}</label>`;
        lookupFieldList.appendChild(li);
      });

      const br = document.createElement("br");
      lookupFieldList.appendChild(br);

      // Update the field list with the received fields from the lookup table
      const valueFieldList = document.getElementById("value-field-list");
      valueFieldList.innerHTML = "";

      const valueHeader = document.createElement("h6");
      const valueHeaderText = document.createTextNode("Value Fields:");
      valueHeader.appendChild(valueHeaderText);
      valueFieldList.appendChild(valueHeader);

      data.value_fields.forEach((field) => {
        const li = document.createElement("li");
        li.innerHTML = `<input type="checkbox" name="value-field-item" id="${field}" value="${field}" class="checkbox" checked/>
                      <label for="${field}">${field}</label>`;
        valueFieldList.appendChild(li);
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

datepicker();
