<template>
	<div class="es-block">
		<Title>快递类型占比</Title>
		<div style="width: 100%; height: 90%;">
			<Chart :option="option" />
		</div>
	</div>
</template>

<script setup lang='ts'>
import { ref, onMounted, onUnmounted } from 'vue'
import Title from '../Title.vue'
import Chart from '@/components/chart/Chart.vue'
import allData from '@/assets/data/hot.json'

const currentIndex = ref(0)

const updateOption = () => {
	option.value = {
		grid: {
			containLabel: false,
		},
		legend: {
			bottom: '0%',
			icon: 'circle',
			data: allData[currentIndex.value].children.map(item => item.name),
			textStyle: {
				color: '#aaa'
			}
		},
		tooltip: {
			show: true,
			formatter: arg => {
				const thirdCategory = arg.data.children
				let total = thirdCategory.reduce((sum, item) => sum + item.value, 0)
				let retStr = ''
				thirdCategory.forEach(item => {
					retStr += `${item.name}: ${(item.value / total * 100).toFixed(2)}%<br/>`
				})
				return retStr
			}
		},
		series: [
			{
				type: 'pie',
				label: {
					show: false
				},
				emphasis: {
					label: {
						show: true
					},
					labelLine: {
						show: false
					}
				},
				data: allData[currentIndex.value].children.map(item => ({
					name: item.name,
					value: item.value,
					children: item.children
				}))
			}
		]
	}
}

// Initial option setup
const option = ref({})
updateOption()

const autoSwitchCategory = () => {
	setInterval(() => {
		currentIndex.value = (currentIndex.value + 1) % allData.length
		updateOption()
	}, 3000) // Switch every 3 seconds (adjust as needed)
}

onMounted(() => {
	autoSwitchCategory()
})

onUnmounted(() => {
	clearInterval(autoSwitchCategory)
})

</script>

<style lang='scss' scoped>
.es-block {
	width: 100%;
	height: 100%;
}
</style>
