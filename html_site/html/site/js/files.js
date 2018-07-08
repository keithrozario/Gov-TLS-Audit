$( document ).ready(function() {
  	const url = "https://govscan.info/api/v2/listScans";
   	const resultsDiv = document.getElementById('scans');
   	resultsDiv.innerHTML = "";

  	fetch(url)
  	.then(function(response) {
  		 if(response.status === 200){
   			let scanspan = document.createElement('span');
   			let spanHead = "<br><br>List of Scans: <br>";
   			scanspan.innerHTML = spanHead
   			resultsDiv.appendChild(scanspan)
   			}
   			$('#img-load').hide();
   	return response.json();
	})

	.then(function(response_json){
 
	response_json.files.forEach(function(element) {
			let filespan = document.createElement('span');
   			let filelink = "<br><a href=\"" + element.url + "\">"
   			let filename = element.fileName + " (" + element.fileSize + ")</a>"
   			filespan.innerHTML = filelink + filename
   			resultsDiv.appendChild(filespan)
	})
 	}).catch(function(error) {
  		return;
	});
});

