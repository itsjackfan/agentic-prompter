import { 
  ReactFlow, 
  Background, 
  Controls, 
  applyEdgeChanges, 
  applyNodeChanges,
  addEdge
} from '@xyflow/react';
import { useState, useCallback } from 'react';
import '@xyflow/react/dist/style.css';
import TextInput from "./nodes/TextNode"
import ButtonNode from "./nodes/ButtonNode"

const initialNodes = [
  {
    id: 'prompt-input',
    position: { x: 0, y:0},
    data: {label: 'Input your prompt here:', value: ''},
    type: 'in'
  },
  {
    id: 'compute-prompt',
    position: {x: 100, y: 100},
    data: { label: 'Agentify prompt by clicking this button' },
    type: 'compute'
  }
];

const nodeTypes = { 
  in: TextInput,
  compute: ButtonNode
}

const initialEdges = [
  {
    id: 'prompt-compute',
    source: 'prompt-input',
    target: 'compute-prompt',
    targetHandle: 'pin'
  },
];

function Flow() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [],
  );

 

  return (
    <div style={{ height: '100%' }}>
      <ReactFlow
        nodes = {nodes}
        onNodesChange = {onNodesChange}
        edges = {edges}
        onEdgesChange = {onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default Flow;
