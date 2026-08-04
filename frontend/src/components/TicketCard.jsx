import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaPlay, FaChevronDown, FaChevronUp } from 'react-icons/fa';

function TicketCard({ ticket, index, onProcess }) {
  const [expanded, setExpanded] = useState(false);

  const statusColors = {
    'Open': 'bg-yellow-100 text-yellow-800',
    'Closed': 'bg-green-100 text-green-800',
    'Pending': 'bg-blue-100 text-blue-800',
    'In Progress': 'bg-purple-100 text-purple-800',
  };

  const statusDot = {
    'Open': 'bg-yellow-500',
    'Closed': 'bg-green-500',
    'Pending': 'bg-blue-500',
    'In Progress': 'bg-purple-500',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="px-6 py-4 hover:bg-gray-50 transition-colors group"
    >
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex-1 min-w-0 cursor-pointer" onClick={() => setExpanded(!expanded)}>
          <div className="flex items-center space-x-3">
            <span className="font-mono text-sm font-semibold text-gray-500">
              #{ticket.id}
            </span>
            <div className={`w-2 h-2 rounded-full ${statusDot[ticket.status] || 'bg-gray-400'}`} />
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColors[ticket.status] || 'bg-gray-100 text-gray-800'}`}>
              {ticket.status}
            </span>
            <span className="text-xs text-gray-400">
              {ticket.date || 'N/A'}
            </span>
          </div>
          <p className="text-gray-800 font-medium truncate mt-1">
            {ticket.subject}
          </p>
          {ticket.description && expanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg"
            >
              {ticket.description.substring(0, 300)}
              {ticket.description.length > 300 && '...'}
            </motion.div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title={expanded ? 'Réduire' : 'Développer'}
          >
            {expanded ? <FaChevronUp className="text-xs" /> : <FaChevronDown className="text-xs" />}
          </button>
          <button
            onClick={() => onProcess(ticket.id)}
            className="px-4 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center space-x-1"
          >
            <FaPlay className="text-xs" />
            <span>Traiter</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export default TicketCard;