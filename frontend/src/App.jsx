import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaRobot, FaSync, FaPlay, FaPause, 
  FaTicketAlt, FaCheckCircle, FaClock, FaExclamationTriangle,
  FaChevronDown, FaChevronUp, FaPaperPlane, FaSpinner, FaDatabase, FaHistory
} from 'react-icons/fa';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({ total_traites: 0, processed_ids: [], tickets_data: [] });
  const [agentRunning, setAgentRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expandedTicket, setExpandedTicket] = useState(null);
  const [processingId, setProcessingId] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  // ==========================================
  // FONCTIONS API
  // ==========================================
  const fetchTickets = async () => {
    try {
      const response = await axios.get(`${API_URL}/tickets?limit=50`);
      setTickets(response.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des tickets');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Erreur stats:', error);
    }
  };

  const fetchAgentStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/agent/status`);
      setAgentRunning(response.data.running);
    } catch (error) {
      console.error('Erreur statut agent:', error);
    }
  };

  const toggleAgent = async () => {
    try {
      setLoading(true);
      if (agentRunning) {
        await axios.post(`${API_URL}/agent/stop`);
        toast.success(' Agent arrêté');
        setAgentRunning(false);
      } else {
        await axios.post(`${API_URL}/agent/start`);
        toast.success('Agent démarré');
        setAgentRunning(true);
      }
      setTimeout(() => {
        fetchTickets();
        fetchStats();
        fetchAgentStatus();
        setLoading(false);
      }, 2000);
    } catch (error) {
      toast.error(' Erreur lors du changement d\'état');
      fetchAgentStatus();
      setLoading(false);
    }
  };

  const handleProcessTicket = async (ticketId) => {
    setProcessingId(ticketId);
    toast.loading(`Traitement du ticket #${ticketId}...`, { id: 'processing' });
    try {
      await axios.post(`${API_URL}/tickets/${ticketId}/process`);
      toast.success(` Ticket #${ticketId} traité avec succès !`, { id: 'processing' });
      await Promise.all([fetchTickets(), fetchStats()]);
    } catch (error) {
      toast.error(` Erreur lors du traitement du ticket #${ticketId}`, { id: 'processing' });
      console.error(error);
    } finally {
      setProcessingId(null);
    }
  };

  // ==========================================
  // EFFET DE CHARGEMENT
  // ==========================================
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTickets(), fetchStats(), fetchAgentStatus()]);
      setLoading(false);
    };
    loadData();

    const interval = setInterval(() => {
      fetchTickets();
      fetchStats();
      fetchAgentStatus();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  // ==========================================
  // STATISTIQUES CORRIGÉES
  // ==========================================
  const totalTickets = tickets.length;
  const openTickets = tickets.filter(t => t.status === 'Open').length;
  const closedTickets = tickets.filter(t => t.status === 'Closed').length;

  // 📌 En attente = Total tickets - Tickets déjà traités (peu importe le statut)
  const processedIds = stats.processed_ids || [];
  const pendingTickets = totalTickets - processedIds.length;

  const autoProcessed = stats.total_traites || 0;
  const dataCollected = stats.tickets_data?.length || 0;

  // Pour debug - voir dans la console
  useEffect(() => {
    console.log(' Stats debug:');
    console.log('   Total tickets:', totalTickets);
    console.log('   Processed IDs:', processedIds);
    console.log('   En attente:', pendingTickets);
  }, [totalTickets, processedIds, pendingTickets]);

  // ==========================================
  // RENDU
  // ==========================================
  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-3">
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 20, repeat: Infinity, ease: "linear" }}>
                <FaRobot className="text-3xl text-white" />
              </motion.div>
              <h1 className="text-2xl font-bold text-white">Zoho Agent</h1>
              <span className="px-2 py-1 text-xs font-semibold text-blue-100 bg-blue-500/30 rounded-full">
                v2.0
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${agentRunning ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
                <div className={`w-2 h-2 rounded-full ${agentRunning ? 'bg-green-400 animate-pulse' : 'bg-gray-400'}`} />
                <span className="text-sm text-white">{agentRunning ? 'Actif' : 'Pause'}</span>
              </div>
              <button
                onClick={toggleAgent}
                disabled={loading}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  loading ? 'opacity-50 cursor-not-allowed' :
                  agentRunning 
                    ? 'bg-yellow-500 hover:bg-yellow-600 text-white' 
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {loading ? (
                  <FaSpinner className="inline animate-spin mr-1" />
                ) : agentRunning ? (
                  <FaPause className="inline mr-1" />
                ) : (
                  <FaPlay className="inline mr-1" />
                )}
                {loading ? 'Chargement...' : agentRunning ? 'Pause' : 'Démarrer'}
              </button>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="px-3 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center space-x-2"
              >
                <FaHistory />
                <span className="text-sm">Historique</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* STATS CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <StatCard 
            icon={<FaTicketAlt className="text-blue-500" />} 
            value={totalTickets} 
            label="Total tickets" 
            color="blue" 
            delay={0} 
          />
          <StatCard 
            icon={<FaExclamationTriangle className="text-yellow-500" />} 
            value={openTickets} 
            label="Ouverts" 
            color="yellow" 
            delay={0.1} 
          />
          <StatCard 
            icon={<FaClock className="text-purple-500" />} 
            value={pendingTickets} 
            label="En attente" 
            color="purple" 
            delay={0.2} 
          />
          <StatCard 
            icon={<FaCheckCircle className="text-green-500" />} 
            value={autoProcessed} 
            label="Traités auto" 
            color="green" 
            delay={0.3} 
          />
          <StatCard 
            icon={<FaDatabase className="text-indigo-500" />} 
            value={dataCollected} 
            label="Données RAG" 
            color="indigo" 
            delay={0.4} 
          />
        </div>

        {/* ACTIONS */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button 
            onClick={() => { fetchTickets(); fetchStats(); }} 
            disabled={loading} 
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2 disabled:opacity-50"
          >
            <FaSync className={`${loading ? 'animate-spin' : ''}`} />
            <span>Rafraîchir</span>
          </button>
          <span className={`text-sm flex items-center ${pendingTickets > 0 ? 'text-red-500 font-medium' : 'text-green-500'}`}>
            {agentRunning 
              ? ' Agent actif - Traitement automatique en cours' 
              : pendingTickets > 0 
                ? ` ${pendingTickets} ticket(s) en attente - Cliquez sur "Démarrer"` 
                : ' Aucun ticket en attente'
            }
          </span>
        </div>

        {/* TICKETS LIST */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h2 className="font-semibold text-gray-700"> Tickets récents</h2>
            <span className="text-sm text-gray-500">
              {tickets.length} ticket(s) - 
              <span className="text-green-600 ml-1">{processedIds.length} traités</span>
              {closedTickets > 0 && (
                <span className="text-gray-400 ml-2">({closedTickets} fermés)</span>
              )}
            </span>
          </div>
          
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent" />
              <span className="ml-3 text-gray-500">Chargement des tickets...</span>
            </div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FaTicketAlt className="mx-auto text-4xl text-gray-300 mb-3" />
              <p>Aucun ticket trouvé</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {tickets.map((ticket, index) => (
                <TicketCard
                  key={ticket.id}
                  ticket={ticket}
                  index={index}
                  onProcess={handleProcessTicket}
                  isExpanded={expandedTicket === ticket.id}
                  onToggleExpand={() => setExpandedTicket(expandedTicket === ticket.id ? null : ticket.id)}
                  isProcessing={processingId === ticket.id}
                  agentRunning={agentRunning}
                  isProcessed={processedIds.includes(String(ticket.id))}
                />
              ))}
            </div>
          )}
        </div>

        {/* HISTORIQUE DES RÉPONSES */}
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
              <h2 className="font-semibold text-gray-700"> Historique des réponses</h2>
              <span className="text-sm text-gray-500">{stats.tickets_data?.length || 0} réponse(s)</span>
            </div>
            {stats.tickets_data && stats.tickets_data.length > 0 ? (
              <div className="divide-y divide-gray-100 max-h-96 overflow-y-auto">
                {stats.tickets_data.slice().reverse().map((item, index) => (
                  <div key={index} className="px-6 py-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sm font-semibold text-gray-500">#{item.id}</span>
                      <span className="text-xs text-gray-400">{item.date_traitement}</span>
                    </div>
                    <p className="text-sm font-medium text-gray-700 mt-1">{item.sujet}</p>
                    <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                      <span className="font-semibold">Réponse :</span> {item.reponse_agent}
                    </div>
                    <div className="mt-1 text-xs text-gray-400">
                      Catégorie: {item.analyse?.categorie || 'N/A'} | Urgence: {item.analyse?.urgence || 'N/A'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">Aucune donnée collectée</div>
            )}
          </motion.div>
        )}

        <div className="mt-8 text-center text-xs text-gray-400 border-t border-gray-200 pt-4">
          Zoho Agent v2.0 • {new Date().toLocaleString()}
        </div>
      </main>
    </div>
  );
}

// ==========================================
// COMPOSANT STAT CARD
// ==========================================
function StatCard({ icon, value, label, color, delay }) {
  const colors = {
    blue: 'bg-blue-50 border-blue-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200',
    indigo: 'bg-indigo-50 border-indigo-200',
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`rounded-xl border p-6 ${colors[color]} hover:shadow-md transition-shadow duration-300`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-3xl font-bold text-gray-800">{value}</div>
          <div className="text-sm text-gray-600 mt-1">{label}</div>
        </div>
        <div className="text-3xl opacity-60">{icon}</div>
      </div>
    </motion.div>
  );
}

// ==========================================
// COMPOSANT TICKET CARD
// ==========================================
function TicketCard({ ticket, index, onProcess, isExpanded, onToggleExpand, isProcessing, agentRunning, isProcessed }) {
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

  const cleanDescription = (html) => {
    if (!html) return 'Aucune description disponible';
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || 'Aucune description disponible';
  };

  const description = ticket.description ? cleanDescription(ticket.description) : 'Aucune description disponible';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`px-6 py-4 hover:bg-gray-50 transition-colors group ${isProcessed ? 'bg-green-50/30' : ''}`}
    >
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex-1 min-w-0 cursor-pointer" onClick={onToggleExpand}>
          <div className="flex items-center space-x-3">
            <span className="font-mono text-sm font-semibold text-gray-500">#{ticket.id}</span>
            <div className={`w-2 h-2 rounded-full ${statusDot[ticket.status] || 'bg-gray-400'}`} />
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${statusColors[ticket.status] || 'bg-gray-100 text-gray-800'}`}>
              {ticket.status}
            </span>
            {isProcessed && (
              <span className="text-xs text-green-600 font-medium"> Traité</span>
            )}
            {agentRunning && ticket.status === 'Open' && !isProcessed && (
              <span className="text-xs text-green-600 animate-pulse"> En traitement...</span>
            )}
            <span className="text-xs text-gray-400">{ticket.date || 'N/A'}</span>
          </div>
          <p className="text-gray-800 font-medium truncate mt-1">{ticket.subject || 'Sans sujet'}</p>
          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
            {description.length > 100 ? description.substring(0, 100) + '...' : description}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onToggleExpand}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title={isExpanded ? 'Réduire' : 'Développer'}
          >
            {isExpanded ? <FaChevronUp className="text-xs" /> : <FaChevronDown className="text-xs" />}
          </button>
          <button
            onClick={() => onProcess(ticket.id)}
            disabled={isProcessing || agentRunning || isProcessed}
            className={`px-4 py-1.5 text-sm rounded-lg transition-colors flex items-center space-x-1 ${
              isProcessing || agentRunning || isProcessed
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
            }`}
          >
            {isProcessing ? (
              <FaSpinner className="animate-spin text-xs" />
            ) : (
              <FaPaperPlane className="text-xs" />
            )}
            <span>{isProcessing ? 'En cours...' : isProcessed ? 'Traité' : agentRunning ? 'Auto' : 'Poster'}</span>
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 pt-3 border-t border-gray-100"
          >
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{description}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default App;