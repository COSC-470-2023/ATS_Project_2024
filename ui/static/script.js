console.log("Script loaded!");

// Sidebar
const hamburger = document.querySelector("#toggle-btn");

hamburger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

//change config - modal search
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

// job scheduling - data file drop down
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

// job scheduling - default setting or custom setting checkbox - border on or off
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

// data export - datepicker
function datepicker() {
  $(function() {
    $('input[name="daterange"]').daterangepicker({
      startDate: new Date(),
      endDate: new Date(),
      minDate: new Date(new Date().getFullYear() - 3, 0, 1),
      opens: 'center',
      locale: {
        format: 'DD/MM/YYYY'
      }
    });
  });
}

function selectAllData(button) {
  var checkboxes;
  if (button.id === 'data-selectAll-Btn') {
    checkboxes = $("#data-list .checkbox");
  } else if (button.id === 'field-selectAll-Btn') {
    checkboxes = $("#field-list .checkbox");
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

// Function to handle when data type is changed (historical or realtime)
function onDataTypeChange(event) {
  if (event.target.checked) {
    localStorage.setItem('selectedDataType', event.target.value);
    location.reload();
  }
}

const dataTypeRadios = document.querySelectorAll('input[name="data-type"]')

dataTypeRadios.forEach(radio => {
  radio.addEventListener('change', onDataTypeChange);
});

// changes the state of "Data Type" radio button based on the data selection
function onDataChange() {
  const dataSelect = document.getElementById("select-data");
  const realtime = document.getElementById("realtime-data");
  const historical = document.getElementById("historical-data");
  const dataValue = dataSelect.value;
  
  if (dataSelect.value === "Bonds" || dataSelect.value === "company-info") {
    realtime.disabled = true;
    historical.disabled = true;
  } else {
    realtime.disabled = false;
    historical.disabled = false;
  }

  // Set query params (dataValue needs to be saved to session storage)
  const params = new URLSearchParams(window.location.search);
  params.set("realtimeDisabled", realtime.disabled);
  params.set("historicalDisabled", historical.disabled);
  params.set("dataValue", dataValue);
  sessionStorage.setItem("selectedValue", dataValue);

  window.location.href = "/data-export?" + params.toString();
}

document.addEventListener("DOMContentLoaded", function () {
  const storedValue = sessionStorage.getItem("selectedValue");
  const dataType = localStorage.getItem('selectedDataType');
  const radio = document.querySelector(`input[value="${dataType}"]`)
  if (storedValue) {
    const dataSelect = document.getElementById("select-data");
    dataSelect.value = storedValue;

    // Clear the stored value
    sessionStorage.removeItem("selectedValue");
  }
  if (dataType) {
    if (radio.disabled) {
      radio.checked = false;
    } else {
      radio.checked = true;
    }
  }
});

datepicker();