<template>
	<div>
		<Title />
		<div ref="chartContainer" style="width: 100%; height: 900px;"></div>
	</div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { useScreenStore } from '@/store';
import Title from '../Title.vue';
import * as echarts from 'echarts';
import chengduJson from '@/assets/data/cd.json';
import piduJson from '@/assets/data/pidu.json';

// 注册地图数据
echarts.registerMap('cd', chengduJson as any);
echarts.registerMap('pidu', piduJson as any);

const store = useScreenStore();
const currentMap = ref('cd');
const chartInstance = ref<echarts.ECharts | null>(null);
const chartContainer = ref<HTMLElement | null>(null);

let refreshInterval: NodeJS.Timeout | null = null;

// 获取动态配置
const getOption = (mapName, theme) => {
	if (mapName === 'cdjc') {
		return {
			graphic: [
				{
					type: 'group',
					id: 'cdjc-stream',
					left: 'center', // 水平方向居中
					top: '100px', // 调整 MJPEG 流位置
					children: [
						{
							type: 'image',
							id: 'mjpeg-stream',
							style: {
								image: 'http://127.0.0.1:5200', // 替换为实际的 MJPEG 流地址
								width: 800,
								height: 700,
							},
						},
					],
				},
			],
			geo: null, // 清空 geo 配置
			series: [], // 清空地图系列数据
		};
	}
	return {
		geo: {
			type: 'map',
			map: mapName,
			top: '5%',
			bottom: '5%',
			itemStyle: {
				areaColor: theme === 'dark' ? '#2E3A59' : '#000',
				borderColor: theme === 'dark' ? '#FF6347' : '#2E72BF',
				borderWidth: 5,
				shadowColor: 'rgba(0, 0, 0, 0.5)',
				shadowBlur: 5,
			},
			emphasis: {
				itemStyle: {
					areaColor: theme === 'dark' ? '#4B6A88' : '#FFD700',
					borderColor: '#FFF',
					borderWidth: 9,
				},
			},
		},
		series: [
			{
				type: 'map',
				map: mapName,
				emphasis: {
					itemStyle: {
						areaColor: theme === 'dark' ? '#FF6347' : '#FFD700',
					},
				},
				select: {
					itemStyle: {
						areaColor: theme === 'dark' ? '#FF6347' : '#FFD700',
					},
					label: {
						show: true,
						color: theme === 'dark' ? '#FFFFFF' : '#000000',
					},
				},
				regions: [
					{
						name: '郫都区',
						selected: mapName === 'cd',
					},
				],
			},
		],
	};
};

const option = ref(getOption(currentMap.value, store.theme));

// 定时刷新 MJPEG 流
const refreshMJPEGStream = () => {
	if (chartInstance.value && currentMap.value === 'cdjc') {
		chartInstance.value.setOption({
			graphic: [
				{
					type: 'image',
					id: 'mjpeg-stream',
					style: {
						image: 'http://127.0.0.1:5200',
					},
				},
			],
		});
	}
};

// 监听主题变化
watch(() => store.theme, (newTheme) => {
	option.value = getOption(currentMap.value, newTheme);
	if (chartInstance.value) {
		chartInstance.value.setOption(option.value, true); // 合并配置
	}
});

// 点击处理
const handleClick = (params) => {
	if (params.name === '郫都区') {
		if (currentMap.value === 'cd') {
			currentMap.value = 'pidu';
		} else if (currentMap.value === 'pidu') {
			currentMap.value = 'cdjc';
			if (!refreshInterval) {
				refreshInterval = setInterval(refreshMJPEGStream, 0);
			}
		} else if (currentMap.value === 'cdjc') {
			currentMap.value = 'cd';
			if (refreshInterval) {
				clearInterval(refreshInterval);
				refreshInterval = null;
			}
		}
		option.value = getOption(currentMap.value, store.theme);
		if (chartInstance.value) {
			chartInstance.value.setOption(option.value, true);
		}
	}
};

// 初始化图表
onMounted(() => {
	if (chartContainer.value) {
		chartInstance.value = echarts.init(chartContainer.value);
		chartInstance.value.setOption(option.value, true);
		chartInstance.value.on('click', handleClick);
	}
});

// 清理定时器
onBeforeUnmount(() => {
	if (refreshInterval) {
		clearInterval(refreshInterval);
	}
});
</script>
