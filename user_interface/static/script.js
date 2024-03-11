console.log("Script loaded!");

// SIDEBAR
const hamburger = document.querySelector("#toggle-btn");

// hamburger.addEventListener("click", function () {
//   document.querySelector("#sidebar").classList.toggle("expand");
// });

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

// ADD FUNCTIONALITY
// Function to update modal title and button dynamically
function addModal(buttonClass, configList, targetListId) {
  $(document).on("click", buttonClass, function () {
    var button = $(this);
    var title = button.text(); // Get the text of the button
    $("#add-modal .modal-title").text(title); // Set the modal title
    $(".modal-footer .btn-primary").text(title); // Set the button text
    updateAddModalBody(configList.slice()); // Update modal body with the config list

    //Event Listener for adding selected items to the targetList
    $("#addBtnModal").on("click", function () {
      addSelectedItemsToConfigList(targetListId);
      $("#add-modal").modal("hide");
    });
  });
}

// Function to update the modal body with the config list
function updateAddModalBody(list) {
  var configListContainer = $("#add-modal").find(".modal-body .modal-list ul"); // Get the config list container inside the modal
  configListContainer.empty(); // Clear the previous content

  // Iterate over the list and create list items with checkboxes
  list.forEach(function (item) {
    var listItem = $("<li>"); // Create list item
    var checkbox = $("<input>")
      .attr("type", "checkbox")
      .addClass("config-item-checkbox"); // Create checkbox
    listItem.append(checkbox); // Append checkbox to list item
    listItem.append(item); // Append list item text
    configListContainer.append(listItem); // Append list item to the container
  });
}

// Function to add selected items to the target list based on the provided targetListId
function addSelectedItemsToConfigList(targetListId) {
  var checkedItems = $(
    ".modal-body .modal-list ul .config-item-checkbox:checked"
  ).closest("li"); // Get checked items
  var targetList = $("#" + targetListId); // Get the target list

  // Append checked items to the target list
  checkedItems.each(function () {
    var itemText = $(this).text().trim(); // Get the text content of the list item
    targetList.append("<li>" + itemText + "</li>"); // Append text content to the target list
  });
}

// Call the addModal function with the desired button class, config list, and target list ID
addModal(".addStock", stockItems, "config-stock-list");
addModal(".addConstituent", constituentItems, "config-constituent-list");
addModal(".addDataSource", dataSourceItems, "config-data-source-list");

//REMOVE FUNCTIONALITY
// Function to update modal title and button dynamically
function removeModal(buttonClass, configList, targetListId) {
  $(document).on("click", buttonClass, function () {
    var button = $(this);
    var title = button.text(); // Get the text of the button
    $("#remove-modal .modal-title").text(title); // Set the modal title
    $(".modal-footer .btn-primary").text(title); // Set the button text
    $("#remove-modal").data("targetListId", targetListId); // Set the targetListId as a data attribute in the Remove modal

    updateRemoveModalBody(targetListId); // Update modal body with the items from the target list
  });
}

// Function to handle removal of selected items from the target list
function removeSelectedItemsFromList(targetListId) {
  var targetList = $("#" + targetListId); // Get the target list

  // Find all checked checkboxes in the Remove modal and remove their corresponding list items from the target list
  $("#remove-modal-list .remove-item-checkbox:checked").each(function () {
    var listItemText = $(this).parent().text().trim(); // Get the text content of the parent element (list item)
    targetList.find('li:contains("' + listItemText + '")').remove(); // Remove the corresponding list item from the target list
  });
}

// Function to update the content of the Remove modal with items from the target list
function updateRemoveModalBody(targetListId) {
  var targetList = $("#" + targetListId); // Get the target list
  var removeModalList = $("#remove-modal-list"); // Get the list container in the Remove modal
  removeModalList.empty(); // Clear previous content

  // Iterate over the items in the target list and add them to the Remove modal
  targetList.find("li").each(function (index) {
    // Skip adding a checkbox for the first list item
    if (index !== 0) {
      var listItemText = $(this).text().trim(); // Get the text content of the list item
      var listItem = $("<li>"); // Create a list item element
      var checkbox = $("<input>")
        .attr("type", "checkbox")
        .addClass("remove-item-checkbox"); // Create a checkbox
      listItem.append(checkbox); // Append the checkbox to the list item
      listItem.append(listItemText); // Append the list item text
      sort.listItem();
      removeModalList.append(listItem); // Append the list item to the Remove modal list
    }
  });
}

// Call the removeModal function with the desired button class, config list, and target list ID
removeModal(".removeStock", stockItems, "config-stock-list");
removeModal(".removeConstituent", constituentItems, "config-constituent-list");
removeModal(".removeDataSource", dataSourceItems, "config-data-source-list");

// Event listener for the "Remove" button in the Remove modal
$(document).on("click", "#removeBtnModal", function () {
  var targetListId = $("#remove-modal").data("targetListId"); // Get the targetListId associated with the modal
  removeSelectedItemsFromList(targetListId); // Remove selected items from the target list associated with the modal
  $("#remove-modal").modal("hide");
});

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
