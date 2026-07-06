<script setup lang="ts">
import Navbar from "@/components/Navbar.vue";
import Sidebar from "@/components/Sidebar.vue";
</script>

<template>
  <div class="h-screen flex overflow-hidden">
    <Sidebar />

    <div class="flex-1 flex flex-col">
      <Navbar />

      
<main class="flex-1 overflow-y-auto bg-[#fff8f9] p-8">
  <div
    class="bg-white rounded-3xl p-8 shadow-sm border border-red-100"
  >
    <p class="text-[#d10f2f] font-semibold uppercase tracking-wider">
      Tableau de bord
    </p>

    <h1 class="mt-2 text-4xl font-bold text-gray-800">
      Bienvenue sur ERP COSELEC
    </h1>

    <p class="mt-4 text-gray-500 text-lg">
      Centralisez vos opérations, suivez vos demandes,
      gérez vos projets et accédez aux informations de
      l'entreprise depuis une plateforme unique.
    </p>
  </div>

  <div class="mt-8 grid grid-cols-4 gap-6">
    <div
      class="bg-white p-6 rounded-2xl border-l-4 border-[#d10f2f] shadow-sm"
    >
      <p class="text-gray-500">Employés</p>
      <h2 class="text-3xl font-bold mt-2">28</h2>
    </div>

    <div
      class="bg-white p-6 rounded-2xl border-l-4 border-[#d10f2f] shadow-sm"
    >
      <p class="text-gray-500">Demandes</p>
      <h2 class="text-3xl font-bold mt-2">12</h2>
    </div>

    <div
      class="bg-white p-6 rounded-2xl border-l-4 border-[#d10f2f] shadow-sm"
    >
      <p class="text-gray-500">Projets</p>
      <h2 class="text-3xl font-bold mt-2">5</h2>
    </div>

    <div
      class="bg-white p-6 rounded-2xl border-l-4 border-[#d10f2f] shadow-sm"
    >
      <p class="text-gray-500">Documents</p>
      <h2 class="text-3xl font-bold mt-2">154</h2>
    </div>
  </div>
</main>

    </div>
  </div>
</template>