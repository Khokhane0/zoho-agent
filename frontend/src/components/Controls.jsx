import React from 'react';
import { FaSync, FaPlay, FaRobot } from 'react-icons/fa';
import { motion } from 'framer-motion';

function Controls({ onRefresh, onProcessAll, loading, ticketsCount }) {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-wrap gap-4 mb-8"
    >
      <button
        onClick={onRefresh}
        disabled={loading}
        className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <FaSync className={`${loading ? 'animate-spin' : ''}`} />
        <span>Rafraîchir</span>
      </button>

      <button
        onClick={onProcessAll}
        disabled={ticketsCount === 0}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <FaPlay className="text-sm" />
        <span>Traiter tous les tickets</span>
      </button>

      {ticketsCount === 0 && (
        <span className="text-sm text-gray-400 flex items-center">
          Aucun ticket disponible
        </span>
      )}
    </motion.div>
  );
}

export default Controls;