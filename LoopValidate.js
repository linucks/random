class DataFrame {

  constructor(range) {
    this.range = range;
    // this.values = range.getValues();
    this.data = [ ["Column1","Column2","Column3","Column4"],
                    ["C1R1","C2R1","dup","C4R1"],
                    ["C1R2","C2R2","C3R2","C4R2"],
                    ["C1R3","C2R3","C3R3","C4R3"],
                    ["C1R4","C2R4","dup","C4R4"],
                  ];
    this.initialise();
  }

  initialise() {
    // this.data = this.range.getValues();
    this.data = this.data;
    this.columns = this.data.shift(); // remove column header
    this.numColumns = this.columns.length;
    this.numRows = this.data.length
  }

  duplicates(colName) {
    /* Return the indexes of any duplicate items in column colName */
    let cidx = this.columns.indexOf(colName);
    if (cidx == -1) {
      throw new Error("Could not find colName " + colName);
    }
    let counts = [];
    for (let i=0; i < this.numRows; i++) {
      let value = this.data[i][cidx];
      if (counts[value] === undefined) {
        counts[value] = 1;
      } else {
        counts[value] += 1;
      }
    }
    var duplicates = [];
    for (let i=0; i < this.numRows; i++) {
      let value = this.data[i][cidx];
      if (counts[value] > 1){
        duplicates.push(i);
      }
    }
    return duplicates;
  } // End duplicates

  select(rows, columns){
    /* Select data based on indexes of rows and column names */
    if (columns === undefined) {
      columns = this.columns;
    }
    var column_idxs = [];
    var idx;
    for (let i=0; i < columns.length; i++) {
      idx = this.columns.indexOf(columns[i]);
      if (idx == -1) {
        throw new Error("Cannot find column: " + columns[i]);
      }
      column_idxs.push(idx);
    }
    var getData = function(idx) {
      return column_idxs.map(cidx => this.data[idx][cidx]);
    }
    return rows.map(getData.bind(this));;
  } //End select

} // End Class

df = new DataFrame(null);
console.log(df.duplicates('Column3'));
console.log(df.select([1, 3], ['Column2', 'Column3']));


/*
var ss = SpreadsheetApp.getActive()
var catalog = DataFrame(ss.getRange('Catalog!A:R'));
var duplicates = catalog.duplicates('Sample Number');
if (duplicates.length) {
  var data = catalog.select(duplicates,
                            ['Sample Number', 'Your name and surname initial']);
  console.log("Got duplicates: " + data.join('\n'));
}
*/
 // var cells = ss.getRange('Catalog!A:R')
 // var sheet = s.getSheetByName('Catalog')
 // SpreadsheetApp.getUi().alert('Got data ' + ss.getRange('Catalog!A:R').getValues().join("\n"));
