<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-xl font-semibold mb-4">Tâches du projet</h2>
    
    <div class="overflow-x-auto border rounded-lg border-gray-200">
      <table class="min-w-full divide-y divide-gray-200">
        <!-- Le thead reste identique -->
        <thead class="bg-gray-50">
          <tr v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <th 
              v-for="header in headerGroup.headers" 
              :key="header.id" 
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer select-none hover:bg-gray-100"
              @click="header.column.getToggleSortingHandler()?.($event)"
            >
              <div class="flex items-center gap-2">
                <FlexRender 
                  :render="header.column.columnDef.header" 
                  :props="header.getContext()" 
                />
                <span v-if="header.column.getIsSorted() === 'asc'" class="text-gray-400">↑</span>
                <span v-else-if="header.column.getIsSorted() === 'desc'" class="text-gray-400">↓</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="row in table.getRowModel().rows" 
            :key="row.id" 
            :class="[
              'cursor-pointer transition-colors duration-150', 
              getRowColor(row.original.status, row.original.priority)
            ]"
            @click="onRowClick(row.original)"
          >
            <td 
              v-for="cell in row.getVisibleCells()" 
              :key="cell.id" 
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-800"
            >
              <FlexRender 
                :render="cell.column.columnDef.cell" 
                :props="cell.getContext()" 
              />
            </td>
          </tr>
          <!-- Message si le projet n'a aucune tâche -->
          <tr v-if="table.getRowModel().rows.length === 0">
            <td :colspan="columns.length" class="px-6 py-8 text-center text-gray-500">
              Aucune tâche trouvée pour ce projet.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  useVueTable, 
  getCoreRowModel, 
  getSortedRowModel,
  FlexRender 
} from '@tanstack/vue-table'
import type { SortingState } from '@tanstack/vue-table'

// On définit la prop qui recevra les tâches du projet sélectionné
const props = defineProps<{
  tasks: Array<any>
}>()
const columns = [
  { accessorKey: 'id', header: 'ID' },
  { accessorKey: 'title', header: 'Titre de la tâche' },
  { accessorKey: 'priority', header: 'Priorité' },
  { accessorKey: 'status', header: 'Statut' },
  { accessorKey: 'assignee_id', header: 'Assigné à' },
]
const sorting = ref<SortingState>([])

// La table utilise "props.tasks" de manière réactive
const table = useVueTable({
  get data() { return props.tasks },
  columns,
  state: {
    get sorting() { return sorting.value },
  },
  onSortingChange: updaterOrValue => {
    sorting.value = typeof updaterOrValue === 'function' ? updaterOrValue(sorting.value) : updaterOrValue
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
})

const onRowClick = (task: any) => {
  console.log('Tâche sélectionnée :', task)
}



const getRowColor = (status: string, priority: string) => {
  switch (status) {
    case 'Terminée': return 'bg-emerald-50 hover:bg-emerald-100'
    case 'En cours': return 'bg-sky-50 hover:bg-sky-100'
    case 'Revue': return 'bg-purple-50 hover:bg-purple-100'
    case 'A faire': return 'bg-amber-50 hover:bg-amber-100'
  }
  return 'bg-white hover:bg-gray-50'
}
</script>