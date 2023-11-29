const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 2345;

let waterUnitsAtA = Array(10).fill(1);
let waterUnitsAtB = [];
let waterUnitsAtC = [];
let waterUnitsAtD = [];

app.use(bodyParser.json());

app.post('/calculateAmount', (req, res) => {
  const { waterUnitsAtA: unitsAtA } = req.body;
  waterUnitsAtA = unitsAtA;

  // Simulate water flow to tanks B, C, and D
  waterUnitsAtB.push(...unitsAtA.splice(0, Math.min(unitsAtA.length, 1)));
  waterUnitsAtC.push(...unitsAtA.splice(0, Math.min(unitsAtA.length, 1)));
  waterUnitsAtD.push(...unitsAtA.splice(0, Math.min(unitsAtA.length, 1)));

  const calculatedAmountAtA = waterUnitsAtA.length;
  const calculatedAmountAtB = waterUnitsAtB.length;
  const calculatedAmountAtC = waterUnitsAtC.length;
  const calculatedAmountAtD = waterUnitsAtD.length;

  res.json({
    waterUnitsAtA,
    waterUnitsAtB,
    waterUnitsAtC,
    waterUnitsAtD,
    calculatedAmountAtA,
    calculatedAmountAtB,
    calculatedAmountAtC,
    calculatedAmountAtD,
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
