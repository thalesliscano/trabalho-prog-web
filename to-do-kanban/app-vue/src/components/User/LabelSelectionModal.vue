<template lang="pug">
  div(v-if="isVisible" class="modal-overlay" @click.self="closeModal")
    div.modal-content
      h2 Selecionar Labels para a Tarefa

      div.labels-list-container
        div(v-if="allLabels && allLabels.length > 0")
          p Selecione as labels para esta tarefa:
          div.label-checkbox-group
            label(v-for="label in allLabels" :key="label.id" class="label-checkbox-item")
              input(
                type="checkbox"
                :value="label.id"
                v-model="selectedLabelIds"
              )
              span.task-label-pill(:style="{ backgroundColor: label.hex_color }")
                | {{ label.name }}
        div(v-else class="no-labels-message")
          | Nenhuma label global cadastrada ainda. Crie labels no gerenciador de labels.

      div.modal-actions
        button.btn.btn-save(@click="handleSaveOrRedirect")
          | {{ allLabels && allLabels.length > 0 ? 'Salvar Labels' : 'Criar Labels Globais' }}
        button.btn.btn-cancel(@click="closeModal") Cancelar

      button.close-modal-btn(@click="closeModal") &times;
</template>

<script>
export default {
  name: 'LabelSelectionModal',
  props: {
    isVisible: {
      type: Boolean,
      default: false,
    },
    allLabels: {
      type: Array,
      default: () => [],
    },
    taskLabels: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      selectedLabelIds: [],
    };
  },
  watch: {
    isVisible(newVal) {
      if (newVal) {
        this.selectedLabelIds = this.taskLabels.map(label => label.id);
      }
    },
    taskLabels: {
      handler(newLabels) {
        if (this.isVisible) {
          this.selectedLabelIds = newLabels.map(label => label.id);
        }
      },
      deep: true,
    }
  },
  methods: {
    handleSaveOrRedirect() {
      if (this.allLabels && this.allLabels.length > 0) {
        this.saveSelection();
      } else {
        this.$emit('open-global-label-modal');
        this.closeModal();
      }
    },
    saveSelection() {
      this.$emit('update-task-labels', this.selectedLabelIds);
    },
    closeModal() {
      this.$emit('close');
      this.selectedLabelIds = [];
    },
  },
};
</script>

<style lang="scss" scoped>
// Variáveis SCSS
$primary-color: #007bff;
$primary-hover-color: #0056b3;
$cancel-color: #6c757d;
$cancel-hover-color: #5a6268;
$text-dark: #333;
$text-medium: #666;
$text-light: #aaa;
$border-light: #ddd;
$shadow-color: rgba(0, 0, 0, 0.3);
$overlay-color: rgba(0, 0, 0, 0.5);

// Mixin para estilos de botão
@mixin button-styles($bg-color, $text-color) {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
  background-color: $bg-color;
  color: $text-color;

  &:hover {
    background-color: darken($bg-color, 10%);
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: $overlay-color;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001; // Z-index maior para sobrepor o LabelModal, se necessário
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 5px 15px $shadow-color;
  width: 90%;
  max-width: 500px;
  position: relative;
  display: flex;
  flex-direction: column;

  h2 {
    margin-top: 0;
    color: $text-dark;
    text-align: center;
    margin-bottom: 25px;
  }
}

.labels-list-container {
  margin-bottom: 20px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 10px;
}

.label-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.label-checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 0;

  input[type="checkbox"] {
    min-width: 20px;
    min-height: 20px;
    accent-color: $primary-color;
    cursor: pointer;
  }
}

.task-label-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  color: white;
  text-shadow: 0 0 3px rgba(0,0,0,0.5);
  white-space: nowrap;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  flex-grow: 1;
}

.no-labels-message {
  text-align: center;
  color: $text-medium;
  margin-top: 10px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;

  .btn {
    &.btn-save {
      @include button-styles($primary-color, white);
    }

    &.btn-cancel {
      @include button-styles($cancel-color, white);
    }
  }
}

.close-modal-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.8em;
  color: $text-light;
  cursor: pointer;
  line-height: 1;

  &:hover {
    color: darken($text-light, 20%);
  }
}
</style>