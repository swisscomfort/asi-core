export const NOTE_TYPES = {
  REFLECTION: "reflection",
  NOTE: "note",
  TODO: "todo",
};

export const TODO_STATUSES = {
  PENDING: "pending",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  DELEGATED: "delegated",
  CANCELLED: "cancelled",
};

export const TODO_PRIORITIES = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  URGENT: "urgent",
};

export const createReflection = (content, tags = [], shared = false) => {
  return {
    type: NOTE_TYPES.REFLECTION,
    content,
    tags,
    shared,
    timestamp: new Date().toISOString(),
    id: generateId(),
  };
};

export const createNote = (content, tags = [], shared = false) => {
  return {
    type: NOTE_TYPES.NOTE,
    content,
    tags,
    shared,
    timestamp: new Date().toISOString(),
    id: generateId(),
  };
};

export const createTodo = (
  content,
  tags = [],
  dueDate = null,
  priority = TODO_PRIORITIES.MEDIUM,
  shared = false
) => {
  return {
    type: NOTE_TYPES.TODO,
    content,
    tags,
    status: TODO_STATUSES.PENDING,
    priority,
    created: new Date().toISOString(),
    dueDate,
    completed: null,
    shared,
    history: [
      {
        action: "created",
        timestamp: new Date().toISOString(),
        status: TODO_STATUSES.PENDING,
      },
    ],
    id: generateId(),
  };
};

export const updateTodoStatus = (todo, newStatus) => {
  const updated = {
    ...todo,
    status: newStatus,
    history: [
      ...todo.history,
      {
        action: "status_changed",
        timestamp: new Date().toISOString(),
        status: newStatus,
        previousStatus: todo.status,
      },
    ],
  };

  if (newStatus === TODO_STATUSES.COMPLETED) {
    updated.completed = new Date().toISOString();
  }

  return updated;
};

const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};
