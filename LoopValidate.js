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
  var catalog = DataFrame(ss.getRange('Catalog!A:R'));
  var duplicates = catalog.duplicates('Sample Number');
  if (duplicates.length) {
    var data = catalog.select(duplicates,
                              ['Sample Number', 'Your name and surname initial']);
    SpreadsheetApp.getUi().alert("Got duplicates: " + data.join('\n'));
  }
}

var DataFrame = function(range){
  this.range = range;
  // this.values = range.getValues();
 this.data = [ ["Column1","Column2","Column3","Column4"],
                 ["C1R1","C2R1","dup","C4R1"],
                 ["C1R2","C2R2","C3R2","C4R2"],
                 ["C1R3","C2R3","C3R3","C4R3"],
                 ["C1R4","C2R4","dup","C4R4"],
               ];

  this.columns = this.data.shift(); // remove column header
  this.numColumns = this.columns.length;
  this.numRows = this.data.length

  this.duplicates = function(colName) {
    /* Return the indexes of any duplicate items in column colName */
    var cidx = this.columns.indexOf(colName);
    if (cidx == -1) {
      throw new Error("Could not find colName " + colName);
    }
    var counts = [];
    for (var i=0; i < this.numRows; i++) {
      var value = this.data[i][cidx];
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

  this.select = function(rows, columns){
    /* Select data based on indexes of rows and column names */
    if (columns === undefined) {
      columns = this.columns;
    }
    var column_idxs = [];
    var idx;
    for (var i=0; i < columns.length; i++) {
      idx = this.columns.indexOf(columns[i]);
      if (idx == -1) {
        throw new Error("Cannot find column: " + columns[i]);
      }
      column_idxs.push(idx);
    }

    var getRows = function(idx) {
      var row = this.data[idx];
      return column_idxs.map(function(idx){return row[idx]});
    }

    return rows.map(getRows.bind(this));
  } //End select

} // End Class


df = new DataFrame(null);
// console.log(df.duplicates('Column3'));
console.log(df.select([1, 3], ['Column1', 'Column3']));
