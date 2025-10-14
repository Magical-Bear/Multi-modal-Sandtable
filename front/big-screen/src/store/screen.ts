import { defineStore } from 'pinia'

interface ScreenState {
	title: string,
	theme: 'dark' | 'light'
}

export const useScreenStore = defineStore({
	id: 'screen',
	state: (): ScreenState => {
		return {
			title: '锦城智慧物流可视化大屏',
			theme: 'dark'
		}
	}
})
