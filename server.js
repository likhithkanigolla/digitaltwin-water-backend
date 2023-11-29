const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 2345;

app.use(express.json());
app.use(cors());

let waterUnitsAtA = Array(10).fill(1); // Initial water units at point A
let waterUnitsAtB = []; // Initial water units at point B

app.post('/startSimulation', (req, res) => {
  res.status(200).json({ message: 'Simulation started' });
});

app.post('/stopSimulation', (req, res) => {
  res.status(200).json({ message: 'Simulation stopped' });
});

app.post('/calculateAmount', (req, res) => {
  const { waterUnitsAtA: unitsAtA } = req.body;
  waterUnitsAtA = unitsAtA;
  waterUnitsAtB = Array(10 - unitsAtA.length).fill(1); // Fill water units at point B accordingly

  res.status(200).json({ waterUnitsAtA, waterUnitsAtB });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
