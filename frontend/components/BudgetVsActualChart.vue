<template>
  <div ref="chartContainer" class="w-full" style="min-height: 250px"></div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'

interface CategoryData {
  category_name: string
  category_color: string
  prevu: number
  reel: number
  ecart: number
  is_over: boolean
  unbudgeted?: boolean
}

const props = defineProps<{
  data: CategoryData[]
}>()

const chartContainer = ref<HTMLElement>()

const renderChart = () => {
  if (!chartContainer.value || !props.data.length) return

  // Nettoyage
  d3.select(chartContainer.value).selectAll('*').remove()

  const containerWidth = chartContainer.value.clientWidth
  const margin = { top: 20, right: 20, bottom: 80, left: 60 }
  const width = containerWidth - margin.left - margin.right
  const height = 250 - margin.top - margin.bottom

  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', containerWidth)
    .attr('height', 250)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const categories = props.data.map(d => d.category_name)

  // Échelle X
  const x0 = d3.scaleBand()
    .domain(categories)
    .rangeRound([0, width])
    .paddingInner(0.2)

  const x1 = d3.scaleBand()
    .domain(['prevu', 'reel'])
    .rangeRound([0, x0.bandwidth()])
    .padding(0.1)

  // Échelle Y
  const maxVal = d3.max(props.data, d => Math.max(d.prevu, d.reel)) || 0
  const y = d3.scaleLinear()
    .domain([0, maxVal * 1.1])
    .nice()
    .rangeRound([height, 0])

  // Axe X
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x0))
    .selectAll('text')
    .attr('transform', 'rotate(-30)')
    .style('text-anchor', 'end')
    .style('font-size', '11px')
    .style('fill', 'currentColor')

  // Axe Y
  svg.append('g')
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => `${d} CHF`))
    .selectAll('text')
    .style('font-size', '11px')
    .style('fill', 'currentColor')

  // Motif de hachures pour les dépassements (accessibilité daltonisme)
  const defs = svg.append('defs')
  const pattern = defs.append('pattern')
    .attr('id', 'over-budget-pattern')
    .attr('patternUnits', 'userSpaceOnUse')
    .attr('width', 6)
    .attr('height', 6)
  pattern.append('rect').attr('width', 6).attr('height', 6).attr('fill', '#ef4444')
  pattern.append('path')
    .attr('d', 'M0,6 L6,0')
    .attr('stroke', '#fff')
    .attr('stroke-width', 1.5)
    .attr('opacity', 0.4)

  // Barres groupées
  const groups = svg.selectAll('.category-group')
    .data(props.data)
    .enter()
    .append('g')
    .attr('transform', d => `translate(${x0(d.category_name)},0)`)

  // Barre Prévu (bleu)
  groups.append('rect')
    .attr('x', x1('prevu')!)
    .attr('y', d => y(d.prevu))
    .attr('width', x1.bandwidth())
    .attr('height', d => height - y(d.prevu))
    .attr('fill', '#3b82f6')
    .attr('rx', 2)

  // Barre Réel (vert si OK, hachures rouges si dépassement)
  groups.append('rect')
    .attr('x', x1('reel')!)
    .attr('y', d => y(d.reel))
    .attr('width', x1.bandwidth())
    .attr('height', d => height - y(d.reel))
    .attr('fill', d => d.is_over ? 'url(#over-budget-pattern)' : '#22c55e')
    .attr('rx', 2)

  // Légende
  const legend = svg.append('g')
    .attr('transform', `translate(${width - 150}, -10)`)

  const legendItems = [
    { label: 'Prévu', color: '#3b82f6' },
    { label: 'Réel', color: '#22c55e' },
    { label: 'Dépassement', color: '#ef4444', fill: 'url(#over-budget-pattern)' },
  ]

  legendItems.forEach((item, i) => {
    const g = legend.append('g').attr('transform', `translate(${i * 90}, 0)`)
    g.append('rect').attr('width', 10).attr('height', 10).attr('fill', item.fill || item.color).attr('rx', 2)
    g.append('text').attr('x', 14).attr('y', 9).text(item.label)
      .style('font-size', '10px').style('fill', 'currentColor')
  })
}

watch(() => props.data, () => renderChart(), { deep: true })

onMounted(() => {
  renderChart()
  window.addEventListener('resize', renderChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', renderChart)
})
</script>
