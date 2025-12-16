import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Monitor,
  Smartphone,
  Globe,
  Search,
  Zap,
  Sparkles,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowLeft,
  Loader2
} from 'lucide-react';
import { apiClient } from '../services/api';
import { SessionStatus } from '../types/api';
import { GlassCard } from '../components/ui/GlassCard';

const Testing: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [status, setStatus] = useState<SessionStatus>({
    session_id: sessionId || '',
    status: 'started',
    progress: 0,
    message: 'Initializing...'
  });

  const [startTime] = useState<Date>(new Date());
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime.getTime()) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  // Polling for status updates
  useEffect(() => {
    if (!sessionId) return;

    const pollStatus = async () => {
      try {
        const newStatus = await apiClient.getAnalysisStatus(sessionId);
        setStatus(newStatus);
        setError(null); // Clear any previous errors

        if (newStatus.status === 'completed') {
          setTimeout(() => {
            navigate(`/results/${sessionId}`);
          }, 1500);
        } else if (newStatus.status === 'failed') {
          setError('Analysis failed. Please try again.');
        }
      } catch (error: any) {
        console.error('Failed to get status:', error);
        setError(`Connection error: ${error.message}`);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);
    pollStatus(); // Initial call

    return () => clearInterval(interval);
  }, [sessionId, navigate]);

  const analysisSteps = [
    {
      key: 'initialization',
      icon: <Globe className="w-5 h-5" />,
      title: 'Initializing',
      description: 'Setting up browser and loading website'
    },
    {
      key: 'loading',
      icon: <Clock className="w-5 h-5" />,
      title: 'Loading Website',
      description: 'Accessing and parsing website content'
    },
    {
      key: 'screenshots',
      icon: <Monitor className="w-5 h-5" />,
      title: 'Responsive Testing',
      description: 'Capturing screenshots across different viewports'
    },
    {
      key: 'seo',
      icon: <Search className="w-5 h-5" />,
      title: 'SEO Analysis',
      description: 'Analyzing meta tags, headings, and structure'
    },
    {
      key: 'forms',
      icon: <Globe className="w-5 h-5" />,
      title: 'Form Testing',
      description: 'Testing forms and interactive elements'
    },
    {
      key: 'platform',
      icon: <Globe className="w-5 h-5" />,
      title: 'Platform Detection',
      description: 'Identifying CMS and technology stack'
    },
    {
      key: 'performance',
      icon: <Zap className="w-5 h-5" />,
      title: 'Performance Audit',
      description: 'Running Lighthouse performance analysis'
    },
    {
      key: 'ai_analysis',
      icon: <Sparkles className="w-5 h-5" />,
      title: 'AI Analysis',
      description: 'Generating intelligent insights and recommendations'
    }
  ];

  const getStepStatus = (stepKey: string) => {
    if (status.current_step === stepKey) return 'active';
    // Simple logic: mark previous steps as completed
    const currentIndex = analysisSteps.findIndex(s => s.key === status.current_step);
    const stepIndex = analysisSteps.findIndex(s => s.key === stepKey);
    if (currentIndex > stepIndex) return 'completed';
    return 'pending';
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-transparent">
        <GlassCard className="p-8 text-center border-red-200 bg-red-50/10">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2 text-slate-900 dark:text-white">Invalid Session</h2>
          <p className="text-slate-600 dark:text-slate-300 mb-4">No valid session ID provided.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            Return Home
          </button>
        </GlassCard>
      </div>
    );
  }

  // Show error if there's a connection problem, but don't block the UI completely
  const showError = error && status.progress === 0;

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background matching Landing */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-400/20 blur-[100px] animate-blob" />
        <div className="absolute top-[20%] right-[-10%] w-[35%] h-[35%] rounded-full bg-blue-400/20 blur-[100px] animate-blob animation-delay-2000" />
      </div>

      <div className="container mx-auto px-4 py-12 relative z-10">
        <div className="max-w-5xl mx-auto">

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={() => navigate('/')}
                className="flex items-center px-4 py-2 rounded-full bg-white/30 backdrop-blur-md border border-white/40 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-white/40 transition-all"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </button>
              <div className="px-4 py-2 rounded-full bg-white/30 backdrop-blur-md border border-white/40 text-sm font-medium text-slate-700 dark:text-slate-200 font-mono">
                {formatTime(elapsedTime)}
              </div>
            </div>

            <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 dark:text-white mb-4 tracking-tight">
              Analyzing Website
            </h1>
            <p className="text-slate-600 dark:text-slate-400 font-mono text-sm opacity-80">
              Session ID: {sessionId}
            </p>

            {/* Show connection error if present */}
            {showError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-6 p-4 max-w-md mx-auto bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-md"
              >
                <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
                <p className="text-red-500/80 text-xs mt-1">
                  Ensure backend server is running on port 8000
                </p>
              </motion.div>
            )}
          </motion.div>

          {/* Main Progress Section */}
          <div className="grid lg:grid-cols-12 gap-8">

            {/* Left Column: Progress & Steps */}
            <div className="lg:col-span-8 space-y-6">

              {/* Overall Progress Card */}
              <GlassCard className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Analysis Progress</h2>
                    <p className="text-slate-500 dark:text-slate-400 mt-1">
                      {status.message}
                    </p>
                  </div>
                  <div className="text-3xl font-bold text-slate-900 dark:text-white font-mono">
                    {Math.round(status.progress)}%
                  </div>
                </div>

                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-4 mb-2 overflow-hidden">
                  <motion.div
                    className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-full relative"
                    initial={{ width: 0 }}
                    animate={{ width: `${status.progress}%` }}
                  >
                    <div className="absolute inset-0 bg-white/20 animate-pulse" />
                  </motion.div>
                </div>

                {status.current_viewport && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-end"
                  >
                    <span className="text-xs font-medium px-2 py-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                      Viewport: {status.current_viewport}
                    </span>
                  </motion.div>
                )}
              </GlassCard>

              {/* Steps List */}
              <GlassCard className="p-0 overflow-hidden">
                <div className="p-6 border-b border-slate-200/50 dark:border-slate-700/50 bg-white/40 dark:bg-slate-900/40 backdrop-blur-sm">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">Detailed Steps</h3>
                </div>

                <div className="p-6 space-y-4">
                  {analysisSteps.map((step, index) => {
                    const stepStatus = getStepStatus(step.key);

                    return (
                      <motion.div
                        key={step.key}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`flex items-center p-4 rounded-xl transition-all duration-300 ${stepStatus === 'completed'
                            ? 'bg-green-500/5 border border-green-500/20'
                            : stepStatus === 'active'
                              ? 'bg-blue-500/10 border border-blue-500/30 shadow-lg shadow-blue-500/5 scale-[1.02]'
                              : 'bg-slate-100/50 dark:bg-slate-800/30 border border-transparent'
                          }`}
                      >
                        <div className={`flex-shrink-0 p-3 rounded-full mr-4 transition-colors ${stepStatus === 'completed'
                            ? 'bg-green-500 text-white shadow-green-500/30 shadow-md'
                            : stepStatus === 'active'
                              ? 'bg-blue-600 text-white shadow-blue-500/30 shadow-md'
                              : 'bg-slate-200 dark:bg-slate-700 text-slate-400'
                          }`}>
                          {stepStatus === 'completed' ? (
                            <CheckCircle2 className="w-5 h-5" />
                          ) : stepStatus === 'active' ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                          ) : (
                            step.icon
                          )}
                        </div>

                        <div className="flex-1">
                          <h4 className={`font-semibold text-base ${stepStatus === 'active' ? 'text-blue-700 dark:text-blue-300' :
                              stepStatus === 'completed' ? 'text-slate-900 dark:text-white' :
                                'text-slate-500 dark:text-slate-500'
                            }`}>
                            {step.title}
                          </h4>
                          <p className={`text-sm ${stepStatus === 'active' ? 'text-blue-600/80 dark:text-blue-300/80' : 'text-slate-500 dark:text-slate-500'
                            }`}>
                            {step.description}
                          </p>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </GlassCard>
            </div>

            {/* Right Column: Sidebar Stats */}
            <div className="lg:col-span-4 space-y-6">

              {/* Radial Progress */}
              <GlassCard className="p-8 text-center flex flex-col items-center justify-center min-h-[300px]">
                <div className="relative inline-flex items-center justify-center mb-6">
                  <div className="absolute inset-0 bg-blue-500/20 blur-3xl rounded-full" />
                  <svg className="w-40 h-40 transform -rotate-90 relative z-10">
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="transparent"
                      className="text-slate-200 dark:text-slate-700"
                    />
                    <motion.circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="currentColor"
                      strokeWidth="12"
                      fill="transparent"
                      strokeLinecap="round"
                      className="text-blue-600 dark:text-blue-500"
                      strokeDasharray={`${2 * Math.PI * 70}`}
                      initial={{ strokeDashoffset: 2 * Math.PI * 70 }}
                      animate={{
                        strokeDashoffset: 2 * Math.PI * 70 * (1 - status.progress / 100)
                      }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <span className="text-4xl font-extrabold text-slate-900 dark:text-white tracking-tighter">
                      {Math.round(status.progress)}%
                    </span>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Complete</span>
                  </div>
                </div>

                <h3 className="text-xl font-bold text-slate-800 dark:text-slate-200 mb-2">
                  {status.status === 'completed' ? 'Analysis Complete' : 'Analyzing via Playwright'}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Using real browser emulation for accurate results.
                </p>
              </GlassCard>

              {/* Current Action / Cancel */}
              <GlassCard className="p-6">
                {status.status !== 'completed' && (
                  <div className="mb-6">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="relative">
                        <span className="absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75 animate-ping"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                      </div>
                      <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
                        Live status
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                      {status.message}
                    </p>
                  </div>
                )}

                <button
                  onClick={() => navigate('/')}
                  className="w-full py-3 px-4 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400 transition-all font-medium text-sm"
                  disabled={status.status === 'completed'}
                >
                  Cancel Analysis
                </button>
              </GlassCard>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Testing;