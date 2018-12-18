function onOpen() {
  var ui = SpreadsheetApp.getUi();
  // Or DocumentApp or FormApp.
  ui.createMenu('Loop Menu')
      .addItem('Validate Data', 'validateData')
      .addToUi();
}

function validateData() {
  //var sheet = s.getSheetByName('Catalog')
  var ss = SpreadsheetApp.getActive()
  var catalog = new DataFrame(ss.getRange('Catalog!A:R'));
  var duplicates = catalog.duplicates('Sample Number');
  if (duplicates.length) {
    var data = catalog.select(duplicates,
                              ['Sample Number', 'Your name and first initial']);
    SpreadsheetApp.getUi().alert("Got duplicates:\n" + data.join('\n'));
  }
}

var DataFrame = function(range){
  this.range = range;
  this.data = [];

  if (false) {
    // Prune empty rows
    var values = range.getValues();
    var rowlen = 0;
    for (var i=0; i < values.length; i++) {
      rowlen = values[i].reduce(function(acc, val){return val.hasOwnProperty('length') ? acc + val.length : acc + 1}, 0);
      if (rowlen > 0) {this.data.push(values[i])};
    }
  } else {
    this.data = [ ["Column1","Column2","Column3","Column4"],
                    ["C1R1","C2R1","dup","C4R1"],
                    ["C1R2","C2R2","C3R2","C4R2"],
                    ["C1R3","C2R3","C3R3","C4R3"],
                    ["C1R4","C2R4","dup","C4R4"]];
    }

  this.columns = this.data.shift(); // remove column header
  this.numColumns = this.columns.length;
  this.numRows = this.data.length

  /* Return the indexes of any duplicate items in column colName */
  this.duplicates = function(colName) {
    var cidx = this.columns.indexOf(colName);
    if (cidx == -1) {
      throw new Error("Could not find colName " + colName);
    }
    var counts = [];
    for (var i=0; i < this.numRows; i++) {
      var value = this.data[i][cidx];
      // Ignore empty strings
      if (value === undefined || (typeof value == 'string' && value.length == 0)) {continue};
      if (counts[value] === undefined) {
        counts[value] = 1;
      } else {
        counts[value] += 1;
      }
    }
    var duplicates = [];
    for (var i=0; i < this.numRows; i++) {
      var value = this.data[i][cidx];
      if (counts[value] > 1){
        duplicates.push(i);
      }
    }
    return duplicates;
  } // End duplicates

  /* Select data based on indexes of rows and column names */
  this.select = function(row_idxs, columns){
    if (columns === undefined) {
      columns = this.columns;
    }
    // Determine which columns we are returning
    var idx, column_idxs = [];
    for (var i=0; i < columns.length; i++) {
      idx = this.columns.indexOf(columns[i]);
      if (idx == -1) {
        throw new Error("Cannot find column: " + columns[i]);
      }
      column_idxs.push(idx);
    }
    return this.get_rows_and_columns(row_idxs,column_idxs);
  } //End select

  this.get_rows_and_columns = function (row_idxs, column_idxs){
    var selected = [];
    for (var i=0; i < this.data.length; i++) {
      if (row_idxs.indexOf(i) == -1) {continue};
      var row = [];
      for (var j=0; j < this.data[i].length; j++) {
        if (column_idxs.indexOf(j) != -1 ) {
          row.push(this.data[i][j]);
        }
      }
      selected.push(row);
    }
    return selected;
  } // End get_rows_and_columns

} // End Class


var df = new DataFrame(null);
// console.log(df.duplicates('Column3'));
console.log(df.select([1, 3], ['Column1', 'Column3']));
