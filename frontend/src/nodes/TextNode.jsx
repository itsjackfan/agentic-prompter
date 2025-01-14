import { useCallback, useState } from 'react';
import { Handle, Position, useReactFlow } from '@xyflow/react';
 
function TextInput({ id, data }) {
  const { updateNodeData } = useReactFlow();
  const [text, setText] = useState(data.value);
 
  const onChange = useCallback((evt) => {
    const text = evt.target.value;
    setText(text);
    updateNodeData(id, { value: text });
  }, []);
 
  return (
    <div className="text-input">
      <div>{data.label}</div>
      <input
        id={`text-${id}`}
        name="text"
        type="text"
        onChange={onChange}
        className="nodrag"
        value={text}
      />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
 
export default TextInput;