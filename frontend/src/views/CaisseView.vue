<template>
  <div class="min-h-screen bg-gray-50 flex">
    <Sidebar />

    <div class="flex-1 flex flex-col">
      <Navbar />

      <main class="flex-1 p-8 overflow-y-auto">
        <div class="max-w-5xl mx-auto">
          <div class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span class="material-symbols-outlined text-[#d10f2f]">receipt_long</span>
              Pièce de Caisse
            </h1>
            <button 
              @click="generateCaissePdf"
              class="px-4 py-2 bg-[#d10f2f] text-white rounded-xl shadow-lg hover:bg-[#97091f] transition flex items-center gap-2"
            >
              <span class="material-symbols-outlined">download</span>
              Générer et Télécharger
            </button>
          </div>

          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-8">
            <!-- Entête -->
            <div class="grid grid-cols-3 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">NUM</label>
                <input v-model="form.num" type="text" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">N° AFFAIRE</label>
                <input v-model="form.affaire" type="text" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">N° CIA</label>
                <input v-model="form.cia" type="text" class="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition" />
              </div>
            </div>

            <!-- Dépenses -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-gray-800">Dépenses</h3>
                <button @click="addDepense" class="text-sm text-red-600 font-medium hover:text-red-800 flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm">add</span> Ajouter une ligne
                </button>
              </div>
              <table class="w-full text-left text-sm text-gray-600">
                <thead class="bg-gray-50 text-gray-700">
                  <tr>
                    <th class="px-4 py-2 rounded-l-lg w-1/4">DATE</th>
                    <th class="px-4 py-2 w-1/2">DÉSIGNATION</th>
                    <th class="px-4 py-2">MONTANT</th>
                    <th class="px-4 py-2 rounded-r-lg w-16"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in form.depenses" :key="'dep-'+index" class="border-b last:border-0">
                    <td class="py-2 pr-2"><input v-model="row.date" type="date" class="w-full px-3 py-1.5 border rounded-lg" /></td>
                    <td class="py-2 pr-2"><input v-model="row.designation" type="text" class="w-full px-3 py-1.5 border rounded-lg" placeholder="Description" /></td>
                    <td class="py-2 pr-2"><input v-model="row.montant" type="text" class="w-full px-3 py-1.5 border rounded-lg" placeholder="0 CFA" /></td>
                    <td class="py-2 text-right">
                      <button @click="removeDepense(index)" class="text-gray-400 hover:text-red-500"><span class="material-symbols-outlined text-lg">delete</span></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <hr class="border-gray-100" />

            <!-- Recettes -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-gray-800">Recettes</h3>
                <button @click="addRecette" class="text-sm text-red-600 font-medium hover:text-red-800 flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm">add</span> Ajouter une ligne
                </button>
              </div>
              <table class="w-full text-left text-sm text-gray-600">
                <thead class="bg-gray-50 text-gray-700">
                  <tr>
                    <th class="px-4 py-2 rounded-l-lg w-1/4">DATE</th>
                    <th class="px-4 py-2 w-1/2">DÉSIGNATION</th>
                    <th class="px-4 py-2">MONTANT</th>
                    <th class="px-4 py-2 rounded-r-lg w-16"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in form.recettes" :key="'rec-'+index" class="border-b last:border-0">
                    <td class="py-2 pr-2"><input v-model="row.date" type="date" class="w-full px-3 py-1.5 border rounded-lg" /></td>
                    <td class="py-2 pr-2"><input v-model="row.designation" type="text" class="w-full px-3 py-1.5 border rounded-lg" placeholder="Description" /></td>
                    <td class="py-2 pr-2"><input v-model="row.montant" type="text" class="w-full px-3 py-1.5 border rounded-lg" placeholder="0 CFA" /></td>
                    <td class="py-2 text-right">
                      <button @click="removeRecette(index)" class="text-gray-400 hover:text-red-500"><span class="material-symbols-outlined text-lg">delete</span></button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import Navbar from '@/components/Navbar.vue';
import { api } from '@/services/api';
import { useToast } from '@/composables/useToast';

const toast = useToast();

const form = ref({
  num: '',
  affaire: '',
  cia: '',
  depenses: [{ date: '', designation: '', montant: '' }],
  recettes: [{ date: '', designation: '', montant: '' }]
});

const addDepense = () => form.value.depenses.push({ date: '', designation: '', montant: '' });
const removeDepense = (index: number) => form.value.depenses.splice(index, 1);

const addRecette = () => form.value.recettes.push({ date: '', designation: '', montant: '' });
const removeRecette = (index: number) => form.value.recettes.splice(index, 1);

async function generateCaissePdf() {
  try {
    const res = await api.post('/caisse/generate', form.value);
    if (res.data && res.data.pdf_url) {
      const url = res.data.pdf_url;
      window.open(url, '_blank');
    }
  } catch (e) {
    console.error("Erreur lors de la génération", e);
    toast.error("Une erreur est survenue lors de la génération du PDF.");
  }
}
</script>
