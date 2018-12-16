class DataFrame {

  constructor(range) {
    this.range = range;
    // this.values = range.getValues();
    this.values = [ ["Column1","Column2","Column3","Column4"],
                    ["C1R1","C2R1","dup","C4R1"],
                    ["C1R2","C2R2","C3R2","C4R2"],
                    ["C1R3","C2R3","C3R3","C4R3"],
                    ["C1R4","C2R4","dup","C4R4"],
                  ];
    this.initialise();
  }

  initialise() {
    this.columns = this.values[0];
    this.numColumns = this.columns.length;
    this.numRows = this.values.length - 1; // exclude column headers
  }

  has_duplicates(colName) {
    let cidx = this.columns.indexOf(colName);
    if (cidx == -1) {
      throw new Error("Could not find colName " + colName);
    }
    let counts = [];
    for (let i=1; i <= this.numRows; i++) {
      let value = this.values[i][cidx];
      if (counts[value] === undefined) {
        counts[value] = 1;
      } else {
        return true;
      }
    }
    return false;
  } // End has_duplicates

  duplicates(colName) {
    let cidx = this.columns.indexOf(colName);
    if (cidx == -1) {
      throw new Error("Could not find colName " + colName);
    }
    // Find any items that are present more than once
    let counts = [];
    for (let i=1; i <= this.numRows; i++) {
      let value = this.values[i][cidx];
      if (counts[value] === undefined) {
        counts[value] = 1;
      } else {
        counts[value] += 1;
      }
    }
    // Create boolean array indicating duplicates
    var duplicates = new Array(this.numRows).fill(false);;
    for (let i=1; i <= this.numRows; i++) {
      let value = this.values[i][cidx];
      if (counts[value] > 1){
        duplicates[i] = true;
      }
    }
    return duplicates;
  } // End duplicates

} // End Class

df = new DataFrame(null);
// console.log("GOT " + df.values.join("\n"));
console.log(df.duplicates('Column3'));

// if df.has_duplicates('Column1') {
//   console.log("Duplicates for Column 1");
//   duplicates = df.duplicated('Column1');
//   console.log(df.select(duplicates));
// }
