// src/components/User/ModalLabels.vue

<template lang="pug">
  // AGORA COM v-if="isVisible" novamente
  div(v-if="isVisible" class="modal-overlay" @click.self="closeModal")
    div.modal-content
      h2 {{ editingLabel ? 'Editar Label' : 'Criar Nova Label' }}

      div.form-section
        div.form-group
          label(for="labelName") Nome da Label:
          input(
            type="text"
            id="labelName"
            v-model="currentLabel.name"
            placeholder="Ex: Urgente, Pessoal, Bug"
          )

        div.form-group
          label(for="labelColor") Cor da Label:
          input(type="color" id="labelColor" v-model="currentLabel.color")

        div.modal-actions
          button.btn.btn-save(@click="saveLabel")
            | {{ editingLabel ? 'Salvar Alterações' : 'Criar Label' }}
          button.btn.btn-cancel(@click="resetFormAndClose") Cancelar

      hr
      div.existing-labels-section(v-if="labels && labels.length > 0")
        h3 Labels Existentes
        ul.label-list
          li(v-for="label in labels" :key="label.id" class="label-item")
            span.label-name-display(:style="{ backgroundColor: label.hex_color || label.color }")
              | {{ label.name }}
            div.label-actions
              button.btn.btn-edit(@click="editLabel(label)") Editar
              button.btn.btn-delete(@click="confirmDeleteLabel(label.id)") Excluir
      div(v-else class="no-labels-message")
        | Nenhuma label cadastrada ainda.

      button.close-modal-btn(@click="closeModal") &times;
</template>

<script>
// Voltar a importar api diretamente para as chamadas de CRUD
// ou deixar o pai lidar com isso via emits
// AQUI, vou deixar o pai lidar via emits, então a api não é importada.
// REMOVER: import { api } from '@/services'; // Não precisa aqui

export default {
  name: 'LabelModal',
  // VOLTAR A TER AS PROPS isVisible, labelToEdit, labels
  props: {
    isVisible: { type: Boolean, default: false, },
    labelToEdit: { type: Object, default: null, },
    labels: { type: Array, default: () => [], }, // Labels virão via prop do pai
  },
  data() {
    return {
      currentLabel: { id: null, name: '', color: '#007bff', },
      editingLabel: false,
    };
  },
  watch: {
    // VOLTAR A TER O WATCHER PARA isVisible
    isVisible(newVal) {
      if (newVal) {
        if (this.labelToEdit) { this.currentLabel = { ...this.labelToEdit }; this.editingLabel = true; }
        else { this.resetForm(); this.editingLabel = false; }
      }
    },
    // VOLTAR A TER O WATCHER PARA labelToEdit
    labelToEdit(newLabel) {
      if (newLabel) { this.currentLabel = { ...newLabel, color: newLabel.hex_color || newLabel.color }; this.editingLabel = true; }
      else { this.resetForm(); this.editingLabel = false; }
    },
    // REMOVER watcher para '$route' se ainda existir, pois não é mais uma rota
  },
  methods: {
    resetForm() {
      this.currentLabel = { id: null, name: '', color: '#007bff', };
    },
    saveLabel() {
        if (!this.currentLabel.name.trim()) { alert('O nome da label não pode ser vazio!'); return; }
        if (!this.currentLabel.color.trim()) { alert('A cor da label é obrigatória!'); return; }
        const labelDataToSend = { id: this.currentLabel.id, name: this.currentLabel.name, hex_color: this.currentLabel.color, };
        // VOLTAR A EMITIR EVENTOS para o componente pai
        this.$emit(this.editingLabel ? 'update-label' : 'create-label', labelDataToSend);
    },
    closeModal() {
      // VOLTAR A EMITIR EVENTO 'close' para o componente pai
      this.$emit('close');
      this.resetForm();
    },
    resetFormAndClose() { this.resetForm(); this.closeModal(); },
    editLabel(label) { this.currentLabel = { ...label, color: label.hex_color || label.color }; this.editingLabel = true; },
    confirmDeleteLabel(labelId) {
      if (confirm("Tem certeza que deseja excluir esta label? Esta ação é irreversível.")) {
        // VOLTAR A EMITIR EVENTO 'delete-label' para o componente pai
        this.$emit('delete-label', labelId);
      }
    }
  },
  // REMOVER hook 'created' para buscar labels, pois as labels virão via prop ou serão buscadas pelo pai.
};
</script>

<style scoped>
/* Estilos básicos para o modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Garante que o modal esteja acima de outros elementos */
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 450px; /* Largura máxima para o modal */
  position: relative;
  display: flex; /* Para organizar as seções verticalmente */
  flex-direction: column;
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
  text-align: center;
  margin-bottom: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="color"] {
  width: calc(100% - 22px); /* Ajuste para padding */
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.form-group input[type="color"] {
  height: 40px; /* Altura padrão para o input de cor */
  padding: 0;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  margin-bottom: 20px; /* Margem para separar do hr */
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.btn-save {
  background-color: #007bff;
  color: white;
}

.btn-save:hover {
  background-color: #0056b3;
}

.btn-cancel {
  background-color: #6c757d;
  color: white;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.close-modal-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.8em;
  color: #aaa;
  cursor: pointer;
  line-height: 1; /* Alinhamento vertical do "x" */
}

.close-modal-btn:hover {
  color: #666;
}

/* Estilos para a seção de labels existentes */
.existing-labels-section {
  margin-top: 20px;
  padding-top: 20px; /* Adiciona padding para a linha */
}

.existing-labels-section h3 {
  text-align: center;
  color: #444;
  margin-bottom: 15px;
}

.label-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 200px; /* Altura máxima para a lista, com scroll se necessário */
  overflow-y: auto;
  border: 1px solid #f0f0f0;
  border-radius: 5px;
}

.label-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #f9f9f9;
  background-color: #fcfcfc;
  justify-content: space-between; /* Espaço entre nome e botões */
}

.label-item:last-child {
  border-bottom: none;
}

/* NOVO: Estilo para o span que contém o nome da label */
.label-item > .label-name-display { /* Use uma nova classe para identificar o span do nome */
  flex-grow: 1; /* Ocupa o espaço restante */
  color: #333;
  font-weight: 500;
  
  /* ESTILOS PARA FAZER O TEXTO "DENTRO DA LABEL" */
  display: inline-flex; /* Permite que o span se ajuste ao conteúdo e tenha padding */
  align-items: center; /* Centraliza verticalmente o texto */
  padding: 4px 8px; /* Padding interno para o texto dentro da "pílula" */
  border-radius: 4px; /* Bordas arredondadas para a forma de "pílula" */
  font-size: 0.95em; /* Ajuste o tamanho da fonte se necessário */
  margin-right: 10px; /* Espaçamento à direita para separar das ações */
  color: #fff; /* Cor do texto (muitas vezes branco para cores escuras) */
  text-shadow: 0 0 3px rgba(0,0,0,0.5); /* Sombra para o texto para melhor contraste */
  /* Adicione uma transição para as cores se elas mudarem */
  transition: background-color 0.2s ease;
}


.label-actions {
  display: flex;
  gap: 8px; /* Espaço entre botões de ação */
  flex-shrink: 0; /* Impede que os botões encolham */
}

.btn-edit, .btn-delete {
  padding: 5px 10px;
  font-size: 0.9em;
  border-radius: 4px;
}

.btn-edit {
  background-color: #ffc107; /* Cor para o botão de editar */
  color: #333;
}

.btn-edit:hover {
  background-color: #e0a800;
}

.btn-delete {
  background-color: #dc3545; /* Cor para o botão de excluir */
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

.no-labels-message {
  text-align: center;
  color: #666;
  margin-top: 20px;
}
</style>