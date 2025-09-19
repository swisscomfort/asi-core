import React, { useState, useEffect } from "react";
import {
  CheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { localStorageService } from "../services/localStorage";
import { updateTodoStatus, TODO_STATUSES } from "../core/data-model";

export const TodoList = ({ onTodoSelect }) => {
  const [todos, setTodos] = useState([]);
  const [filter, setFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadTodos();
  }, []);

  const loadTodos = async () => {
    setIsLoading(true);
    try {
      const allTodos = await localStorageService.getAllTodos();
      setTodos(
        allTodos.sort((a, b) => new Date(b.created) - new Date(a.created))
      );
    } catch (error) {
      console.error("Fehler beim Laden der To-Dos:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = async (todo, newStatus) => {
    try {
      const updatedTodo = updateTodoStatus(todo, newStatus);
      await localStorageService.updateTodo(updatedTodo);
      await loadTodos();
    } catch (error) {
      console.error("Fehler beim Aktualisieren des To-Do Status:", error);
    }
  };

  const filteredTodos = todos.filter((todo) => {
    switch (filter) {
      case "pending":
        return todo.status === TODO_STATUSES.PENDING;
      case "completed":
        return todo.status === TODO_STATUSES.COMPLETED;
      case "overdue":
        return (
          todo.dueDate &&
          new Date(todo.dueDate) < new Date() &&
          todo.status !== TODO_STATUSES.COMPLETED
        );
      default:
        return true;
    }
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "urgent":
        return "text-red-600 bg-red-50";
      case "high":
        return "text-orange-600 bg-orange-50";
      case "medium":
        return "text-yellow-600 bg-yellow-50";
      case "low":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case TODO_STATUSES.COMPLETED:
        return <CheckIcon className="w-5 h-5 text-green-600" />;
      case TODO_STATUSES.IN_PROGRESS:
        return <ClockIcon className="w-5 h-5 text-blue-600" />;
      default:
        return <div className="w-5 h-5 border-2 border-gray-300 rounded" />;
    }
  };

  const isOverdue = (todo) => {
    return (
      todo.dueDate &&
      new Date(todo.dueDate) < new Date() &&
      todo.status !== TODO_STATUSES.COMPLETED
    );
  };

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 text-2xl mb-2">⏳</div>
        <p className="text-gray-600">Lade To-Dos...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { key: "all", label: "Alle", count: todos.length },
          {
            key: "pending",
            label: "Offen",
            count: todos.filter((t) => t.status === TODO_STATUSES.PENDING)
              .length,
          },
          {
            key: "completed",
            label: "Erledigt",
            count: todos.filter((t) => t.status === TODO_STATUSES.COMPLETED)
              .length,
          },
          {
            key: "overdue",
            label: "Überfällig",
            count: todos.filter((t) => isOverdue(t)).length,
          },
        ].map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              filter === key
                ? "bg-white text-indigo-600 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {label}{" "}
            {count > 0 && <span className="text-xs opacity-75">({count})</span>}
          </button>
        ))}
      </div>

      {/* Todo List */}
      <div className="space-y-2">
        {filteredTodos.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 text-4xl mb-4">✅</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === "all"
                ? "Keine To-Dos gefunden"
                : `Keine ${
                    filter === "pending"
                      ? "offenen"
                      : filter === "completed"
                      ? "erledigten"
                      : "überfälligen"
                  } To-Dos`}
            </h3>
            <p className="text-gray-600">
              {filter === "all"
                ? "Erstelle dein erstes To-Do!"
                : "Wähle einen anderen Filter oder erstelle neue To-Dos."}
            </p>
          </div>
        ) : (
          filteredTodos.map((todo) => (
            <div
              key={todo.id}
              className={`p-4 bg-white border rounded-lg hover:shadow-sm transition-shadow cursor-pointer ${
                isOverdue(todo) ? "border-red-200 bg-red-50" : "border-gray-200"
              }`}
              onClick={() => onTodoSelect && onTodoSelect(todo)}
            >
              <div className="flex items-start space-x-3">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    const newStatus =
                      todo.status === TODO_STATUSES.COMPLETED
                        ? TODO_STATUSES.PENDING
                        : TODO_STATUSES.COMPLETED;
                    handleStatusChange(todo, newStatus);
                  }}
                  className="mt-1"
                >
                  {getStatusIcon(todo.status)}
                </button>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4
                      className={`text-sm font-medium ${
                        todo.status === TODO_STATUSES.COMPLETED
                          ? "line-through text-gray-500"
                          : "text-gray-900"
                      }`}
                    >
                      {todo.title || todo.content.substring(0, 50)}
                      {todo.content.length > 50 && "..."}
                    </h4>

                    <div className="flex items-center space-x-2">
                      {isOverdue(todo) && (
                        <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
                      )}
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(
                          todo.priority
                        )}`}
                      >
                        {todo.priority}
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-600 mt-1">
                    {todo.content.length > 100
                      ? todo.content.substring(0, 100) + "..."
                      : todo.content}
                  </p>

                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>
                        Erstellt:{" "}
                        {new Date(todo.created).toLocaleDateString("de-DE")}
                      </span>
                      {todo.dueDate && (
                        <span
                          className={
                            isOverdue(todo) ? "text-red-600 font-medium" : ""
                          }
                        >
                          • Fällig:{" "}
                          {new Date(todo.dueDate).toLocaleDateString("de-DE")}
                        </span>
                      )}
                    </div>

                    {todo.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {todo.tags.slice(0, 3).map((tag, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {todo.tags.length > 3 && (
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                            +{todo.tags.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
