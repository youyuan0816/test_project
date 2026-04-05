import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface PieChartProps {
  data: { type: string; value: number }[];
  width?: number;
  height?: number;
}

const COLORS = ['#52c41a', '#ff4d4f', '#faad14'];

export function PieChart({ data, width = 400, height = 300 }: PieChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || data.length === 0) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const radius = Math.min(width, height) / 2 - 40;

    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    const pie = d3.pie<{ type: string; value: number }>()
      .value(d => d.value)
      .sort(null);

    const arc = d3.arc<d3.PieArcDatum<{ type: string; value: number }>>()
      .innerRadius(radius * 0.5)
      .outerRadius(radius);

    const labelArc = d3.arc<d3.PieArcDatum<{ type: string; value: number }>>()
      .innerRadius(radius * 0.8)
      .outerRadius(radius * 0.8);

    // Draw arcs
    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter()
      .append('g')
      .attr('class', 'arc');

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (_, i) => COLORS[i] || '#999')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Draw labels
    arcs.append('text')
      .attr('transform', d => `translate(${labelArc.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .attr('font-size', 14)
      .attr('font-weight', 'bold')
      .text(d => d.data.value > 0 ? `${d.data.type}: ${d.data.value}` : '');

    // Draw legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 100}, 20)`);

    data.forEach((item, i) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${i * 20})`);

      legendRow.append('rect')
        .attr('width', 14)
        .attr('height', 14)
        .attr('fill', COLORS[i] || '#999')
        .attr('rx', 2);

      legendRow.append('text')
        .attr('x', 20)
        .attr('y', 12)
        .attr('font-size', 12)
        .text(item.type);
    });

  }, [data, width, height]);

  return <svg ref={svgRef} />;
}
