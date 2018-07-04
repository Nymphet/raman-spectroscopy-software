function parseJSONToCSVStr(jsonData) {
    if(jsonData.length == 0) {
        return '';
    }
    
    let keys = Object.keys(jsonData);
    
    let columnDelimiter = ',';
    let lineDelimiter = '\n';
    
    let csvColumnHeader = keys.join(columnDelimiter);
    let csvStr = csvColumnHeader + lineDelimiter;
    
    for (var i = 0; i < jsonData[keys[0]].length; i++) {
        keys.forEach(
            function(key){
                csvStr += jsonData[key][i];
                csvStr += columnDelimiter;
            }
        )
        csvStr = csvStr.slice(0, -1);
        csvStr += lineDelimiter;
    }

    return encodeURIComponent(csvStr);
}

function exportToCsvFile(jsonData) {
    let csvStr = parseJSONToCSVStr(jsonData);
    let dataUri = 'data:text/csv;charset=utf-8,'+ csvStr;
    
    let exportFileDefaultName = 'data.csv';
    
    let linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

var jsonData = source.data;
exportToCsvFile(jsonData);