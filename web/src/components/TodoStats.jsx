import React, { useState, useEffect } from "react";
import { localStorage } from "../services/localStorage";

export const TodoStats = () => {
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    completed: 0,
    overdue: 0,
    completionRate: 0,
    insights: [],
  });

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const todos = await localStorageService.getAllTodos();
      const now = new Date();

      const pending = todos.filter((t) => t.status === "pending").length;
      const completed = todos.filter((t) => t.status === "completed").length;
      const overdue = todos.filter(
        (t) =>
          t.dueDate && new Date(t.dueDate) < now && t.status !== "completed"
      ).length;

      const completionRate =
        todos.length > 0 ? (completed / todos.length) * 100 : 0;

      // Generate insights
      const insights = generateInsights(todos);

      setStats({
        total: todos.length,
        pending,
        completed,
        overdue,
        completionRate: Math.round(completionRate),
        insights,
      });
    } catch (error) {
      console.error("Fehler beim Laden der To-Do Statistiken:", error);
    }
  };

  const generateInsights = (todos) => {
    const insights = [];

    if (todos.length === 0) return insights;

    // Completion rate insight
    const completionRate =
      todos.filter((t) => t.status === "completed").length / todos.length;
    if (completionRate > 0.8) {
      insights.push({
        type: "positive",
        message: `Starke Leistung! Du erledigst ${Math.round(
          completionRate * 100
        )}% deiner To-Dos.`,
      });
    } else if (completionRate < 0.5) {
      insights.push({
        type: "warning",
        message: `Nur ${Math.round(
          completionRate * 100
        )}% deiner To-Dos werden erledigt. Weniger planen, mehr fokussieren?`,
      });
    }

    // Overdue insight
    const overdue = todos.filter(
      (t) =>
        t.dueDate &&
        new Date(t.dueDate) < new Date() &&
        t.status !== "completed"
    );

    if (overdue.length > 0) {
      insights.push({
        type: "warning",
        message: `${overdue.length} To-Do${
          overdue.length > 1 ? "s sind" : " ist"
        } überfällig. Zeit für eine Prioritätsprüfung!`,
      });
    }

    // Tag pattern insight
    const tagCounts = {};
    todos.forEach((todo) => {
      todo.tags.forEach((tag) => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      });
    });

    const topTag = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])[0];
    if (topTag && topTag[1] > 3) {
      insights.push({
        type: "info",
        message: `"${topTag[0]}" ist dein häufigstes To-Do-Thema mit ${topTag[1]} Einträgen.`,
      });
    }

    // Weekly pattern
    const thisWeek = todos.filter((t) => {
      const todoDate = new Date(t.created);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return todoDate > weekAgo;
    });

    if (thisWeek.length > 0) {
      const completedThisWeek = thisWeek.filter(
        (t) => t.status === "completed"
      ).length;
      const weeklyRate = completedThisWeek / thisWeek.length;

      if (weeklyRate > 0.7) {
        insights.push({
          type: "positive",
          message: `Diese Woche läuft gut! ${completedThisWeek} von ${thisWeek.length} To-Dos erledigt.`,
        });
      }
    }

    return insights.slice(0, 3); // Max 3 insights
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case "positive":
        return "🎉";
      case "warning":
        return "⚠️";
      case "info":
        return "💡";
      default:
        return "📊";
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case "positive":
        return "bg-green-50 text-green-800 border-green-200";
      case "warning":
        return "bg-orange-50 text-orange-800 border-orange-200";
      case "info":
        return "bg-blue-50 text-blue-800 border-blue-200";
      default:
        return "bg-gray-50 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        ✅ To-Do Statistiken
        {stats.overdue > 0 && (
          <span className="ml-2 bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
            {stats.overdue} überfällig
          </span>
        )}
      </h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-indigo-600">
            {stats.total}
          </div>
          <div className="text-xs text-gray-600">Gesamt</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">
            {stats.pending}
          </div>
          <div className="text-xs text-gray-600">Offen</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {stats.completed}
          </div>
          <div className="text-xs text-gray-600">Erledigt</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
          <div className="text-xs text-gray-600">Überfällig</div>
        </div>
      </div>

      {/* Completion Rate */}
      {stats.total > 0 && (
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Abschlussrate</span>
            <span className="font-medium">{stats.completionRate}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${stats.completionRate}%` }}
            />
          </div>
        </div>
      )}

      {/* Insights */}
      {stats.insights.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-900">KI-Insights</h3>
          {stats.insights.map((insight, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border text-sm ${getInsightColor(
                insight.type
              )}`}
            >
              <div className="flex items-start space-x-2">
                <span className="text-lg">{getInsightIcon(insight.type)}</span>
                <p className="flex-1">{insight.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
