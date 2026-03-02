import React, { useEffect, useState, useRef } from "react";
import CytoscapeComponent from 'react-cytoscapejs';
import axios from 'axios';

const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws";

function App(){
  const [elements, setElements] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    // load initial graph
    axios.get("http://localhost:8000/graph/top")
      .then(res => {
        const nodes = res.data.nodes.map(n => ({ data: { id: n.id, label: n.label }}));
        const edges = res.data.edges.map((e, idx) => ({ data: { id: 'e'+idx, source: e.source, target: e.target, label: e.label }}));
        setElements([...nodes, ...edges]);
      }).catch(err => console.error(err));

    // websocket
    const ws = new WebSocket(WS_URL);
    ws.onopen = () => console.log("WS connected");
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if(msg.type === "new_email"){
          const e = msg.data;
          const elNodes = [];
          const elEdges = [];

          const emailId = 'email_' + e.id;
          elNodes.push({ data: { id: emailId, label: e.subject || 'email' }});
          const senderId = 'actor_' + e.from;
          elNodes.push({ data: { id: senderId, label: e.from }});
          elEdges.push({ data: { id: `sent_${e.id}`, source: senderId, target: emailId }});

          (e.to || []).forEach((r, i) => {
            const rid = 'actor_' + r;
            elNodes.push({ data: { id: rid, label: r }});
            elEdges.push({ data: { id: `to_${e.id}_${i}`, source: emailId, target: rid }});
          });

          Object.keys(e.url_domain_map || {}).forEach((u, i) => {
            const uid = 'url_' + btoa(u).slice(0,8) + '_' + i;
            elNodes.push({ data: { id: uid, label: u }});
            elEdges.push({ data: { id: `urlhost_${e.id}_${i}`, source: emailId, target: uid }});
          });

          setElements(prev => {
            const existing = new Set(prev.map(p => p.data.id));
            const toAdd = [...elNodes, ...elEdges].filter(x => !existing.has(x.data.id));
            return [...prev, ...toAdd];
          });
        }
      } catch (err) { console.error(err); }
    }
    wsRef.current = ws;
    return () => { ws.close(); }
  }, []);

  const layout = { name: 'cose', animate: true, fit: true };

  const style = [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'text-valign': 'center',
        'color': '#222',
        'background-color': '#9fd3c7',
        'width': 'label',
        'padding': '6px'
      }
    },
    {
      selector: 'edge',
      style: {
        'label': 'data(label)',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'width': 2,
        'font-size': 8
      }
    }
  ];

  return (
    <div style={{height:"100vh"}}>
      <h3 style={{textAlign:"center"}}>Kill Chain Visualizer - Live</h3>
      <CytoscapeComponent elements={elements} style={{width: '100%', height: '90%'}} stylesheet={style} layout={layout} />
    </div>
  );
}

export default App;
