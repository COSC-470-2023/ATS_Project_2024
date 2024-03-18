console.log("Script loaded!");

// SIDEBAR
const hamburger = document.querySelector("#toggle-btn");

hamburger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

var stockItems = ["Stock 1", "Stock 2", "Stock 3", "Stock 4", "Stock 5"];
var constituentItems = [
  "Constituent 1",
  "Constituent 2",
  "Constituent 3",
  "Constituent 4",
  "Constituent 5",
];
var dataSourceItems = [
  "Data Source 1",
  "Data Source 2",
  "Data Source 3",
  "Data Source 4",
  "Data Source 5",
];

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

function selectAll() {
  var checkboxes = $(".modal-list .checkbox");
  // Check if any of the checkboxes are already checked
  var anyChecked = checkboxes.is(":checked");
  checkboxes.prop("checked", !anyChecked);
}

function selectAllFilter() {
  var filterCheckboxes = $(".filter-modal-list .checkbox"); 
  // Check if any of the checkboxes are already checked
  var anyChecked = filterCheckboxes.is(":checked"); 
  filterCheckboxes.prop("checked", !anyChecked); 
}

function resetAll() {
  var dataCB = $(".modal-list .checkbox");
  var dataTypeCB = $("#data-type-list .checkbox");
  var selectData = $("#select-data option");
  var dateRange = $("#datepicker");

  dataCB.prop("checked", false);
  dataTypeCB.prop("checked", false);
  selectData.prop("selected", false);
  datepicker();
}

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
  if (storedValue) {
    const dataSelect = document.getElementById("select-data");
    dataSelect.value = storedValue;

    // Clear the stored value
    sessionStorage.removeItem("selectedValue");
  }
});

datepicker();
//selectAll();
resetAll();
