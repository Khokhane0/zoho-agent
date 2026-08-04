import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaRobot, FaSync } from 'react-icons/fa';
import { Toaster, toast } from 'react-hot-toast';
import StatsCards from './StatsCards';
import Controls from './Controls';
import TicketList from './TicketList';
import { getTickets, getStats, processTicket, processAllTickets } from '../services/api';

function Dashboard() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({ total_traites: 0 });
  const [loading, setLoading] = useState(true);
  const [agentRunning, setAgentRunning] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ticketsData, statsData] = await Promise.all([
        getTickets(10),
        getStats()
      ]);
      setTickets(ticketsData);
      setStats(statsData);
    } catch (error) {
      toast.error('Erreur de chargement des données');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      if (agentRunning) loadData();
    }, 30000);
    return () => clearInterval(interval);
  }, [agentRunning]);

  const handleProcessTicket = async (ticketId) => {
    toast.loading(`Traitement du ticket #${ticketId}...`, { id: 'processing' });
    try {
      await processTicket(ticketId);
      toast.success(`Ticket #${ticketId} traité !`, { id: 'processing' });
      loadData();
    } catch (error) {
      toast.error(`Erreur sur #${ticketId}`, { id: 'processing' });
    }
  };

  const handleProcessAll = async () => {
    const openTickets = tickets.filter(t => t.status === 'Open');
    if (openTickets.length === 0) {
      toast('Aucun ticket ouvert à traiter');
      return;
    }
    try {
      await processAllTickets(openTickets.map(t => t.id));
      loadData();
    } catch (error) {
      toast.error('Erreur lors du traitement en masse');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
              >
                <FaRobot className="text-3xl text-white" />
              </motion.div>
              <h1 className="text-2xl font-bold text-white">Zoho Agent</h1>
              <span className="px-2 py-1 text-xs font-semibold text-blue-100 bg-blue-500/30 rounded-full">
                v1.0
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${agentRunning ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
                <div className={`w-2 h-2 rounded-full ${agentRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                <span className="text-sm text-white">{agentRunning ? 'Actif' : 'Pause'}</span>
              </div>
              <button
                onClick={() => setAgentRunning(!agentRunning)}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  agentRunning 
                    ? 'bg-yellow-500 hover:bg-yellow-600 text-white' 
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {agentRunning ? '⏸ Pause' : '▶ Démarrer'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="container mx-auto px-6 py-8">
        <StatsCards tickets={tickets} stats={stats} />
        
        <Controls 
          onRefresh={loadData} 
          onProcessAll={handleProcessAll}
          loading={loading}
          ticketsCount={tickets.length}
        />

        <TicketList 
          tickets={tickets} 
          loading={loading} 
          onProcessTicket={handleProcessTicket}
        />
      </main>
    </div>
  );
}

export default Dashboard;