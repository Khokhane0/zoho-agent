import React from 'react';
import { motion } from 'framer-motion';
import { FaTicketAlt, FaExclamationTriangle, FaCheckCircle, FaRobot } from 'react-icons/fa';

function StatsCards({ tickets, stats }) {
  const openCount = tickets.filter(t => t.status === 'Open').length;
  const closedCount = tickets.filter(t => t.status === 'Closed').length;

  const cards = [
    { icon: <FaTicketAlt className="text-blue-500" />, value: tickets.length, label: "Total tickets", color: "blue" },
    { icon: <FaExclamationTriangle className="text-yellow-500" />, value: openCount, label: "Ouverts", color: "yellow" },
    { icon: <FaCheckCircle className="text-green-500" />, value: closedCount, label: "Fermés", color: "green" },
    { icon: <FaRobot className="text-purple-500" />, value: stats.total_traites || 0, label: "Traités auto", color: "purple" },
  ];

  const colors = {
    blue: 'bg-blue-50 border-blue-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200',
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`rounded-xl border p-6 ${colors[card.color]} hover:shadow-md transition-shadow duration-300`}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-gray-800">{card.value}</div>
              <div className="text-sm text-gray-600 mt-1">{card.label}</div>
            </div>
            <div className="text-3xl opacity-60">{card.icon}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

export default StatsCards;