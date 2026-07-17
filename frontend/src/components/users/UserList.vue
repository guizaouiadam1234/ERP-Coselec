<template>
  <div class="overflow-x-auto">
    <table class="w-full text-left text-sm text-gray-500">
      <thead class="bg-gray-50 text-xs text-gray-700 uppercase border-b border-gray-100">
        <tr>
          <th scope="col" class="px-6 py-4 font-semibold">Nom</th>
          <th scope="col" class="px-6 py-4 font-semibold">Email</th>
          <th scope="col" class="px-6 py-4 font-semibold">Rôle</th>
          <th scope="col" class="px-6 py-4 font-semibold text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading" class="bg-white border-b border-gray-50">
          <td colspan="4" class="px-6 py-12 text-center text-gray-400">
            Chargement des utilisateurs...
          </td>
        </tr>
        
        <tr v-else-if="users.length === 0" class="bg-white border-b border-gray-50">
          <td colspan="4" class="px-6 py-12 text-center text-gray-400">
            Aucun utilisateur trouvé.
          </td>
        </tr>

        <tr 
          v-else
          v-for="user in users" 
          :key="user.id" 
          class="bg-white border-b border-gray-50 hover:bg-gray-50/50 transition"
        >
          <td class="px-6 py-4 font-medium text-gray-900">
            {{ user.name }}
          </td>
          <td class="px-6 py-4">
            {{ user.email }}
          </td>
          <td class="px-6 py-4">
            <span 
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="getRoleColor(user.roles[0]?.name)"
            >
              {{ user.roles[0]?.name || 'Sans rôle' }}
            </span>
          </td>
          <td class="px-6 py-4 text-right">
            <button 
              @click="$emit('edit', user)"
              class="font-medium text-blue-600 hover:text-blue-800 transition mr-4"
            >
              Éditer
            </button>
            <button 
              v-if="user.id !== currentUserId"
              @click="$emit('delete', user)"
              class="font-medium text-red-600 hover:text-red-800 transition"
            >
              Supprimer
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { User } from '@/services/userService';

defineProps<{
  users: User[];
  loading: boolean;
  currentUserId?: number;
}>();

defineEmits<{
  (e: 'edit', user: User): void;
  (e: 'delete', user: User): void;
}>();

const getRoleColor = (roleName: string | undefined) => {
  if (!roleName) return 'bg-gray-100 text-gray-800';
  
  switch (roleName) {
    case 'Admin': return 'bg-purple-100 text-purple-800';
    case 'Employe': return 'bg-blue-100 text-blue-800';
    case 'RH': return 'bg-green-100 text-green-800';
    case 'Direction': return 'bg-orange-100 text-orange-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};
</script>
