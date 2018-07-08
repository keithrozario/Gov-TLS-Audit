$(document).ready(function () {

  var result_table = document.getElementById("result_table");
  var error_message = document.getElementById("error_message");
  var baseUrl = "https://govscan.info/api/v2/siteHistory?FQDN=";
  var urlAddition = "";
  var urlScanDetail = "https://govscan.info/api/v2/scanDetails?FQDN=";

  $('.form').find('input, textarea').on('keyup blur focus', function (e) {

    var $this = $(this),
      label = $this.prev('label');

    if (e.type === 'keyup') {
      if ($this.val() === '') {
        label.removeClass('active highlight');
      } else {
        label.addClass('active highlight');
      }
    } else if (e.type === 'blur') {
      if ($this.val() === '') {
        label.removeClass('active highlight');
      } else {
        label.removeClass('highlight');
      }
    } else if (e.type === 'focus') {

      if ($this.val() === '') {
        label.removeClass('highlight');
      } else if ($this.val() !== '') {
        label.addClass('highlight');
      }
    }

  });

document.getElementById('callAPI').onclick = checkHistory;
  $('#img-load').hide();

  // start request when "return" key is pressed
  $('#FQDN').keypress(function (e) {
    if (e.which == 13) {
      checkHistory();
    }
  });

  // clear table when loading new informations
  function clearTable() {
    while (result_table.rows.length > 0) {
      result_table.deleteRow(0);
    }
  }

  // give cell onclick listener
  function createCellButton(rowPosition, scanDateTime) {
    document.getElementById('result_table').getElementsByTagName('tbody')[0].rows[rowPosition - 1].cells[0].onclick = function () {
      var tempPosition = Number(rowPosition);
      var tempScanDateTime = scanDateTime;

      if ((result_table.rows[tempPosition + 1].cells[0].innerHTML) == "") {
        additionalInformations(tempPosition, tempScanDateTime);
      } else {
        result_table.rows[tempPosition + 1].cells[0].innerHTML = "";
      }
    };
  }

  function additionalInformations(tempPosition, tempScanDateTime) {
    result_table.rows[tempPosition + 1].cells[0].innerHTML = "<img src='img/loading.gif' height='42' width='42' alt='' style='margin:20px'>";
    // $('#img-load').show();
    error_message.innerHTML = "";
    fetchAdditionalInformations(tempPosition, tempScanDateTime);

  }

  function fetchAdditionalInformations(tempPosition, tempScanDateTime) {

    console.log(urlScanDetail.concat(urlAddition).concat("&scanDate=" + tempScanDateTime));
    fetch(urlScanDetail.concat(urlAddition).concat("&scanDate=" + tempScanDateTime)).then(
        function (response) {
          if (response.status !== 200) {

            console.log('Error : ' +
              response.status); 
              result_table.rows[tempPosition + 1].cells[0].innerHTML ="";
            displayErrorMessage("<h2>No Entries found !<h2>");
            return;
          }

          // console.log(response.status);
          response.json().then(function (data) {
            result_table.rows[tempPosition + 1].cells[0].innerHTML ="";

            var tempCell = result_table.rows[tempPosition + 1].cells[0];


            if (data.hasOwnProperty('ip')) {
              tempCell.innerHTML += "<span class='fontcolor'>" + "IP : " + "</span>" + data.ip + '<br>';
            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "IP : " + "</span>" + "n.a." + "<br>";
            }

            if (data.hasOwnProperty('redirectType')) {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Redirect Type : " + "</span>" + data.redirectType + '<br>';
            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Redirect Type : " + "</span>" + "n.a." + "<br>";
            }

            if (data.hasOwnProperty('formFields')) {
              // split result to make line break possible
              var tempSplittable = data.formFields;
              var splitted = tempSplittable.replace(/\|/g, ' \| ');
              tempCell.innerHTML += "<span class='fontcolor'>" + "Form Fields : " + "</span>" + splitted + '<br>';
            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Form Fields : " + "</span>" + "n.a." + "<br>";
            }

            if (data.hasOwnProperty('certData')) {
              if (data.certData.hasOwnProperty('notValidBefore')) {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Issued : " + "</span>" + data.certData.notValidBefore + '<br>';
              } else {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Issued : " + "</span>" + "n.a." + "<br>";
              }

            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Issued : " + "</span>" + "n.a." + "<br>";
            }



            if (data.hasOwnProperty('certData')) {
              if (data.certData.hasOwnProperty('notValidAfter')) {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Expiry : " + "</span>" + data.certData.notValidAfter + '<br>';
              } else {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Expiry : " + "</span>" + "n.a." + "<br>";
              }
            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Cert Expiry : " + "</span>" + "n.a." + "<br>";
            }


            if (data.hasOwnProperty('TLSServerInfo')) {
              if (data.TLSServerInfo.hasOwnProperty('highestTLSVersionSupported')) {
                tempCell.innerHTML += "<span class='fontcolor'>" + "TLS Version : " + "</span>" + data.TLSServerInfo.highestTLSVersionSupported + '<br>';
              } else {
                tempCell.innerHTML += "<span class='fontcolor'>" + "TLS Version : " + "</span>" + "n.a." + "<br>";
              }

            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "TLS Version : " + "</span>" + "n.a." + "<br>";
            }

            if (data.hasOwnProperty('certData')) {
              if (data.certData.hasOwnProperty('serialNumber')) {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Serial : " + "</span>" + data.certData.serialNumber + '<br>';
              } else {
                tempCell.innerHTML += "<span class='fontcolor'>" + "Serial : " + "</span>" + "n.a." + "<br>";
              }

            } else {
              tempCell.innerHTML += "<span class='fontcolor'>" + "Serial : " + "</span>" + "n.a." + "<br>";
            }

          });
        }
      )
      .catch(function (err) {
        result_table.rows[tempPosition + 1].cells[0].innerHTML ="";

        console.log('Error : ', err);
        displayErrorMessage("<h2>No Entries found !<h2>");
      });

  }

  function displayErrorMessage(message) {
    error_message.innerHTML = message;

  }

  function checkHistory() {

    $('#img-load').show();
    clearTable();
  urlAddition = document.getElementById("FQDN").value;

    error_message.innerHTML = "";
    console.log(baseUrl.concat(urlAddition));
    fetch(baseUrl.concat(urlAddition)).then(
        function (response) {
          if (response.status !== 200) {

            console.log('Error : ' +
              response.status);$('#img-load').hide();
            displayErrorMessage("<h2>No Entries found !<h2>");
            return;
          }

          // console.log(response.status);
          response.json().then(function (data) {
            $('#img-load').hide();
createResultTable(data);
          });
        }
      )
      .catch(function (err) {
        $('#img-load').hide();
console.log('Error : ', err);
        displayErrorMessage("<h2>No Entries found !<h2>");
      });

  }

  // create result table
  function createResultTable(data) {

    // create head
    var header = result_table.createTHead();
    var row = header.insertRow(0);
    // 1st cell
    var cell = row.insertCell(0);
    cell.innerHTML = "Date";
    // 2nd cell
    var cell = row.insertCell(1);
    cell.innerHTML = "TLS Redirect";
    // 3rd cell
    var cell = row.insertCell(2);
    cell.innerHTML = "TLS Implemented";
    // 4th cell
    var cell = row.insertCell(3);
    cell.innerHTML = "Page Size";

    var tableRef = document.getElementById('result_table').getElementsByTagName('tbody')[0];

    for (var i = 0; i < data.results.length; i++) {

      var newRow = tableRef.insertRow(tableRef.rows.length);

      // 1st cell
      var newCell = newRow.insertCell(0);
      var newText = document.createTextNode(data.results[i].scanDate);
      newCell.appendChild(newText);
      // make cell clickable
      createCellButton(tableRef.rows.length, data.results[i].scanDateTime);
      // insert row for additional informations
      tableRef.insertRow(tableRef.rows.length).insertCell(0).colSpan = 4;

      // 2nd cell
      newCell = newRow.insertCell(1);
      newText = data.results[i].TLSRedirect;
      
      if (newText) {
        newCell.innerHTML = "<img src='img/true.png' alt='true'/>";
      } else {
        newCell.innerHTML = "<img src='img/false.png' alt='true'/>";
      }

      // 3rd cell
      newCell = newRow.insertCell(2);
      newText = data.results[i].TLSSiteExist;
      if (newText) {
        newCell.innerHTML = "<img src='img/true.png' alt='true'/>";
      } else {
        newCell.innerHTML = "<img src='img/false.png' alt='true'/>";
      }

      // 4th cell
      newCell = newRow.insertCell(3);
      newText = document.createTextNode(data.results[i].htmlSize);
      newCell.appendChild(newText);
    }
  }
});