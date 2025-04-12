import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell 
} from 'recharts';

// Main App Component
const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/judges" element={<JudgeSearch />} />
            <Route path="/judges/:judgeId" element={<JudgeProfile />} />
            <Route path="/cases/predict" element={<CasePrediction />} />
            <Route path="/simulations/new" element={<NewSimulation />} />
            <Route path="/simulations/:simulationId" element={<SimulationSession />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

// Header Component
const Header = () => {
  return (
    <header className="bg-indigo-700 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.25v-3.5m0 18v-3.5m-7.5-1.5h15m-15-7h15m-7.5 10c4.142 0 7.5-3.358 7.5-7.5 0-4.142-3.358-7.5-7.5-7.5-4.142 0-7.5 3.358-7.5 7.5 0 4.142 3.358 7.5 7.5 7.5z" />
          </svg>
          <h1 className="text-2xl font-bold">Litigation Simulator</h1>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li><NavLink to="/">Dashboard</NavLink></li>
            <li><NavLink to="/judges">Judges</NavLink></li>
            <li><NavLink to="/cases/predict">Predict</NavLink></li>
            <li><NavLink to="/simulations/new">New Simulation</NavLink></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

// Navigation Link Component
const NavLink = ({ to, children }) => {
  const navigate = useNavigate();
  const [isActive, setIsActive] = useState(false);
  
  useEffect(() => {
    setIsActive(window.location.pathname === to);
  }, [to]);
  
  return (
    <Link 
      to={to} 
      className={`hover:text-indigo-200 transition-colors ${isActive ? 'font-bold border-b-2 border-indigo-400' : ''}`}
    >
      {children}
    </Link>
  );
};

// Footer Component
const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm">© 2025 Litigation Simulator. All rights reserved.</p>
          </div>
          <div className="flex space-x-4">
            <a href="#" className="text-gray-400 hover:text-white">Terms</a>
            <a href="#" className="text-gray-400 hover:text-white">Privacy</a>
            <a href="#" className="text-gray-400 hover:text-white">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

// Dashboard Component
const Dashboard = () => {
  const navigate = useNavigate();
  const [recentSimulations, setRecentSimulations] = useState([]);
  const [stats, setStats] = useState({
    completedSimulations: 0,
    predictions: 0,
    avgAccuracy: 0
  });
  
  useEffect(() => {
    // Fetch recent simulations (mock data for now)
    setRecentSimulations([
      { id: 'sim_20250410123456', case_type: 'lease_dispute', date: '2025-04-10T12:34:56', rounds: 3 },
      { id: 'sim_20250409091023', case_type: 'foreclosure', date: '2025-04-09T09:10:23', rounds: 5 }
    ]);
    
    // Fetch stats (mock data)
    setStats({
      completedSimulations: 12,
      predictions: 34,
      avgAccuracy: 0.78
    });
  }, []);
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Welcome to the Litigation Simulator</h2>
        <p className="text-gray-600 mb-6">
          Prepare for your legal proceedings with data-driven simulations and predictions based on
          real case outcomes and judicial behavior patterns.
        </p>
        <div className="flex flex-wrap gap-4">
          <button 
            onClick={() => navigate('/judges')}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
          >
            Analyze Judge
          </button>
          <button 
            onClick={() => navigate('/cases/predict')}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
          >
            Predict Case Outcome
          </button>
          <button 
            onClick={() => navigate('/simulations/new')}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
          >
            Start New Simulation
          </button>
        </div>
      </section>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Simulations" value={stats.completedSimulations} icon="sim" />
        <StatCard title="Predictions" value={stats.predictions} icon="predict" />
        <StatCard title="Avg. Accuracy" value={`${Math.round(stats.avgAccuracy * 100)}%`} icon="accuracy" />
      </div>
      
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Recent Simulations</h3>
        {recentSimulations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead>
                <tr className="bg-gray-100">
                  <th className="py-2 px-4 text-left">ID</th>
                  <th className="py-2 px-4 text-left">Case Type</th>
                  <th className="py-2 px-4 text-left">Date</th>
                  <th className="py-2 px-4 text-left">Rounds</th>
                  <th className="py-2 px-4 text-left">Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentSimulations.map(sim => (
                  <tr key={sim.id} className="border-t">
                    <td className="py-2 px-4">{sim.id}</td>
                    <td className="py-2 px-4">{sim.case_type}</td>
                    <td className="py-2 px-4">{new Date(sim.date).toLocaleString()}</td>
                    <td className="py-2 px-4">{sim.rounds}</td>
                    <td className="py-2 px-4">
                      <button 
                        onClick={() => navigate(`/simulations/${sim.id}`)}
                        className="text-indigo-600 hover:text-indigo-800"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">No recent simulations found.</p>
        )}
      </section>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, icon }) => {
  const iconMap = {
    sim: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
    predict: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    accuracy: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center space-x-4">
        <div className="p-3 bg-indigo-100 text-indigo-700 rounded-full">
          {iconMap[icon]}
        </div>
        <div>
          <p className="text-gray-500">{title}</p>
          <p className="text-3xl font-semibold text-gray-800">{value}</p>
        </div>
      </div>
    </div>
  );
};

// Judge Search Component
const JudgeSearch = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSearch = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Mock API call
    setTimeout(() => {
      // Mock response data
      const mockResults = [
        { id: 'judge1', name: 'Hon. Ellen Johnson', court: 'Northern District of California', position: 'District Judge' },
        { id: 'judge2', name: 'Hon. Michael Rodriguez', court: 'Southern District of New York', position: 'Chief Judge' }
      ];
      
      setSearchResults(mockResults);
      setIsLoading(false);
    }, 1000);
  };
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Judge Search</h2>
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
              Search by name, court, or position
            </label>
            <div className="flex">
              <input
                type="text"
                id="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-grow px-4 py-2 border border-gray-300 rounded-l focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g. John Smith, Southern District of New York"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-r hover:bg-indigo-700 transition"
                disabled={isLoading}
              >
                {isLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>
        </form>
      </section>
      
      {searchResults.length > 0 && (
        <section className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Prediction Results</h3>
          
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-2">Predicted Outcome</h4>
                <div className="flex items-center space-x-3">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white ${
                    prediction.predicted_outcome.includes('plaintiff') 
                      ? 'bg-green-500' 
                      : prediction.predicted_outcome === 'defendant_win'
                        ? 'bg-red-500'
                        : 'bg-yellow-500'
                  }`}>
                    <span className="text-2xl font-bold">
                      {prediction.predicted_outcome.includes('plaintiff') 
                        ? 'P' 
                        : prediction.predicted_outcome === 'defendant_win'
                          ? 'D'
                          : 'O'}
                    </span>
                  </div>
                  <div>
                    <p className="text-xl font-semibold">{formatOutcome(prediction.predicted_outcome)}</p>
                    <p className="text-gray-600">
                      Confidence: <span className="font-medium">{Math.round(prediction.confidence * 100)}%</span>
                    </p>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Outcome Probabilities</h4>
                <div className="space-y-2">
                  {Object.entries(prediction.class_probabilities).map(([outcome, probability]) => (
                    <div key={outcome} className="flex items-center">
                      <div className="w-32 text-sm text-gray-600">{formatOutcome(outcome)}</div>
                      <div className="flex-grow">
                        <div className="h-5 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${
                              outcome.includes('plaintiff') 
                                ? 'bg-green-500' 
                                : outcome === 'defendant_win'
                                  ? 'bg-red-500'
                                  : 'bg-yellow-500'
                            }`}
                            style={{ width: `${Math.round(probability * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-12 text-right text-sm font-medium">
                        {Math.round(probability * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex-1">
              <h4 className="font-medium text-gray-700 mb-2">Factor Impact</h4>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart
                  data={Object.entries(prediction.factor_impact).map(([factor, impact]) => ({
                    factor: factor.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
                    impact: Math.round(impact * 100)
                  }))}
                  layout="vertical"
                  margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="factor" type="category" />
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Bar dataKey="impact" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
              
              <div className="mt-6">
                <h4 className="font-medium text-gray-700 mb-2">Recommendation</h4>
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <p className="text-indigo-800">
                    {prediction.predicted_outcome.includes('plaintiff')
                      ? "This case has a favorable prediction for the plaintiff. Consider highlighting the strongest evidence and precedents during negotiation or trial."
                      : prediction.predicted_outcome === 'defendant_win'
                        ? "This case favors the defendant. If representing the plaintiff, consider settlement options or strengthening your arguments regarding precedent applicability."
                        : "This case has an uncertain outcome. Careful preparation and strong evidence presentation will be critical."
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

// New Simulation Component
const NewSimulation = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    case_type: "lease_dispute",
    case_facts: "",
    jurisdiction: { federal: false, state: "CA" },
    judge_id: ""
  });
  
  const [isLoading, setIsLoading] = useState(false);
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData({
        ...formData,
        [parent]: {
          ...formData[parent],
          [child]: type === 'checkbox' ? checked : value
        }
      });
    } else {
      setFormData({
        ...formData,
        [name]: type === 'checkbox' ? checked : value
      });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Mock API call
    setTimeout(() => {
      // Mock response with simulation ID
      const simulationId = `sim_${Date.now()}`;
      setIsLoading(false);
      navigate(`/simulations/${simulationId}`);
    }, 1500);
  };
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">New Litigation Simulation</h2>
        <p className="text-gray-600 mb-6">
          Create a new simulation session to practice for an upcoming hearing or trial. The system will generate
          realistic judicial questions and opposing counsel arguments based on the provided case information.
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="case_type" className="block text-sm font-medium text-gray-700 mb-1">
              Case Type
            </label>
            <select
              id="case_type"
              name="case_type"
              value={formData.case_type}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="lease_dispute">Lease Dispute</option>
              <option value="foreclosure">Foreclosure</option>
              <option value="zoning">Zoning / Land Use</option>
              <option value="contract_dispute">Contract Dispute</option>
              <option value="financing_dispute">Financing Dispute</option>
              <option value="developer_dispute">Developer Dispute</option>
              <option value="property_tax">Property Tax</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="case_facts" className="block text-sm font-medium text-gray-700 mb-1">
              Case Facts
            </label>
            <textarea
              id="case_facts"
              name="case_facts"
              value={formData.case_facts}
              onChange={handleInputChange}
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Describe the key facts of the case in detail..."
            ></textarea>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jurisdiction
              </label>
              <div className="flex items-center mb-2">
                <input
                  type="checkbox"
                  id="sim_federal"
                  name="jurisdiction.federal"
                  checked={formData.jurisdiction.federal}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="sim_federal" className="ml-2 text-sm text-gray-600">
                  Federal Court
                </label>
              </div>
              <select
                id="sim_state"
                name="jurisdiction.state"
                value={formData.jurisdiction.state}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
                disabled={formData.jurisdiction.federal}
              >
                <option value="CA">California</option>
                <option value="NY">New York</option>
                <option value="TX">Texas</option>
                <option value="FL">Florida</option>
                <option value="IL">Illinois</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="judge_id" className="block text-sm font-medium text-gray-700 mb-1">
                Judge (Optional)
              </label>
              <select
                id="judge_id"
                name="judge_id"
                value={formData.judge_id}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select a judge (or leave blank for random)</option>
                <option value="judge1">Hon. Ellen Johnson</option>
                <option value="judge2">Hon. Michael Rodriguez</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">
                Selecting a specific judge will tailor questions to their known patterns.
              </p>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
              disabled={isLoading || !formData.case_facts}
            >
              {isLoading ? 'Creating Simulation...' : 'Start Simulation'}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
};

// Simulation Session Component
const SimulationSession = () => {
  const { simulationId } = useParams();
  const [simulation, setSimulation] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [userResponse, setUserResponse] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [opposingArgument, setOpposingArgument] = useState(null);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [sessionSummary, setSessionSummary] = useState(null);
  
  useEffect(() => {
    // Mock API call to get simulation data
    setTimeout(() => {
      // Mock simulation data
      const mockSimulation = {
        id: simulationId,
        case_type: "lease_dispute",
        judge: {
          id: "judge1",
          name: "Hon. Ellen Johnson"
        },
        case_facts: "Plaintiff alleges that defendant breached commercial lease agreement by failing to maintain the property as required by Section 8 of the lease. Defendant counterclaims that plaintiff's modifications to the property violated the lease terms.",
        rounds_completed: 0,
        status: "active"
      };
      
      setSimulation(mockSimulation);
      setIsLoading(false);
      
      // Automatically generate first question
      generateQuestion();
    }, 1000);
  }, [simulationId]);
  
  const generateQuestion = () => {
    // Mock API call to generate question
    setIsLoading(true);
    
    setTimeout(() => {
      // Mock question response
      const mockQuestion = {
        id: simulation ? simulation.rounds_completed : 0,
        text: "Given the lease agreement's Section 8, how do you reconcile the plaintiff's claim about maintenance requirements with the defendant's assertion of unauthorized modifications?",
        category: "factual"
      };
      
      setCurrentQuestion(mockQuestion);
      setFeedback(null);
      setOpposingArgument(null);
      setUserResponse("");
      setIsLoading(false);
    }, 1000);
  };
  
  const submitResponse = () => {
    if (!userResponse.trim()) return;
    
    // Mock API call to submit response
    setIsLoading(true);
    
    setTimeout(() => {
      // Mock feedback response
      const mockFeedback = {
        metrics: {
          directness: 0.82,
          persuasiveness: 0.75,
          legal_soundness: 0.68,
          overall_effectiveness: 0.75
        },
        text: "Your response directly addresses the question by focusing on the specific maintenance requirements in Section 8. You effectively point out the defendant's contractual obligations. Consider strengthening your argument with more specific lease terms and addressing the unauthorized modifications claim more explicitly.",
        strengths: [
          "Directly addresses the question",
          "Clear logical structure",
          "Good focus on key lease terms"
        ],
        areas_for_improvement: [
          "Could provide more specific evidence",
          "Address counterarguments more comprehensively",
          "Cite relevant case law for stronger legal foundation"
        ]
      };
      
      setFeedback(mockFeedback);
      setIsLoading(false);
      
      // Update simulation rounds completed
      if (simulation) {
        setSimulation({
          ...simulation,
          rounds_completed: simulation.rounds_completed + 1
        });
      }
      
      // If this is the third round, complete the session
      if (simulation && simulation.rounds_completed >= 2) {
        setSessionComplete(true);
        getSessionSummary();
      }
    }, 1500);
  };
  
  const getOpposingArgument = () => {
    // Mock API call to get opposing argument
    setIsLoading(true);
    
    setTimeout(() => {
      // Mock opposing argument
      const mockArgument = {
        text: "Your Honor, while Section 8 does outline maintenance responsibilities, it must be read in conjunction with Section 12, which explicitly prohibits tenant modifications without written consent. Our client consistently performed required maintenance, but the plaintiff's unauthorized structural changes to the HVAC system voided those obligations under the terms of the agreement. The plaintiff's own actions created the conditions they're now complaining about."
      };
      
      setOpposingArgument(mockArgument);
      setIsLoading(false);
    }, 1000);
  };
  
  const getSessionSummary = () => {
    // Mock API call to get session summary
    setIsLoading(true);
    
    setTimeout(() => {
      // Mock session summary
      const mockSummary = {
        overall_effectiveness: 0.76,
        metrics: {
          directness: 0.81,
          persuasiveness: 0.74,
          legal_soundness: 0.72
        },
        strengths: [
          "Consistently addresses questions directly",
          "Presents persuasive arguments",
          "Good understanding of lease terms"
        ],
        areas_for_improvement: [
          "Could strengthen legal foundation with case citations",
          "More comprehensive handling of counterarguments",
          "More specific evidence references"
        ],
        overall_feedback: "Good performance overall. You effectively addressed most questions with sound legal reasoning. Focus on strengthening your legal foundation with relevant case law and more thoroughly addressing opposing arguments."
      };
      
      setSessionSummary(mockSummary);
      setIsLoading(false);
    }, 1500);
  };
  
  if (isLoading && !simulation) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-700"></div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800">Simulation Session</h2>
            <p className="text-gray-600">
              Case Type: <span className="font-medium">{simulation?.case_type.replace('_', ' ')}</span>
            </p>
            {simulation?.judge && (
              <p className="text-gray-600">
                Judge: <span className="font-medium">{simulation.judge.name}</span>
              </p>
            )}
          </div>
          <div className="bg-indigo-100 px-4 py-2 rounded-lg">
            <p className="text-sm text-indigo-800">Round: {simulation?.rounds_completed || 0}</p>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-700 mb-2">Case Facts:</h3>
          <p className="text-gray-600">{simulation?.case_facts}</p>
        </div>
      </section>
      
      {sessionComplete && sessionSummary ? (
        <section className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Session Summary</h3>
          
          <div className="mb-6">
            <h4 className="font-medium text-gray-700 mb-2">Overall Performance</h4>
            <div className="h-4 bg-gray-200 rounded-full w-full mb-2">
              <div 
                className="h-full bg-indigo-600 rounded-full"
                style={{ width: `${Math.round(sessionSummary.overall_effectiveness * 100)}%` }}
              ></div>
            </div>
            <p className="text-right text-sm text-gray-600">
              Score: <span className="font-medium">{Math.round(sessionSummary.overall_effectiveness * 100)}%</span>
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Performance Metrics</h4>
              <div className="space-y-3">
                {Object.entries(sessionSummary.metrics).map(([metric, value]) => (
                  <div key={metric}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600 capitalize">{metric.replace('_', ' ')}</span>
                      <span className="font-medium">{Math.round(value * 100)}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full w-full">
                      <div 
                        className="h-full bg-indigo-600 rounded-full"
                        style={{ width: `${Math.round(value * 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Strengths</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {sessionSummary.strengths.map((strength, idx) => (
                  <li key={idx}>{strength}</li>
                ))}
              </ul>
              
              <h4 className="font-medium text-gray-700 mt-4 mb-2">Areas for Improvement</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-600">
                {sessionSummary.areas_for_improvement.map((area, idx) => (
                  <li key={idx}>{area}</li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="p-4 bg-indigo-50 rounded-lg">
            <h4 className="font-medium text-indigo-800 mb-2">Overall Feedback:</h4>
            <p className="text-indigo-700">{sessionSummary.overall_feedback}</p>
          </div>
          
          <div className="flex justify-end mt-6">
            <button
              onClick={() => window.location.href = '/simulations/new'}
              className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
            >
              New Simulation
            </button>
          </div>
        </section>
      ) : (
        <>
          {currentQuestion && (
            <section className="p-6 bg-white rounded-lg shadow-md">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-indigo-100 rounded-full text-indigo-700">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div>
                  <p className="text-gray-500 text-sm mb-1">Judge {simulation?.judge?.name || "Question"} ({currentQuestion.category}):</p>
                  <p className="text-gray-800 text-lg">{currentQuestion.text}</p>
                </div>
              </div>
              
              <div className="mt-6">
                <label htmlFor="response" className="block text-sm font-medium text-gray-700 mb-1">
                  Your Response:
                </label>
                <textarea
                  id="response"
                  value={userResponse}
                  onChange={(e) => setUserResponse(e.target.value)}
                  rows={5}
                  className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your response to the judge's question..."
                  disabled={!!feedback}
                ></textarea>
              </div>
              
              {!feedback ? (
                <div className="flex justify-end mt-4">
                  <button
                    onClick={submitResponse}
                    className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
                    disabled={isLoading || !userResponse.trim()}
                  >
                    {isLoading ? 'Submitting...' : 'Submit Response'}
                  </button>
                </div>
              ) : (
                <div className="mt-6 border-t pt-4">
                  <div className="flex items-start space-x-4">
                    <div className="p-2 bg-green-100 rounded-full text-green-700">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Feedback:</h4>
                      <p className="text-gray-600">{feedback.text}</p>
                      
                      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h5 className="text-sm font-medium text-gray-700 mb-1">Strengths:</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                            {feedback.strengths.map((strength, idx) => (
                              <li key={idx}>{strength}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="text-sm font-medium text-gray-700 mb-1">Areas for Improvement:</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                            {feedback.areas_for_improvement.map((area, idx) => (
                              <li key={idx}>{area}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                      
                      <div className="mt-4 space-y-2">
                        <h5 className="text-sm font-medium text-gray-700">Performance Metrics:</h5>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(feedback.metrics).map(([metric, value]) => (
                            <div key={metric}>
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-500 capitalize">{metric.replace('_', ' ')}</span>
                                <span className="font-medium">{Math.round(value * 100)}%</span>
                              </div>
                              <div className="h-1.5 bg-gray-200 rounded-full w-full">
                                <div 
                                  className="h-full bg-indigo-600 rounded-full"
                                  style={{ width: `${Math.round(value * 100)}%` }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {!opposingArgument ? (
                    <div className="flex justify-end mt-4 space-x-3">
                      <button
                        onClick={getOpposingArgument}
                        className="px-4 py-2 border border-indigo-600 text-indigo-600 rounded hover:bg-indigo-50 transition"
                        disabled={isLoading}
                      >
                        Get Opposing Argument
                      </button>
                      <button
                        onClick={generateQuestion}
                        className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
                        disabled={isLoading}
                      >
                        {isLoading ? 'Loading...' : 'Next Question'}
                      </button>
                    </div>
                  ) : (
                    <>
                      <div className="mt-6 border-t pt-4">
                        <div className="flex items-start space-x-4">
                          <div className="p-2 bg-red-100 rounded-full text-red-700">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                            </svg>
                          </div>
                          <div>
                            <p className="text-gray-500 text-sm mb-1">Opposing Counsel:</p>
                            <p className="text-gray-800">{opposingArgument.text}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex justify-end mt-4">
                        <button
                          onClick={generateQuestion}
                          className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
                          disabled={isLoading}
                        >
                          {isLoading ? 'Loading...' : 'Next Question'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
};

// Export the App component
export default App;-4">Search Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {searchResults.map(judge => (
              <div key={judge.id} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                <h4 className="text-lg font-medium text-gray-800">{judge.name}</h4>
                <p className="text-gray-600">{judge.position}, {judge.court}</p>
                <button
                  onClick={() => navigate(`/judges/${judge.id}`)}
                  className="mt-2 text-sm text-indigo-600 hover:text-indigo-800"
                >
                  View Profile
                </button>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

// Judge Profile Component
const JudgeProfile = () => {
  const { judgeId } = useParams();
  const [judge, setJudge] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Mock API call
    setTimeout(() => {
      // Mock judge data
      const mockJudge = {
        id: judgeId,
        name: 'Hon. Ellen Johnson',
        position: 'District Judge',
        court: 'Northern District of California',
        appointed: '2018-06-15',
        stats: {
          case_types: {
            "lease_dispute": 28,
            "foreclosure": 15,
            "zoning": 22,
            "contract_dispute": 35
          },
          outcomes: {
            "plaintiff_full": 30,
            "plaintiff_partial": 25,
            "defendant_win": 35,
            "dismissed": 10
          },
          avg_citation_count: 5.4,
          avg_opinion_length: 3204
        },
        writing_style: {
          cluster: 2,
          common_phrases: ["As the Court has previously noted", "The statute clearly provides"],
          avg_sentence_length: 24.6
        },
        topics: {
          primary_topics: ["Contract interpretation", "Regulatory compliance", "Fiduciary duty"],
          topic_distribution: [
            { name: "Contracts", value: 40 },
            { name: "Regulations", value: 25 },
            { name: "Procedure", value: 20 },
            { name: "Evidence", value: 15 }
          ]
        }
      };
      
      setJudge(mockJudge);
      setIsLoading(false);
    }, 1500);
  }, [judgeId]);
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-700"></div>
      </div>
    );
  }
  
  if (!judge) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-md">
        <p className="text-red-500">Judge not found</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-semibold text-gray-800">{judge.name}</h2>
            <p className="text-gray-600">{judge.position}, {judge.court}</p>
            <p className="text-gray-500 text-sm">Appointed: {new Date(judge.appointed).toLocaleDateString()}</p>
          </div>
          <div className="p-4 bg-indigo-100 rounded-lg text-center">
            <div className="text-3xl font-bold text-indigo-700">{
              Math.round((judge.stats.outcomes.plaintiff_full + judge.stats.outcomes.plaintiff_partial) / 
              Object.values(judge.stats.outcomes).reduce((a, b) => a + b, 0) * 100)
            }%</div>
            <div className="text-xs text-indigo-700">Plaintiff Success Rate</div>
          </div>
        </div>
      </section>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Case Outcomes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={Object.entries(judge.stats.outcomes).map(([key, value]) => ({ name: key, value }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
              >
                {Object.entries(judge.stats.outcomes).map(([key, value], index) => (
                  <Cell key={`cell-${index}`} fill={['#8884d8', '#82ca9d', '#ffc658', '#ff7300'][index % 4]} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, name.replace('_', ' ')]} />
              <Legend formatter={(value) => value.replace('_', ' ')} />
            </PieChart>
          </ResponsiveContainer>
        </section>
        
        <section className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Case Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={Object.entries(judge.stats.case_types).map(([key, value]) => ({ name: key.replace('_', ' '), value }))}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>
      
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Writing Style & Topics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Common Phrases</h4>
            <ul className="list-disc list-inside space-y-1">
              {judge.writing_style.common_phrases.map((phrase, idx) => (
                <li key={idx} className="text-gray-600">"{phrase}"</li>
              ))}
            </ul>
            <div className="mt-4">
              <p className="text-gray-700">Average sentence length: <span className="font-medium">{judge.writing_style.avg_sentence_length} words</span></p>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Primary Topics</h4>
            <div className="space-y-2">
              {judge.topics.primary_topics.map((topic, idx) => (
                <div key={idx} className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full inline-block mr-2">
                  {topic}
                </div>
              ))}
            </div>
            <div className="mt-4">
              <ResponsiveContainer width="100%" height={150}>
                <PieChart>
                  <Pie
                    data={judge.topics.topic_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={30}
                    outerRadius={60}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {judge.topics.topic_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#8884d8', '#82ca9d', '#ffc658', '#ff7300'][index % 4]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

// Case Prediction Component
const CasePrediction = () => {
  const [formData, setFormData] = useState({
    case_type: "lease_dispute",
    case_facts: "",
    jurisdiction: { federal: false, state: "CA" },
    judge_id: "",
    precedent_strength: 0.5
  });
  
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData({
        ...formData,
        [parent]: {
          ...formData[parent],
          [child]: type === 'checkbox' ? checked : value
        }
      });
    } else {
      setFormData({
        ...formData,
        [name]: type === 'checkbox' ? checked : value
      });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Mock API call
    setTimeout(() => {
      // Mock prediction response
      const mockPrediction = {
        predicted_outcome: "plaintiff_partial",
        confidence: 0.78,
        class_probabilities: {
          "plaintiff_full": 0.15,
          "plaintiff_partial": 0.78,
          "defendant_win": 0.05,
          "dismissed": 0.02
        },
        factor_impact: {
          judge_impact: 0.12,
          precedent_impact: 0.24,
          case_facts_impact: 0.64
        }
      };
      
      setPrediction(mockPrediction);
      setIsLoading(false);
    }, 2000);
  };
  
  const formatOutcome = (outcome) => {
    return outcome
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  return (
    <div className="space-y-8">
      <section className="p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">Case Outcome Prediction</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="case_type" className="block text-sm font-medium text-gray-700 mb-1">
              Case Type
            </label>
            <select
              id="case_type"
              name="case_type"
              value={formData.case_type}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="lease_dispute">Lease Dispute</option>
              <option value="foreclosure">Foreclosure</option>
              <option value="zoning">Zoning / Land Use</option>
              <option value="contract_dispute">Contract Dispute</option>
              <option value="financing_dispute">Financing Dispute</option>
              <option value="developer_dispute">Developer Dispute</option>
              <option value="property_tax">Property Tax</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="case_facts" className="block text-sm font-medium text-gray-700 mb-1">
              Case Facts
            </label>
            <textarea
              id="case_facts"
              name="case_facts"
              value={formData.case_facts}
              onChange={handleInputChange}
              rows={5}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Describe the key facts of the case..."
            ></textarea>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jurisdiction
              </label>
              <div className="flex items-center mb-2">
                <input
                  type="checkbox"
                  id="federal"
                  name="jurisdiction.federal"
                  checked={formData.jurisdiction.federal}
                  onChange={handleInputChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="federal" className="ml-2 text-sm text-gray-600">
                  Federal Court
                </label>
              </div>
              <select
                id="state"
                name="jurisdiction.state"
                value={formData.jurisdiction.state}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
                disabled={formData.jurisdiction.federal}
              >
                <option value="CA">California</option>
                <option value="NY">New York</option>
                <option value="TX">Texas</option>
                <option value="FL">Florida</option>
                <option value="IL">Illinois</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="precedent_strength" className="block text-sm font-medium text-gray-700 mb-1">
                Precedent Strength
              </label>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Weak</span>
                <input
                  type="range"
                  id="precedent_strength"
                  name="precedent_strength"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.precedent_strength}
                  onChange={handleInputChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-sm text-gray-500">Strong</span>
              </div>
              <div className="text-center mt-1">
                <span className="text-sm text-gray-600">{Math.round(formData.precedent_strength * 100)}%</span>
              </div>
            </div>
          </div>
          
          <div>
            <label htmlFor="judge_id" className="block text-sm font-medium text-gray-700 mb-1">
              Judge (Optional)
            </label>
            <select
              id="judge_id"
              name="judge_id"
              value={formData.judge_id}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select a judge</option>
              <option value="judge1">Hon. Ellen Johnson</option>
              <option value="judge2">Hon. Michael Rodriguez</option>
            </select>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-6 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
              disabled={isLoading || !formData.case_facts}
            >
              {isLoading ? 'Analyzing...' : 'Predict Outcome'}
            </button>
          </div>
        </form>
      </section>
      
      {prediction && (
        <section className="p-6 bg-white rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-800 mb