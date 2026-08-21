import { useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

export interface Stage {
  id: string;
  type: string;
  connector: string;
  depends_on?: string[];
  [key: string]: unknown;
}

export interface Pipeline {
  name: string;
  stages: Stage[];
}

interface CanvasProps {
  pipeline: Pipeline | null;
}

const stageColors: Record<string, string> = {
  collect: "#e3f2fd",
  clean: "#fff3e0",
  transform: "#f3e5f5",
  load: "#e8f5e9",
  analyze: "#fce4ec",
  report: "#fffde7",
};

function StageNode({ data }: { data: Stage }) {
  return (
    <div
      style={{
        padding: "10px 16px",
        borderRadius: 8,
        border: "1px solid #bdbdbd",
        background: stageColors[data.type] || "#ffffff",
        minWidth: 140,
        textAlign: "center",
      }}
    >
      <Handle type="target" position={Position.Left} />
      <div style={{ fontWeight: 600, fontSize: 14 }}>{data.id}</div>
      <div style={{ fontSize: 12, color: "#616161" }}>{data.connector}</div>
      <div
        style={{
          fontSize: 10,
          textTransform: "uppercase",
          color: "#9e9e9e",
          marginTop: 4,
        }}
      >
        {data.type}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = { stage: StageNode };

export default function Canvas({ pipeline }: CanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node<Stage>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    if (!pipeline || !pipeline.stages) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const newNodes: Node<Stage>[] = pipeline.stages.map((stage, index) => ({
      id: stage.id,
      type: "stage",
      position: { x: index * 220 + 24, y: 100 + (index % 2) * 80 },
      data: stage,
    }));

    const newEdges: Edge[] = [];
    pipeline.stages.forEach((stage) => {
      (stage.depends_on || []).forEach((depId) => {
        newEdges.push({
          id: `${depId}-${stage.id}`,
          source: depId,
          target: stage.id,
          animated: true,
        });
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [pipeline, setNodes, setEdges]);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}
