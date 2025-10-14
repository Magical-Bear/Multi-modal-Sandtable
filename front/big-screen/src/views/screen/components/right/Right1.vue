<template>
	<div class="es-block">
		<Title>当前环境温湿度</Title>
		<div class="temp-humi-container">
			<div class="sensor-data" v-for="sensor in sensors" :key="sensor.id">
				<div class="sensor-circle" :style="{ borderColor: sensor.color }">
					<div class="sensor-value">{{ sensor.value }} {{ sensor.unit }}</div>
				</div>
				<p>{{ sensor.label }}</p>
			</div>
		</div>
	</div>
</template>

<script setup lang='ts'>
import { ref, onMounted } from 'vue'
import Title from '../Title.vue'
import mqtt from 'mqtt'

// 温湿度数据和逻辑
const sensors = ref([
	{ id: 1, label: '温度', value: 25.0, unit: '°C', color: '' },
	{ id: 2, label: '湿度', value: 54.0, unit: '%', color: '' }
])

function getColorForTemperature(temp: number) {
	if (temp <= 0) return 'blue'
	else if (temp <= 20) return 'lightblue'
	else if (temp <= 25) return 'yellow'
	else return 'red'
}

function getColorForHumidity(humi: number) {
	if (humi < 30) return 'lightblue'
	else if (humi <= 60) return 'green'
	else return 'blue'
}

// MQTT连接与订阅
onMounted(() => {
	const client = mqtt.connect('ws://192.168.124.10:8083/mqtt')

	client.on('connect', () => {
		console.log('MQTT Connected')

		// 订阅温湿度主题
		client.subscribe('network/temp_info', (err) => {
			if (err) {
				console.error('订阅温度失败', err)
			}
		})
		client.subscribe('network/humi_info', (err) => {
			if (err) {
				console.error('订阅湿度失败', err)
			}
		})
	})

	// 监听温度数据
	client.on('message', (topic, message) => {
		// 去除前缀 '1_'，并转换为数字
		const valueStr = message.toString().replace('1_', '') + '.0'
		const value = parseFloat(valueStr)

		if (topic === 'network/temp_info') {
			sensors.value[0].value = value
			sensors.value[0].color = getColorForTemperature(value)
		} else if (topic === 'network/humi_info') {
			sensors.value[1].value = value
			sensors.value[1].color = getColorForHumidity(value)
		}
	})



	// 断开连接时的处理
	client.on('close', () => {
		console.log('MQTT Connection Closed')
	})
})
</script>

<style lang='scss' scoped>
.es-block {
	width: 100%;
	height: 100%;
	transition: all 0.3s ease;
}

.temp-humi-container {
	display: flex;
	justify-content: space-around;
	align-items: center;
	height: 100%;
}

.sensor-data {
	text-align: center;
}

.sensor-circle {
	width: 100px;
	height: 100px;
	border-radius: 50%;
	border: 5px solid;
	display: flex;
	justify-content: center;
	align-items: center;
	margin-bottom: 10px;
}

.sensor-value {
	font-size: 24px;
	font-weight: bold;
}
</style>
