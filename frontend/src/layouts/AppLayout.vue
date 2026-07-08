<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';
</script>

<template>
	<div class="flex h-screen overflow-hidden">
		<Sidebar />

		<div class="flex min-w-0 flex-1 flex-col">
			<Navbar />

			<main class="flex min-w-0 flex-1 overflow-y-auto bg-[#fff8f9] p-6">
				<slot />
			</main>
		</div>
	</div>
</template>
