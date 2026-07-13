<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <table class="w-full text-left">
      <thead>
        <tr>
          <th class="border-r px-4 py-2">Titre</th>
          <th class="border-r px-4 py-2">Statut</th>
          <th class="border-r px-4 py-2">Priorité</th>
          <th class="border-r px-4 py-2">Assigné</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id" class="border-t">
          <td>{{ task.title }}</td>
          <td>{{ task.status }}</td>
          <td>{{ task.priority }}</td>
          <td>{{ task.assignee_id }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps(['tasks']); // Reçoit les données du parent
</script>

<script setup lang="ts">

</script>