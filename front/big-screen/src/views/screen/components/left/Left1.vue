<template>
	<div class="es-block">
		<Title>物流配送统计</Title>
		<div ref="chartDom" style="width: 100%; height: 90%;"></div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Title from '../Title.vue'
import allData from '@/assets/data/seller.json'
import * as echarts from 'echarts'

const barWidth = 22
const chartDom = ref(null)
let echartsInstance = null

const option = {
	grid: {
		top: '10%',
		left: '5%',
		right: '10%',
		bottom: '5%',
		containLabel: true
	},
	xAxis: {
		type: 'value',
		splitLine: { show: false },
		axisLine: { show: true }
	},
	yAxis: {
		type: 'category',
		axisTick: { show: false },
		data: [] // 初始为空，稍后动态赋值
	},
	tooltip: {
		trigger: 'axis',
		axisPointer: {
			type: 'line',
			z: 0,
			lineStyle: {
				color: '#2D3443'
			}
		}
	},
	series: [
		{
			type: 'bar',
			label: {
				show: true,
				position: 'right'
			},
			barWidth: barWidth,
			roundCap: true,
			itemStyle: {
				borderWidth: 0,
				borderRadius: [0, barWidth / 2, barWidth / 2, 0],
				color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
					{
						offset: 0,
						color: '#5052EE'
					},
					{
						offset: 1,
						color: '#AB6EE5'
					}
				])
			},
			data: [] // 初始为空，稍后动态赋值
		}
	]
}

// 用于定期更新图表的函数
function updateChart() {
	// 随机选择一组数据
	const randomData = allData
		.sort(() => 0.5 - Math.random())
		.slice(0, 5)

	// 更新 yAxis 和 series 数据
	option.yAxis.data = randomData.map(item => item.name)
	option.series[0].data = randomData.map(item => item.value)

	// 手动更新图表
	echartsInstance.setOption(option)
}

// 在组件挂载时初始化 ECharts 实例并开始更新
onMounted(() => {
	echartsInstance = echarts.init(chartDom.value)
	updateChart() // 初次渲染时更新一次图表
	setInterval(updateChart, 3000) // 每3秒更新一次图表
})
</script>

<style lang="scss" scoped>
.es-block {
	width: 100%;
	height: 100%;
}
</style>
