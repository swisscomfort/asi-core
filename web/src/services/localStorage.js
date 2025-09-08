// Simple localStorage wrapper for ASI-Core
export const localStorageService = {
  // Get all reflections from localStorage
  getReflections: () => {
    try {
      const stored = localStorage.getItem("asi-reflections");
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error("Error getting reflections:", error);
      return [];
    }
  },

  // Save a reflection to localStorage
  saveReflection: (reflection) => {
    try {
      const reflections = localStorageService.getReflections();
      reflections.push({
        ...reflection,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      });
      localStorage.setItem("asi-reflections", JSON.stringify(reflections));
      return true;
    } catch (error) {
      console.error("Error saving reflection:", error);
      return false;
    }
  },

  // Get all todos from localStorage
  getTodos: () => {
    try {
      const stored = localStorage.getItem("asi-todos");
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error("Error getting todos:", error);
      return [];
    }
  },

  // Save a todo to localStorage
  saveTodo: (todo) => {
    try {
      const todos = localStorageService.getTodos();
      todos.push({
        ...todo,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      });
      localStorage.setItem("asi-todos", JSON.stringify(todos));
      return true;
    } catch (error) {
      console.error("Error saving todo:", error);
      return false;
    }
  },

  // Initialize localStorage
  init: () => {
    try {
      // Test localStorage availability
      localStorage.setItem("asi-test", "test");
      localStorage.removeItem("asi-test");
      return true;
    } catch (error) {
      console.error("localStorage not available:", error);
      return false;
    }
  },

  // Get storage stats
  getStats: () => {
    const reflections = localStorageService.getReflections();
    const todos = localStorageService.getTodos();

    return {
      totalReflections: reflections.length,
      totalTodos: todos.length,
      totalItems: reflections.length + todos.length,
      lastUpdate: new Date().toISOString(),
    };
  },
};

export default localStorageService;
