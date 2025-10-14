<template>
	<SeamlessScroll class="es-center-bottom">
		<div v-for="(item, index) in actions" :key="index" class="es-bottom-item">
			<div :style="{ color: item.color }" class="es-item-text">
				姓名：{{ item.name }}
			</div>
			<div :style="{ color: item.color }" class="es-item-college">
				学院：{{ item.college }}
			</div>
			<div :style="{ color: item.color }" class="es-item-major">
				专业：{{ item.major }}
			</div>
			<div :style="{ color: item.color }" class="es-item-status">
				状态：{{ item.status }}
			</div>
		</div>
	</SeamlessScroll>
</template>

<script setup lang='ts'>
import { ref, onMounted } from 'vue'
import SeamlessScroll from '@/components/SeamlessScroll.vue'

// 学院和专业对应关系
const collegeMajorMap = {
	'电子学院': ['物联网', '电子信息', '通讯工程', '智能科学'],
	'计软学院': ['软件工程', '网络工程', '计算机类', '人工智能'],
	'财务学院': ['财务管理', '会计学', '金融学', '经济学'],
	'艺术学院': ['美术', '音乐', '舞蹈', '编导'],
	'建筑学院': ['建筑学', '土木工程', '工程造价', '工程管理']
}

const actions = ref([
	{ color: 'rgb(24, 144, 255)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(255, 192, 105)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(92, 219, 211)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(179, 127, 235)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(255, 133, 192)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(255, 214, 102)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(24, 144, 255)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(255, 192, 105)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(92, 219, 211)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(179, 127, 235)', name: '', college: '', major: '', status: '' },
	{ color: 'rgb(255, 133, 192)', name: '', college: '', major: '', status: '' },
])

const studentNames = ['小明', '小红', '小刚', '小丽', '小芳', '小军', '小霞', '小燕', '小强', '小杰', '小玉']
const statuses = ['运输中', '已送达', '待处理', '已取消', '处理中']

onMounted(() => {
	actions.value.forEach(item => {
		item.name = studentNames[Math.floor(Math.random() * studentNames.length)]
		// 随机选择一个学院
		item.college = Object.keys(collegeMajorMap)[Math.floor(Math.random() * Object.keys(collegeMajorMap).length)]
		// 根据学院选择对应的专业
		item.major = collegeMajorMap[item.college][Math.floor(Math.random() * collegeMajorMap[item.college].length)]
		item.status = statuses[Math.floor(Math.random() * statuses.length)]
	})
})
</script>

<style lang='scss' scoped>
.es-center-bottom {
	position: relative;
	width: 100%;
	overflow: hidden;
	height: 150px;

	.es-bottom-item {
		position: absolute;
		top: 0;
		left: 0;
		width: 200px;
		height: 200px;
		display: flex;
		flex-direction: column;
		justify-content: start;
		align-items: center;
		background-color: var(--es-block-bg);
		font-size: 22px;
		font-weight: 600;

		.es-item-text {
			margin-top: 16px;
		}

		.es-item-college, .es-item-major, .es-item-status {
			margin-top: 8px;
			font-size: 18px;
		}
	}
}
</style>
