<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function logout() {
    localStorage.removeItem("access_token");
    sessionStorage.removeItem("access_token");

    router.push("/login");
}
</script>

<template>
    <header
        class="h-16 bg-white border-b border-red-100 px-6 flex items-center justify-between"
    >
        <div>
            <h1 class="text-xl font-bold text-[#d10f2f]">
                ERP COSELEC
            </h1>
        </div>

        <div class="flex items-center gap-6">
            <button
                class="relative p-2 rounded-lg hover:bg-red-50 transition"
            >
                <span class="material-symbols-outlined text-[#d10f2f]">
                    notifications

                </span>
            </button>

            <div class="flex items-center gap-3">
                <div
                    class="h-10 w-10 rounded-full bg-[#d10f2f] text-white flex items-center justify-center"
                >
                    A
                </div>

                <div>
                    <p class="font-semibold">
                        Adam Guizaoui
                    </p>

                    <p class="text-xs text-gray-500">
                        Administrateur
                    </p>
                </div>
            </div>

            
<button class="flex items-center gap-2 text-[#d10f2f] hover:bg-red-50 transition p-2 rounded-lg" @click="logout">
  <span class="material-symbols-outlined">
    logout
  </span>
</button>

        </div>
    </header>
</template>