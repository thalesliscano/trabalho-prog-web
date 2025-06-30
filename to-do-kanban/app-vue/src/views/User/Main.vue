<template lang="pug">
  .kanban-board
    LabelModal(
      :isVisible="getShowLabelModal"
      :labelToEdit="labelToEdit"
      :labels="labels"
      @close="closeLabelModal"
      @create-label="handleCreateLabel"
      @update-label="handleUpdateLabel"
      @delete-label="handleDeleteLabel"
    )

    LabelSelectionModal(
      :isVisible="showTaskLabelSelectionModal"
      :allLabels="labels"
      :taskLabels="selectedTask ? selectedTask.labels : []"
      @close="showTaskLabelSelectionModal = false"
      @update-task-labels="handleUpdateTaskLabels"
      @open-global-label-modal="handleOpenGlobalLabelModal"
    )

    .kanban-column(v-for="(tasks, status) in columns" :key="status")
      h2 {{ statusLabels[status] }}

      .kanban-task(v-for="task in tasks" :key="task.id" :class="getTaskClass(task)")
        button.close-btn(@click="deleteTask(task)")
          | &times;
        h3 {{ task.title }}
        p {{ task.description }}

        .task-labels-container(v-if="task.labels && task.labels.length > 0")
          span.task-label-pill(
            v-for="label in task.labels"
            :key="label.id"
            :style="{ backgroundColor: label.hex_color }"
          )
            | {{ label.name }}

        button.btn-manage-labels(@click="openTaskLabelSelectionModal(task)")
          | Gerenciar Labels

        .task-controls
          button(v-if="status !== 'archived'" @click="moveTask(task, 'archived')")
            | Archive
          button(v-if="status !== 'toDo'" @click="moveTask(task, 'toDo')")
            | To Do
          button(v-if="status !== 'doing'" @click="moveTask(task, 'doing')")
            | Doing
          button(v-if="status !== 'done'" @click="moveTask(task, 'done')")
            | Done

      .add-task-column
        .input-container(v-if="showInput[status]")
          input(v-model="newTaskText[status]" @keyup.enter="addTaskToColumn(status)" placeholder="Enter task name")
        button(@click="toggleInput(status)") +
    p.nome-profile {{ name }}
</template>

<script>
import LabelModal from "@/components/User/ModalLabels.vue";
import LabelSelectionModal from "@/components/User/LabelSelectionModal.vue";
import { api } from "../../services"; // Assumindo que services.js é o seu api.js principal
import { mapState, mapActions } from 'vuex';

export default {
  name: "TemplateKanban", // Mantive o nome original da script tag
  components: {
    LabelModal,
    LabelSelectionModal,
  },
  data() {
    return {
      name: '',
      columns: {
        toDo: [],
        doing: [],
        done: [],
        archived: [],
      },
      newTaskText: {
        toDo: "",
        doing: "",
        done: "",
        archived: "",
      },
      showInput: {
        toDo: false,
        doing: false,
        done: false,
        archived: false,
      },
      statusLabels: {
        toDo: "To Do",
        doing: "Doing",
        done: "Done",
        archived: "Archive",
      },
      labelToEdit: null,
      labels: [],

      showTaskLabelSelectionModal: false,
      selectedTask: null,
    };
  },
  computed: {
    ...mapState(['showLabelModal']),
    getShowLabelModal() {
      return this.showLabelModal;
    }
  },
  methods: {
    ...mapActions(['toggleLabelModal']),

    getTaskClass(task) {
      switch (task.status) {
        case 'toDo':
          return 'task-to-do';
        case 'doing':
          return 'task-doing';
        case 'done':
        case 'archived':
          return `task-${task.status}`;
        default:
          return '';
      }
    },
    async addTaskToColumn(status) {
      if (!this.newTaskText[status]) return;

      const newTask = {
        title: this.newTaskText[status],
        description: `Descrição da tarefa para ${this.newTaskText[status]}`,
        status: status,
        labels: []
      };

      try {
        const response = await api.createTask(newTask);
        console.log("Tarefa criada com sucesso", response);

        const createdTask = {
          id: response.id,
          user_task_id: response.user_task_id,
          title: response.title,
          description: response.description || "Sem descrição",
          status: response.status,
          labels: response.labels || []
        };
        this.columns[status].push(createdTask);

      } catch (error) {
        console.error("Erro ao criar tarefa", error);
        alert(error.message || "Erro ao criar tarefa!");
      } finally {
        this.newTaskText[status] = "";
        this.showInput[status] = false;
      }
    },

    toggleInput(status) {
      this.showInput[status] = !this.showInput[status];
      this.newTaskText[status] = "";
    },

    async moveTask(task, newStatus) {
      if (task.status === newStatus) return;

      if (!this.columns[newStatus]) {
        console.error("Novo status inválido:", newStatus);
        return;
      }

      try {
        const response = await api.patch(
          `/tasks/status/${task.id}`,
          {
            status: newStatus,
          }
        );
        console.log("Tarefa atualizada com sucesso", response);

        const oldStatus = task.status;
        const taskIndex = this.columns[oldStatus].findIndex((t) => t.id === task.id);
        if (taskIndex !== -1) {
          const [movedTask] = this.columns[oldStatus].splice(taskIndex, 1);
          movedTask.status = newStatus;
          this.columns[newStatus].push(movedTask);
        }
      } catch (error) {
        console.error("Erro ao atualizar a tarefa:", error);
        alert(error.message || "Erro ao mover tarefa!");
        this.fetchUserData();
      }
    },

    async deleteTask(task) {
      try {
        await api.deleteTask(task.id);
        console.log("Tarefa excluída com sucesso", task.id);
        for (const status in this.columns) {
          const taskIndex = this.columns[status].findIndex(t => t.id === task.id);
          if (taskIndex !== -1) {
            this.columns[status].splice(taskIndex, 1);
            break;
          }
        }
      } catch (error) {
        console.error("Erro ao excluir a tarefa:", error);
        alert(error.message || "Erro ao excluir tarefa!");
      }
    },

    async fetchUserData() {
      try {
        const data = await api.getUserData();
        this.userData = data;
        this.name = this.userData.usuario.name;
        console.log("Dados do usuário carregados:", this.userData);

        this.columns = {
          toDo: [],
          doing: [],
          done: [],
          archived: [],
        };

        if (data.usuario.board && data.usuario.board.tarefas) {
          data.usuario.board.tarefas.forEach((task) => {
            const newTask = {
              id: task.id,
              user_task_id: task.user_task_id,
              title: task.title,
              status: task.status === 'archive' ? 'archived' : task.status, // Normaliza 'archive' para 'archived'
              description: task.description || "Sem descrição",
              labels: task.labels || []
            };
            if (this.columns[newTask.status]) {
              this.columns[newTask.status].push(newTask);
            }
          });
        }
        this.labels = data.usuario.labels || [];
      } catch (error) {
        console.error("Erro ao buscar dados do usuário:", error);
        alert("Erro ao carregar dados do usuário: " + (error.message || "Erro desconhecido"));
        if (error.message === 'Token inválido ou expirado!') {
          this.$router.push('/login');
        }
      }
    },

    closeLabelModal() {
      this.toggleLabelModal(false);
      this.labelToEdit = null;
    },

    async fetchLabels() {
      try {
        const response = await api.getLabels();
        this.labels = response;
        console.log("Labels carregadas:", this.labels);
      } catch (error) {
        console.error("Erro ao carregar labels:", error);
        this.labels = [];
      }
    },

    async handleCreateLabel(newLabel) {
      try {
        const response = await api.createLabel(newLabel);
        console.log("Label criada com sucesso:", response);
        this.fetchLabels();
      } catch (error) {
        console.error("Erro ao criar label:", error);
        alert(error.message || "Erro ao criar label!");
      }
    },

    async handleUpdateLabel(updatedLabel) {
      try {
        const response = await api.updateLabel(updatedLabel.id, updatedLabel);
        console.log("Label atualizada com sucesso:", response);
        this.fetchLabels();
        this.labelToEdit = null;
      } catch (error) {
        console.error("Erro ao atualizar label:", error);
        alert(error.message || "Erro ao atualizar label!");
      }
    },

    async handleDeleteLabel(labelId) {
      if (confirm("Tem certeza que deseja excluir esta label? Esta ação é irreversível.")) {
        try {
          await api.deleteLabel(labelId);
          console.log("Label excluída com sucesso:", labelId);
          this.fetchLabels();
          this.labelToEdit = null;
        } catch (error) {
          console.error("Erro ao excluir label:", error);
          alert(error.message || "Erro ao excluir label!");
        }
      }
    },

    openTaskLabelSelectionModal(task) {
      this.selectedTask = task;
      this.showTaskLabelSelectionModal = true;
    },

    async handleUpdateTaskLabels(newSelectedLabelIds) {
        if (!this.selectedTask) return;

        const currentLabelIds = new Set(this.selectedTask.labels.map(label => label.id));
        const labelsToAdd = newSelectedLabelIds.filter(id => !currentLabelIds.has(id));
        const labelsToRemove = Array.from(currentLabelIds).filter(id => !newSelectedLabelIds.includes(id));

        let hasError = false;

        for (const labelId of labelsToAdd) {
            try {
                const response = await api.linkLabelToTask(this.selectedTask.id, labelId);
                console.log(`Label ${labelId} vinculada à tarefa ${this.selectedTask.id}:`, response);
                this.updateTaskLocally(response);
            } catch (error) {
                console.error(`Erro ao vincular label ${labelId} à tarefa ${this.selectedTask.id}:`, error);
                alert(`Erro ao vincular label ${this.getLabelNameById(labelId)}: ${error.message || 'Erro desconhecido'}`);
                hasError = true;
            }
        }

        for (const labelId of labelsToRemove) {
            try {
                const response = await api.unlinkLabelFromTask(this.selectedTask.id, labelId);
                console.log(`Label ${labelId} desvinculada da tarefa ${this.selectedTask.id}:`, response);
                this.updateTaskLocally(response);
            } catch (error) {
                console.error(`Erro ao desvincular label ${labelId} da tarefa ${this.selectedTask.id}:`, error);
                alert(`Erro ao desvincular label ${this.getLabelNameById(labelId)}: ${error.message || 'Erro desconhecido'}`);
                hasError = true;
            }
        }

        this.showTaskLabelSelectionModal = false;
        this.selectedTask = null;
        if (hasError) {
            this.fetchUserData(); // Recarrega os dados se houver erros para garantir consistência
        }
    },

    updateTaskLocally(updatedTask) {
        if (!updatedTask || !updatedTask.id) return;

        for (const status in this.columns) {
            const index = this.columns[status].findIndex(t => t.id === updatedTask.id);
            if (index !== -1) {
                this.columns[status].splice(index, 1);
                break;
            }
        }
        if (this.columns[updatedTask.status]) {
            this.columns[updatedTask.status].push(updatedTask);
        } else {
            console.warn(`Status desconhecido para a tarefa atualizada: ${updatedTask.status}`);
            this.fetchUserData(); // Fallback: Recarrega todos os dados se o status for inválido
        }
    },

    getLabelNameById(labelId) {
        const label = this.labels.find(l => l.id === labelId);
        return label ? label.name : `ID ${labelId}`;
    },

    handleOpenGlobalLabelModal() {
      this.showTaskLabelSelectionModal = false;
      this.selectedTask = null;
      this.toggleLabelModal(true);
    }
  },

  async mounted() {
    await this.fetchUserData();
    await this.fetchLabels();
  },
};
</script>

<style lang="scss" scoped>
// Variáveis SCSS para cores e dimensões
$column-bg: #f4f4f4;
$column-shadow: rgba(0, 0, 0, 0.1);
$task-bg: #ffffff;
$task-shadow: rgba(0, 0, 0, 0.1);
$text-dark: #333;
$text-light: #aaa;
$text-medium: #555;
$primary-blue: #007bff;
$primary-blue-hover: #0056b3;
$delete-red: #d9534f;
$delete-red-hover: #c9302c;
$manage-labels-gray: #6c757d;
$manage-labels-gray-hover: #5a6268;
$border-light: #ccc;
$border-lighter: #ddd;
$task-gap: 8px;
$button-gap: 5px;

// Cores para status das tarefas
$status-to-do: #e0e0e0;
$status-doing: #a0d9f4;
$status-done: #a8e6a8;
$status-archived: #b0b0b0;

// Cores dos botões de controle de status
$control-archive: #343a40;
$control-to-do: #6c757d;
$control-doing: #17a2b8;
$control-done: #28a745;

// Mixin para botões
@mixin button-base($bg-color, $text-color) {
  padding: 6px 10px;
  font-size: 0.85em;
  border-radius: 4px;
  background-color: $bg-color;
  color: $text-color;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: darken($bg-color, 10%);
  }
}

.kanban-board {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px; // Adicionado padding para o board inteiro
}

.kanban-column {
  flex: 1;
  min-width: 250px;
  padding: 15px;
  background-color: $column-bg;
  border-radius: 8px;
  box-shadow: 0 4px 10px $column-shadow;
  display: flex;
  flex-direction: column;

  h2 {
    text-align: center;
    margin-bottom: 20px;
    color: $text-dark;
    font-size: 1.5em;
    border-bottom: 2px solid $border-light;
    padding-bottom: 10px;
  }
}

.kanban-task {
  background: $task-bg;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  box-shadow: 0 3px 6px $task-shadow;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: $task-gap;

  h3 {
    margin-top: 0;
    margin-bottom: 5px;
    color: $primary-blue;
  }

  p {
    font-size: 0.9em;
    color: $text-medium;
    margin-bottom: 10px;
  }

  .close-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: none;
    border: none;
    font-size: 1.6em;
    color: $text-light;
    cursor: pointer;
    transition: color 0.2s ease;

    &:hover {
      color: $delete-red;
    }
  }
}

.task-labels-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 8px;
}

.task-label-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  color: white;
  text-shadow: 0 0 3px rgba(0,0,0,0.5);
  white-space: nowrap;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.btn-manage-labels {
  @include button-base($manage-labels-gray, white);
  margin-top: 5px;
  align-self: flex-start; // Para alinhar à esquerda
}

.task-controls {
  display: flex;
  flex-wrap: wrap;
  gap: $button-gap;
  margin-top: 10px;

  button {
    flex: 1;
    min-width: 70px;
    @include button-base($primary-blue, white);

    // Sobrescrevendo cores baseadas no atributo `v-if`
    &[v-if*="archived"] { @include button-base($control-archive, white); }
    &[v-if*="toDo"] { @include button-base($control-to-do, white); }
    &[v-if*="doing"] { @include button-base($control-doing, white); }
    &[v-if*="done"] { @include button-base($control-done, white); }
  }
}

.add-task-column {
  margin-top: 20px;
  text-align: center;
  width: 100%;

  .input-container {
    margin-bottom: 10px;
  }

  input {
    width: calc(100% - 20px);
    padding: 10px;
    border: 1px solid $border-lighter;
    border-radius: 5px;
    font-size: 1em;
  }

  button {
    width: 100%;
    padding: 10px;
    @include button-base($primary-blue, white);
    font-size: 1.2em;
  }
}

// Classes de cor de fundo das tarefas por status
.task-to-do {
  background-color: $status-to-do;
}

.task-doing {
  background-color: $status-doing;
}

.task-done {
  background-color: $status-done;
}

.task-archived {
  background-color: $status-archived;
}
.nome-profile{
  text-align: center;
  display: flex;
  color: white;
  background: #30ABD3;
  position: absolute;
  top:10px;
  padding: 5px;
  right: 22%;
  border-radius: 8px;
}
</style>