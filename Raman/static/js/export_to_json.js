function parseJSONToPyJSON(jsonData) {
    if(jsonData.length == 0) {
        return '';
    }
    
    let pyJson = {};

    pyJson['rawdata_x'] = jsonData['rawdata_x'];

    var intensitiesObj = jsonData['intensities']
    pyJson['intensities'] = [];
    for (const i in intensitiesObj) {
        pyJson['intensities'].push(intensitiesObj[i])
    }

    var intensitiesObj = jsonData['raman_spec_x']
    pyJson['raman_spec_x'] = [];
    for (const i in intensitiesObj) {
        pyJson['raman_spec_x'].push(intensitiesObj[i])
    }

    return pyJson;
}


function exportToJsonFile(jsonData) {
    let pyJson = parseJSONToPyJSON(jsonData);
    let dataStr = JSON.stringify(pyJson);
    let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    let exportFileDefaultName = 'data.json';
    
    let linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

var jsonData = source.data;
exportToJsonFile(jsonData);