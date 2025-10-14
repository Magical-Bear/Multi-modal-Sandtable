<template>
	<div class="es-block">
		<Title>快递数量接受趋势</Title>
		<div style="width: 100%;height: 90%;">
			<Chart :option="option" />
		</div>
	</div>
</template>

<script setup lang='ts'>
import { ref, onMounted, onUnmounted } from 'vue'
import Title from '../Title.vue'
import Chart from '@/components/chart/Chart.vue'
import allData from '@/assets/data/trend.json'
import * as echarts from 'echarts'

const choiceTypes = ['map', 'seller', 'commodity']
let currentIndex = 0
const option = ref(getOption(choiceTypes[currentIndex]))

function getOption(type: string) {
	return {
		grid: {
			left: '3%',
			top: '25%',
			right: '4%',
			bottom: '1%',
			containLabel: true
		},
		tooltip: {
			trigger: 'axis'
		},
		legend: {
			left: 20,
			top: '8%',
			icon: 'circle',
			data: allData[type].data,
			textStyle: {
				color: '#aaa'
			}
		},
		xAxis: {
			type: 'category',
			boundaryGap: false,
			data: allData.common.month
		},
		yAxis: {
			type: 'value'
		},
		series: getSeries(type)
	}
}

function getSeries(type: string) {
	const colorArr1 = [
		'rgba(11, 168, 44, 0.5)',
		'rgba(44, 110, 255, 0.5)',
		'rgba(22, 242, 217, 0.5)',
		'rgba(254, 33, 30, 0.5)',
		'rgba(250, 105, 0, 0.5)'
	]
	const colorArr2 = [
		'rgba(11, 168, 44, 0)',
		'rgba(44, 110, 255, 0)',
		'rgba(22, 242, 217, 0)',
		'rgba(254, 33, 30, 0)',
		'rgba(250, 105, 0, 0)'
	]
	const valueArr = allData[type].data
	return valueArr.map((item, index) => {
		return {
			name: item.name,
			type: 'line',
			data: item.data,
			stack: type,
			itemStyle: {
				borderWidth: 4
			},
			lineStyle: {
				width: 3
			},
			symbolSize: 0,
			symbol: 'circle',
			smooth: true,
			areaStyle: {
				color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
					{
						offset: 0,
						color: colorArr1[index]
					},
					{
						offset: 1,
						color: colorArr2[index]
					}
				])
			}
		}
	})
}

// Automatically switch categories
onMounted(() => {
	const interval = setInterval(() => {
		currentIndex = (currentIndex + 1) % choiceTypes.length
		option.value = getOption(choiceTypes[currentIndex])
	}, 5000) // Switch every 5 seconds

	onUnmounted(() => {
		clearInterval(interval)
	})
})
</script>

<style lang='scss' scoped>
.es-block {
	width: 100%;
	height: 100%;
}
</style>
