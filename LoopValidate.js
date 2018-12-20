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

  var catalog = new DataFrame(ss.getRange('Catalog!A:R').getValues(), 'Sample Number', 'catalog');
  var ftir = new DataFrame(ss.getRange('FTIR!A:X').getValues(), 'Sample Number', 'ftir');
  var reagent = new DataFrame(ss.getRange('Reagent!A:W').getValues(), 'Sample Number', 'reagent');
  var mla = new DataFrame(ss.getRange('MLA!A:R').getValues(), 'Sample Number', 'mla');
  var hr = new DataFrame(ss.getRange('Interventions!A:BJ').getValues(), 'Sample Number', 'hr');

  var dataframes = [catalog, ftir, reagent, mla, hr];
  var duplicates, data, ret="";
  for (d in dataframes) {
    duplicates = dataframes[d].duplicates('Sample Number');
    if (duplicates.length) {
      data = dataframes[d].select(duplicates, ['Sample Number', 'Your name and first initial']);
      ret += "Got duplicates for sheet[" + d.name +"]\n" + data.join('\n') + "\n";
    }
  }
  if (ret.length) {
    SpreadsheetApp.getUi().alert(ret);
  }
}

var DataFrame = function(values, key, name){

  this.init = function(values, key, name){
      if (name === undefined) {
        this.name = 'dataframe';
      } else {
        this.name = name;
      }
      if (key === undefined) {
        throw new Error("Need db key!");
      }
      this.data = [];

      // Prune empty rows and set key
      var rowlen = 0;
      for (var i=0; i < values.length; i++) {
        rowlen = values[i].reduce(function(acc, val){return val.hasOwnProperty('length') ? acc + val.length : acc + 1}, 0);
        if (rowlen > 0) {this.data.push(values[i])};
      }

      this.columns = this.data.shift(); // remove column header
      this.numColumns = this.columns.length;
      this.numRows = this.data.length;

      // set index - will ignore duplicates
      var keyidx = this.column_indexes(key)[0];
      this.index = {};
      for (var i=0; i < this.data.length; i++) {
        var keyv = this.data[i][keyidx];
        this.index[keyv] = i;
      }
  }

  /* Get the indexes of the supplied columns */
  this.column_indexes = function(columns) {
    if (!(columns instanceof Array)) {
      columns = [columns];
    }
    var idx, column_idxs = [];
    for (var i=0; i < columns.length; i++) {
      idx = this.columns.indexOf(columns[i]);
      if (idx == -1) {
        throw new Error("Cannot find column: " + columns[i]);
      }
      column_idxs.push(idx);
    }
    return column_idxs;
  }

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
    if (!(row_idxs instanceof Array)) {
      row_idxs = [row_idxs];
    }
    if (columns === undefined) {
      columns = this.columns;
    } else if (typeof columns === 'string' || columns instanceof String) {
      columns = [columns];
    }
    return this.get_rows_and_columns(row_idxs, columns);
  } //End select

  this.get_rows_and_columns = function (row_idxs, columns){
    var column_idxs = this.column_indexes(columns);
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

  /* Find rows where identically labelled columns with the same index have different values */
  this.column_difference = function(d2, column) {
    var idx1, idx2, val1, val2, differences=[];
    for (var key in this.index) {
      if (key in d2.index) {
        val1 = this.select(this.index[key], column)[0][0];
        val2 = d2.select(d2.index[key], column)[0][0];
        if (val1 != val2) {
          differences.push([key, val1, val2]);
        }
      }
    }
    return differences;
  }

  this.init(values, key, name);

} // End Class


function column_differences(dataframes, columns){
  var d1 = dataframes[0];
  for (var i=1; i < dataframes.length; i++) {
    d2 = dataframes[i];
    for (var j=0; j < columns.length; j++) {
      column = columns[j];
      var differences = d1.column_difference(d2, column);
      if (differences.length) {
        for (var k=0; k < differences.length; k++) {
          console.log("Got differences: " + d1.name + ":" + d2.name + "   [" + column + "] \"" + differences[k][0] + "\" -> \"" + differences[k][1] + "\"")
        }
      }
    }
    d1 = d2;
  }
}

var values1 = [ ["Index","Column2","Column3","Column4"],
                ["I1","X2R1","dup","C4R1"],
                ["I2","C2R2","C3R2","C4R2"],
                ["I3","C2R3","C3R3","C4R3"],
                ["I4","X2R4","dup","C4R4"]];

var values2 = [ ["Index","Column2","Column3","Column4"],
                ["I1","C2R1","dup","C4R1"],
                ["I2","C2R2","C3R2","C4R2"],
                ["I3","C2R3","C3R3","C4R3"],
                ["I4","C2R4","dup","C4R4"]];

var df1 = new DataFrame(values1, 'Index');
// console.log(df.duplicates('Column3'));
// console.log(df1.select([1, 3], ['Column2', 'Column3']));
var df2 = new DataFrame(values2, 'Index', 'd2');

console.log(column_differences([df1, df2, df1],['Column2']));
// console.log(df1.column_difference(df2, 'Column2'));
