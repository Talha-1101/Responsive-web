import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Globe,
  Smartphone,
  Monitor,
  Zap,
  Eye,
  Search,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Layout,
  History
} from 'lucide-react';
import { validateUrl, normalizeUrl, apiClient } from '../services/api';
import { GlassCard } from '../components/ui/GlassCard';

const Landing: React.FC = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validation = validateUrl(url);
    if (!validation.isValid) {
      setError(validation.error || 'Please enter a valid URL');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      const normalizedUrl = normalizeUrl(url);
      const response = await apiClient.startAnalysis({ url: normalizedUrl });
      navigate(`/testing/${response.session_id}`);
    } catch (error: any) {
      setError(error.message || 'Failed to start analysis. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: <Smartphone className="w-6 h-6 text-blue-500" />,
      title: 'Responsive Testing',
      description: 'Test across 7 different viewport sizes from mobile to desktop'
    },
    {
      icon: <Eye className="w-6 h-6 text-purple-500" />,
      title: 'Accessibility Audit',
      description: 'Check for WCAG compliance and accessibility barriers'
    },
    {
      icon: <Search className="w-6 h-6 text-green-500" />,
      title: 'SEO Analysis',
      description: 'Analyze meta tags, headings, and search engine visibility'
    },
    {
      icon: <Zap className="w-6 h-6 text-yellow-500" />,
      title: 'Performance Audit',
      description: 'Lighthouse-powered performance and Core Web Vitals analysis'
    },
    {
      icon: <Layout className="w-6 h-6 text-pink-500" />,
      title: 'Platform Detection',
      description: 'Identify CMS, frameworks, and technology stack'
    },
    {
      icon: <Sparkles className="w-6 h-6 text-amber-500" />,
      title: 'AI-Powered Insights',
      description: 'Get intelligent fix suggestions and recommendations'
    }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Dynamic Background Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-400/20 blur-[100px] animate-blob" />
        <div className="absolute top-[20%] right-[-10%] w-[35%] h-[35%] rounded-full bg-blue-400/20 blur-[100px] animate-blob animation-delay-2000" />
        <div className="absolute bottom-[-10%] left-[20%] w-[35%] h-[35%] rounded-full bg-pink-400/20 blur-[100px] animate-blob animation-delay-4000" />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-4xl mx-auto text-center"
        >
          {/* Hero Section */}
          <div className="mb-16">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-white/30 backdrop-blur-md border border-white/40 text-sm font-medium text-slate-700 dark:text-slate-200 mb-6 shadow-sm"
            >
              <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>Now with AI-Powered Fix Suggestions</span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900 dark:text-white mb-6 leading-tight tracking-tight">
              Test Your Website's{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                Responsiveness
              </span>
            </h1>
            <p className="text-xl text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed">
              Professional-grade analysis of design, accessibility, SEO, and performance.
              Powered by advanced device emulation.
            </p>
          </div>

          {/* URL Input Form */}
          <div className="mb-20">
            <GlassCard className="max-w-2xl mx-auto p-1 text-left shadow-2xl border-white/40 dark:border-white/10">
              <div className="bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl rounded-xl p-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 ml-1">
                      Website URL
                    </label>
                    <div className="relative group">
                      <Globe className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors w-5 h-5" />
                      <input
                        type="url"
                        placeholder="e.g. https://example.com"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="w-full pl-12 pr-4 py-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all shadow-inner"
                      />
                    </div>
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="mt-3 text-sm text-red-500 flex items-center"
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-red-500 mr-2" />
                        {error}
                      </motion.div>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 shadow-lg hover:shadow-blue-500/25 transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Running Analysis...</span>
                      </>
                    ) : (
                      <>
                        <span>Start Free Analysis</span>
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </form>

                {/* Recent / Quick Links */}
                <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    Quick Test
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {['github.com', 'tailwindcss.com', 'apple.com', 'stripe.com'].map((example) => (
                      <button
                        key={example}
                        onClick={() => setUrl(`https://${example}`)}
                        className="px-3 py-1.5 text-sm bg-slate-100 dark:bg-slate-800 hover:bg-blue-50 dark:hover:bg-slate-700 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg text-slate-600 dark:text-slate-400 transition-colors border border-transparent hover:border-blue-200 dark:hover:border-slate-600"
                      >
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Features Grid */}
          <div className="mb-20">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-10">
              Complete Analysis Suite
            </h2>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <GlassCard
                  key={index}
                  hoverEffect={true}
                  className="text-left group"
                >
                  <div className="mb-4 p-3 bg-slate-50 dark:bg-slate-800 rounded-xl w-fit group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                    {feature.description}
                  </p>
                </GlassCard>
              ))}
            </div>
          </div>

          {/* Feature Highlight */}
          <GlassCard className="p-10 text-left relative overflow-hidden">
            <div className="absolute top-0 right-0 p-10 opacity-10">
              <History className="w-64 h-64 text-slate-900 dark:text-white" />
            </div>
            <div className="relative z-10 max-w-2xl">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                Professional Reports & Historical Data
              </h2>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  'Export to PDF (Coming Soon)',
                  'Historical Trend Analysis',
                  'Competitor Benchmarking',
                  'Network Condition Simulation'
                ].map((item, i) => (
                  <div key={i} className="flex items-center text-slate-700 dark:text-slate-300">
                    <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>

        </motion.div>
      </div>
    </div>
  );
};

export default Landing;