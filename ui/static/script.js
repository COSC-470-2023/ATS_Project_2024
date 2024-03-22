console.log("Script loaded!");

// SIDEBAR
const hamburger = document.querySelector("#toggle-btn");

hamburger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

// --------------------------- CHANGE CONFIGURTAION PAGE ---------------------------------------------------

//modal search
function searchList() {
  // Declare variables
  var input, filter, ul, li, i, txtValue;
  input = document.getElementById("searchInput");
  filter = input.value.toUpperCase();
  ul = document.querySelector(".modal-list ul"); // Select the ul element within the modal
  li = ul.getElementsByTagName("li");

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    txtValue = li[i].textContent || li[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
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

// --------------------------- DOWNLOAD DATA PAGE ---------------------------------------------------

function datepicker() {
  $(function () {
    $('input[name="daterange"]').daterangepicker({
      startDate: new Date(),
      endDate: new Date(),
      minDate: new Date(new Date().getFullYear() - 3, 0, 1),
      opens: "center",
      locale: {
        format: "DD/MM/YYYY",
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
  // Can functions to populate lists on initial page load
  onDataChange();
  onDataTypeChange();
  // Add event listener to the select dropdown
  const selectData = document.getElementById("select-data");
  selectData.addEventListener("change", onDataChange);

  // Add event listener to the radio buttons
  const radioButtons = document.querySelectorAll('input[name="data-type"]');
  radioButtons.forEach((radioButton) => {
    radioButton.addEventListener("change", onDataTypeChange);
  });
});

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
          li.innerHTML = `<input type="checkbox" name="data-item" id="${
            item[entity_identifier]
          }" value="${item[entity_identifier]}" class="checkbox" />
                        <label for="${item[entity_identifier]}">${
            item[entity_identifier]
          }</label>`;
        } else {
          li.innerHTML = `<input type="checkbox" name="data-item" id="${
            item[entity_identifier]
          }" value="${item[entity_identifier]}" class="checkbox" />
                        <label for="${item[entity_identifier]}">${
            item[entity_identifier]
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
