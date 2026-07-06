<template>
  <AppLayout>
    <div class="min-h-screen bg-[linear-gradient(180deg,_#fff_0%,_#fff8f9_100%)] px-6 py-8 lg:px-8">
      <section class="mx-auto max-w-4xl">
        <div class="overflow-hidden rounded-[30px] border border-red-100 bg-white shadow-[0_18px_50px_rgba(127,7,28,0.12)]">
          <div class="bg-gradient-to-r from-[#d10f2f] to-[#97091f] px-6 py-8 text-white sm:px-10">
            <p class="text-xs font-semibold uppercase tracking-[0.4em] text-white/80">
              {{ sectionMeta.eyebrow }}
            </p>
            <h1 class="mt-3 text-3xl font-black tracking-tight sm:text-4xl">
              {{ sectionMeta.title }}
            </h1>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-white/85 sm:text-base">
              {{ sectionMeta.description }}
            </p>
          </div>

          <div class="grid gap-8 px-6 py-8 lg:grid-cols-[1.1fr_0.9fr] lg:px-10 lg:py-10">
            <form class="space-y-5" @submit.prevent="submitRequest">
              <div>
                <label class="mb-2 block text-sm font-semibold text-gray-700">Sujet</label>
                <input
                  v-model="form.subject"
                  type="text"
                  class="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-800 outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-100"
                  :placeholder="sectionMeta.subjectPlaceholder"
                  required
                />
              </div>

              <div>
                <label class="mb-2 block text-sm font-semibold text-gray-700">Détail de la demande</label>
                <textarea
                  v-model="form.description"
                  rows="6"
                  class="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-800 outline-none transition focus:border-red-400 focus:ring-4 focus:ring-red-100"
                  :placeholder="sectionMeta.descriptionPlaceholder"
                  required
                ></textarea>
              </div>

              <div class="flex flex-wrap gap-3 pt-2">
                <button
                  type="submit"
                  :disabled="isSubmitting.value"
                  class="inline-flex items-center gap-2 rounded-2xl bg-red-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-red-200 transition hover:bg-red-700"
                >
                  <span class="material-symbols-outlined text-[18px]">send</span>
                  {{ isSubmitting.value ? "Envoi..." : "Envoyer la demande" }}
                </button>
                <RouterLink
                  :to="{ name: 'requests' }"
                  class="inline-flex items-center gap-2 rounded-2xl border border-red-100 bg-white px-5 py-3 text-sm font-semibold text-red-700 transition hover:bg-red-50"
                >
                  Retour au portail
                </RouterLink>
              </div>
            </form>

            <aside class="rounded-[26px] border border-red-100 bg-[linear-gradient(180deg,_#fff_0%,_#fff8f9_100%)] p-6">
              <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-600 text-white shadow-lg shadow-red-200">
                <span class="material-symbols-outlined text-[30px]">{{ sectionMeta.icon }}</span>
              </div>

              <h2 class="mt-5 text-2xl font-black tracking-tight text-gray-950">
                Ce que tu peux demander
              </h2>
              <p class="mt-3 text-sm leading-6 text-gray-500">
                {{ sectionMeta.helpText }}
              </p>

              <div class="mt-6 space-y-3">
                <div
                  v-for="hint in sectionMeta.hints"
                  :key="hint"
                  class="flex items-start gap-3 rounded-2xl border border-gray-100 bg-white p-4"
                >
                  <span class="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-red-50 text-xs font-bold text-red-600">
                    ✓
                  </span>
                  <p class="text-sm leading-6 text-gray-600">{{ hint }}</p>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue';
import { RouterLink } from 'vue-router';
import { useRouter } from 'vue-router';
import AppLayout from '@/layouts/AppLayout.vue';
import { createTicket, type TicketCategory } from '@/services/tickets';

const props = defineProps<{
  section: 'hr' | 'it' | 'facilities';
}>();

const router = useRouter();

const sectionMeta = computed(() => {
  const map = {
    hr: {
      eyebrow: 'Demande RH',
      title: 'Créer une demande RH',
      icon: 'groups',
      description: 'Utilise ce formulaire pour les congés, onboarding, documents collaborateurs ou validations internes.',
      subjectPlaceholder: 'Ex: Demande de congé du 12 au 16 août',
      descriptionPlaceholder: 'Explique le besoin RH, le contexte et les dates importantes.',
      helpText: 'Les demandes RH doivent rester claires, datées et liées à un collaborateur identifié.',
      hints: [
        'Indique le nom du collaborateur concerné.',
        'Ajoute les dates, le motif et toute pièce utile.',
        'Précise si la demande nécessite une validation hiérarchique.'
      ]
    },
    it: {
      eyebrow: 'Demande IT',
      title: 'Créer un ticket IT',
      icon: 'memory',
      description: 'Déclare un incident, un besoin d’accès, un problème matériel ou une demande de support applicatif.',
      subjectPlaceholder: 'Ex: Impossible de se connecter au VPN',
      descriptionPlaceholder: 'Décris l’incident, les étapes pour le reproduire et l’impact métier.',
      helpText: 'Ajoute un maximum de détails techniques pour accélérer la prise en charge.',
      hints: [
        'Mentionne le poste, l’utilisateur et le service concerné.',
        'Indique le niveau d’urgence et l’impact sur l’activité.',
        'Ajoute une capture ou un message d’erreur si disponible.'
      ]
    },
    facilities: {
      eyebrow: 'Demande Facilities',
      title: 'Créer une demande Facilities',
      icon: 'home_repair_service',
      description: 'Dépose une demande liée aux locaux, badge, maintenance, salles, matériel ou logistique.',
      subjectPlaceholder: 'Ex: Climatisation salle projet en panne',
      descriptionPlaceholder: 'Précise le lieu, le matériel concerné et l’action attendue.',
      helpText: 'Les demandes Facilities sont traitées selon le lieu, le service et la criticité du besoin.',
      hints: [
        'Indique la zone ou le bâtiment.',
        'Précise s’il s’agit d’une urgence opérationnelle.',
        'Ajoute les informations d’accès si une intervention est requise.'
      ]
    }
  } as const;

  return map[props.section];
});

const form = reactive({
  subject: '',
  description: '',
  priority: 'Normal',
  attachment: ''
});

const isSubmitting = reactive({
  value: false
});

const sectionToCategory: Record<typeof props.section, TicketCategory> = {
  hr: 'Leave',
  it: 'IT',
  facilities: 'Facility'
};

const submitRequest = async () => {
  if (isSubmitting.value) {
    return;
  }

  isSubmitting.value = true;

  try {
    await createTicket({
      title: form.subject,
      description: form.description,
      category: sectionToCategory[props.section],
      meta_data: {
        source_section: props.section,
        priority: form.priority,
        attachment: form.attachment || null
      }
    });

    window.alert('Demande créée avec succès.');
    router.push({ name: 'tickets' });
  } catch (error) {
    console.error('Erreur lors de la création de la demande', error);
    window.alert('Impossible de créer la demande pour le moment.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>
