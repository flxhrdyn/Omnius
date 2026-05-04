/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { NewsAnalysis } from '../types';
import { ZoomIn, ZoomOut, Focus, ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';

interface KeywordGraphProps {
  analyses: NewsAnalysis[];
}

interface Node extends d3.SimulationNodeDatum {
  id: string;
  type: 'source' | 'keyword';
  label: string;
  color: string;
  val: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string | Node;
  target: string | Node;
}

export const KeywordRelationshipGraph: React.FC<KeywordGraphProps> = ({ analyses }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const svgSelectionRef = useRef<d3.Selection<SVGSVGElement, unknown, null, undefined> | null>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = 400;

    // Data Processing
    const nodes: Node[] = [];
    const links: Link[] = [];
    const keywordsMap = new Map<string, { count: number; sources: Set<string> }>();

    // 1. Add Source Nodes
    analyses.forEach((analysis) => {
      nodes.push({
        id: analysis.source,
        type: 'source',
        label: analysis.source,
        color: '#2A35D1',
        val: 12, // Reduced size
      });

      analysis.keywords.forEach((kw) => {
        const existing = keywordsMap.get(kw) || { count: 0, sources: new Set() };
        existing.count += 1;
        existing.sources.add(analysis.source);
        keywordsMap.set(kw, existing);

        links.push({
          source: analysis.source,
          target: kw,
        });
      });
    });

    // 2. Add Keyword Nodes
    keywordsMap.forEach((data, kw) => {
      const isShared = data.sources.size > 1;
      nodes.push({
        id: kw,
        type: 'keyword',
        label: kw,
        color: isShared ? '#10b981' : '#404040',
        val: 4 + data.count * 2, // Reduced size
      });
    });

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    svg.selectAll('*').remove();

    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .extent([[0, 0], [width, height]])
      .scaleExtent([0.2, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);
    zoomRef.current = zoom;
    svgSelectionRef.current = svg;

    // Anchor force layout to 0,0 for easier transform math
    const simulation = d3.forceSimulation<Node>(nodes)
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-150))
      .force('center', d3.forceCenter(0, 0))
      .force('collision', d3.forceCollide<Node>().radius(d => d.val + 10));

    // Set initial transform to center the graph in the view
    const initialTransform = d3.zoomIdentity.translate(width / 2, height / 2).scale(0.9);
    svg.call(zoom.transform, initialTransform);

    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#1A1E26')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 1);

    const node = g.append('g')
      .selectAll('.node')
      .data(nodes)
      .join('g')
      .attr('class', 'node')
      .call(drag(simulation));

    node.append('circle')
      .attr('r', d => d.val)
      .attr('fill', d => d.type === 'source' ? 'transparent' : d.color)
      .attr('stroke', d => d.type === 'source' ? d.color : 'none')
      .attr('stroke-width', 2)
      .attr('filter', d => d.type === 'source' ? 'drop-shadow(0 0 5px #2A35D1)' : 'none');

    // Add background rect for text to make it readable
    node.append('text')
      .attr('dy', d => d.val + 12)
      .attr('text-anchor', 'middle')
      .text(d => d.label)
      .attr('fill', d => d.type === 'source' ? '#fff' : '#606060')
      .attr('font-size', d => d.type === 'source' ? '11px' : '9px')
      .attr('font-weight', d => d.type === 'source' ? 'bold' : 'normal')
      .attr('className', 'font-mono uppercase tracking-tighter');

    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as Node).x!)
        .attr('y1', d => (d.source as Node).y!)
        .attr('x2', d => (d.target as Node).x!)
        .attr('y2', d => (d.target as Node).y!);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    function drag(sim: d3.Simulation<Node, undefined>) {
      function dragstarted(event: d3.D3DragEvent<Element, Node, Node>) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event: d3.D3DragEvent<Element, Node, Node>) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event: d3.D3DragEvent<Element, Node, Node>) {
        if (!event.active) sim.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3.drag<any, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }

    return () => {
      simulation.stop();
    };
  }, [analyses]);

  const handleZoom = (scale: number) => {
    if (svgSelectionRef.current && zoomRef.current) {
      svgSelectionRef.current.transition().duration(300).call(zoomRef.current.scaleBy, scale);
    }
  };

  const handlePan = (dx: number, dy: number) => {
    if (svgSelectionRef.current && zoomRef.current) {
      svgSelectionRef.current.transition().duration(300).call(zoomRef.current.translateBy, dx, dy);
    }
  };

  const handleCenter = () => {
    if (svgSelectionRef.current && zoomRef.current && containerRef.current) {
      const w = containerRef.current.clientWidth;
      svgSelectionRef.current.transition().duration(750).call(
        zoomRef.current.transform, 
        d3.zoomIdentity.translate(w / 2, 200).scale(0.9)
      );
    }
  };

  return (
    <div ref={containerRef} className="w-full bg-[#06080B] rounded-3xl overflow-hidden border border-white/5 relative group">
      <div className="absolute top-4 left-4 z-10 flex gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#2A35D1]" />
          <span className="text-[10px] text-[#606060] font-mono uppercase">Media Source</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#10b981]" />
          <span className="text-[10px] text-[#606060] font-mono uppercase">Shared Narrative</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#404040]" />
          <span className="text-[10px] text-[#606060] font-mono uppercase">Unique Keyword</span>
        </div>
      </div>

      {/* Graph Navigation Controls */}
      <div className="absolute bottom-4 right-4 z-10 flex flex-col items-end gap-2 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity duration-300">
        
        {/* Zoom Controls */}
        <div className="flex flex-col bg-[#0E1117]/80 backdrop-blur-md p-1.5 rounded-xl border border-white/10">
          <button onClick={() => handleZoom(1.3)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ZoomIn className="w-4 h-4" /></button>
          <div className="h-px bg-white/10 mx-1 my-1" />
          <button onClick={() => handleZoom(0.7)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ZoomOut className="w-4 h-4" /></button>
        </div>

        {/* Pan Controls */}
        <div className="grid grid-cols-3 gap-1 bg-[#0E1117]/80 backdrop-blur-md p-1.5 rounded-xl border border-white/10">
          <div />
          <button onClick={() => handlePan(0, 50)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ChevronUp className="w-4 h-4" /></button>
          <div />
          <button onClick={() => handlePan(50, 0)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ChevronLeft className="w-4 h-4" /></button>
          <button onClick={handleCenter} className="w-8 h-8 flex items-center justify-center hover:bg-[#2A35D1]/20 rounded-lg text-[#2A35D1] hover:text-[#3A45E1] transition-colors"><Focus className="w-4 h-4" /></button>
          <button onClick={() => handlePan(-50, 0)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ChevronRight className="w-4 h-4" /></button>
          <div />
          <button onClick={() => handlePan(0, -50)} className="w-8 h-8 flex items-center justify-center hover:bg-white/10 rounded-lg text-[#808080] hover:text-white transition-colors"><ChevronDown className="w-4 h-4" /></button>
          <div />
        </div>
      </div>

      <svg ref={svgRef} className="cursor-grab active:cursor-grabbing w-full" />
    </div>
  );
};
