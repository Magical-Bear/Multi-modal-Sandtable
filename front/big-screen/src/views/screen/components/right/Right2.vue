<template>
	<div class="es-block">
		<Title>交通灯监控面板</Title>
		<div class="traffic-lights-container">
			<div v-for="light in trafficLights" :key="light.id" class="traffic-light">
				<div class="light-circle">
					<svg viewBox="0 0 36 36" class="circular-chart" :style="{ stroke: light.color }">
						<path class="circle-bg"
									d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
						/>
						<path class="circle"
									:stroke-dasharray="light.timeLeft + ', 100'"
									d="M18 2.0845
                        a 15.9155 15.9155 0 0 1 0 31.831
                        a 15.9155 15.9155 0 0 1 0 -31.831"
						/>
					</svg>
					<div class="time-text">
						<p>{{ light.timeLeft >= 0 ? light.timeLeft + ' 秒' : '结束' }}</p>
					</div>
				</div>
				<p>交通灯 {{ light.id }}</p>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
import Title from '../Title.vue';
import mqtt from 'mqtt';

// 定义颜色顺序
const colorSequence = ['red', 'green', 'yellow'];

// 初始化5个交通灯的数据，默认设置为绿灯 60 秒
const trafficLights = ref([
	{ id: 0, color: 'green', timeLeft: 60 },
	{ id: 1, color: 'green', timeLeft: 60 },
	{ id: 2, color: 'green', timeLeft: 60 },
	{ id: 3, color: 'green', timeLeft: 60 },
	{ id: 4, color: 'green', timeLeft: 60 },
]);

let mqttClient: mqtt.MqttClient | undefined;

// MQTT连接与订阅
onMounted(() => {
	// 连接到 MQTT 服务器
	mqttClient = mqtt.connect('ws://192.168.124.10:8083/mqtt');

	mqttClient.on('connect', () => {
		console.log('MQTT Connected');
		mqttClient?.subscribe('network/traffic_info', (err) => {
			if (err) {
				console.error('订阅失败', err);
			}
		});
	});

	// 监听 MQTT 消息
	mqttClient?.on('message', (topic, message) => {
		if (topic === 'network/traffic_info') {
			const data = message.toString().split('_');
			if (data.length === 3) {
				const lightId = parseInt(data[0], 10);
				const colorIndex = parseInt(data[1], 10);
				const timeLeft = parseInt(data[2], 10);

				// 更新对应交通灯的状态
				if (trafficLights.value[lightId]) {
					const color = colorSequence[colorIndex];
					trafficLights.value[lightId].color = color;
					trafficLights.value[lightId].timeLeft = timeLeft;
				}
			}
		}
	});

	// 默认倒计时功能（未接收到 MQTT 数据时减少 timeLeft）
	setInterval(() => {
		for (const light of trafficLights.value) {
			if (light.timeLeft > 0) {
				light.timeLeft--;
			} else {
				// 切换到下一颜色
				const currentIndex = colorSequence.indexOf(light.color);
				const nextIndex = (currentIndex + 1) % colorSequence.length;
				light.color = colorSequence[nextIndex];
				light.timeLeft = nextIndex === 0 ? 20 : nextIndex === 1 ? 60 : 5; // 红20，绿60，黄5
			}
		}
	}, 1000);
});

// 清理
onBeforeUnmount(() => {
	if (mqttClient) {
		mqttClient.end();
	}
});
</script>


<style lang="scss" scoped>
.es-block {
	width: 100%;
	height: 100%;
}

.traffic-lights-container {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 20px;
	justify-items: center;
}

.traffic-light {
	text-align: center;
}

.light-circle {
	width: 100px;
	height: 100px;
	display: flex;
	justify-content: center;
	align-items: center;
	margin: 0 auto 10px;
	position: relative;
}

.circular-chart {
	width: 100px;
	height: 100px;
	transform: rotate(-90deg);
}

.circle-bg {
	fill: none;
	stroke: #363636;
	stroke-width: 3.8;
}

.circle {
	fill: none;
	stroke-width: 3.8;
	stroke-linecap: round;
	transition: stroke-dasharray 0.3s;
}

.time-text {
	position: absolute;
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 18px;
	font-weight: bold;
	color: inherit;
}
</style>
