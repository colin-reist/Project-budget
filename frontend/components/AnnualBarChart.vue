<template>
  <div ref="chartContainer" class="w-full" style="min-height: 300px"></div>
</template>

<script setup lang="ts">
import * as d3 from 'd3'

interface MonthData {
  month: string
  income: number
  expense: number
}

const props = defineProps<{
  data: MonthData[]
  currency: string
}>()

const chartContainer = ref<HTMLElement>()

const MONTH_LABELS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

const renderChart = () => {
  if (!chartContainer.value || !props.data.length) return

  d3.select(chartContainer.value).selectAll('*').remove()

  const containerWidth = chartContainer.value.clientWidth
  const margin = { top: 30, right: 20, bottom: 60, left: 70 }
  const width = containerWidth - margin.left - margin.right
  const height = 300 - margin.top - margin.bottom

  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', containerWidth)
    .attr('height', 300)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const months = props.data.map(d => d.month)

  // X0 : mois
  const x0 = d3.scaleBand()
    .domain(months)
    .rangeRound([0, width])
    .paddingInner(0.15)

  // X1 : income / expense
  const x1 = d3.scaleBand()
    .domain(['income', 'expense'])
    .rangeRound([0, x0.bandwidth()])
    .padding(0.08)

  // Y
  const maxVal = d3.max(props.data, d => Math.max(d.income, d.expense)) || 0
  const y = d3.scaleLinear()
    .domain([0, maxVal * 1.1])
    .nice()
    .rangeRound([height, 0])

  // Axe X
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x0).tickFormat((d, i) => MONTH_LABELS[i] ?? d))
    .selectAll('text')
    .style('font-size', '11px')
    .style('fill', 'currentColor')

  // Axe Y
  svg.append('g')
    .call(
      d3.axisLeft(y)
        .ticks(5)
        .tickFormat(d => `${d3.format(',.0f')(d as number)} ${props.currency}`)
    )
    .selectAll('text')
    .style('font-size', '10px')
    .style('fill', 'currentColor')

  // Groupes par mois
  const groups = svg.selectAll('.month-group')
    .data(props.data)
    .enter()
    .append('g')
    .attr('transform', d => `translate(${x0(d.month)},0)`)

  // Barres revenus (bleu)
  groups.append('rect')
    .attr('x', x1('income')!)
    .attr('y', d => y(d.income))
    .attr('width', x1.bandwidth())
    .attr('height', d => Math.max(0, height - y(d.income)))
    .attr('fill', '#3b82f6')
    .attr('rx', 2)

  // Barres dépenses (orange)
  groups.append('rect')
    .attr('x', x1('expense')!)
    .attr('y', d => y(d.expense))
    .attr('width', x1.bandwidth())
    .attr('height', d => Math.max(0, height - y(d.expense)))
    .attr('fill', '#f97316')
    .attr('rx', 2)

  // Légende
  const legend = svg.append('g')
    .attr('transform', `translate(${width / 2 - 80}, -20)`)

  const legendItems = [
    { label: 'Revenus', color: '#3b82f6' },
    { label: 'Dépenses', color: '#f97316' },
  ]

  legendItems.forEach((item, i) => {
    const g = legend.append('g').attr('transform', `translate(${i * 110}, 0)`)
    g.append('rect').attr('width', 12).attr('height', 12).attr('fill', item.color).attr('rx', 2)
    g.append('text').attr('x', 16).attr('y', 10).text(item.label)
      .style('font-size', '11px').style('fill', 'currentColor')
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
