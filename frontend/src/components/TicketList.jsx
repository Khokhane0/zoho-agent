import React from 'react';
import { motion } from 'framer-motion';
import { FaTicketAlt } from 'react-icons/fa';
import TicketCard from './TicketCard';

function TicketList({ tickets, loading, onProcessTicket }) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
          <span className="ml-3 text-gray-500">Chargement des tickets...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h2 className="font-semibold text-gray-700">📋 Tickets récents</h2>
        <span className="text-sm text-gray-500">{tickets.length} ticket(s)</span>
      </div>

      {tickets.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <FaTicketAlt className="mx-auto text-4xl text-gray-300 mb-3" />
          <p>Aucun ticket trouvé</p>
          <p className="text-sm text-gray-400 mt-1">Les tickets apparaîtront ici automatiquement</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100">
          {tickets.map((ticket, index) => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              index={index}
              onProcess={onProcessTicket}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TicketList;