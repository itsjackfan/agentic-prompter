import { useCallback } from 'react';
import {
  Handle,
  Position,
  useNodesData,
  useHandleConnections,
} from '@xyflow/react';

const ButtonNode = ({ data, isConnectable}) => {
  const promptInput = useHandleConnections({
    type: 'target',
    id: 'pin',
  });
  const promptInputData = useNodesData(promptInput?.[0].source);

  const onClick = () => {
    console.log(promptInputData.data.value)    
  }

  return (
    <div className = "compute-node">
      <Handle
        type="target"
        id="pin"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div>
        <div>{data.label}</div>
        <button onClick={onClick} >Go!</button>
      </div>
      <Handle
        type="source"
        id="a"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );   
};

export default ButtonNode;