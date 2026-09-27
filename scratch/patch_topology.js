const fs = require('fs');

// 1. Patch TopologyPage.tsx
let pageCode = fs.readFileSync('web/src/features/topology/TopologyPage.tsx', 'utf-8');
pageCode = pageCode.replace(
  `<span>Simulated Event Trace Log</span>`,
  `<span>Live Event Trace Log</span>`
);
pageCode = pageCode.replace(
  `No active event trace. Click "Trigger Real Flow" above to simulate an end-to-end multi-step flow execution.`,
  `No active event trace. Click "Trigger Real Flow" above to execute an end-to-end multi-step flow.`
);
fs.writeFileSync('web/src/features/topology/TopologyPage.tsx', pageCode);

// 2. Patch TopologyCanvas3D.tsx
let canvasCode = fs.readFileSync('web/src/features/topology/TopologyCanvas3D.tsx', 'utf-8');
// Increase camera distance to show all nodes
canvasCode = canvasCode.replace(
  `camera={{ position: [0, 8, 18], fov: 50 }}`,
  `camera={{ position: [0, 16, 26], fov: 55 }}`
);
fs.writeFileSync('web/src/features/topology/TopologyCanvas3D.tsx', canvasCode);
