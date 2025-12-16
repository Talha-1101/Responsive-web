import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download,
  ArrowLeft,
  Globe,
  Calendar,
  ExternalLink,
  Share2,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Info,
  Smartphone,
  Zap,
  Layout,
  Search,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Code2
} from 'lucide-react';
import { apiClient, formatUrl } from '../services/api';
import { CompleteAnalysisResults, DetectedIssue } from '../types/api';
import { GlassCard } from '../components/ui/GlassCard';

const Results: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [results, setResults] = useState<CompleteAnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [expandedIssue, setExpandedIssue] = useState<string | null>(null);
  const [guideModal, setGuideModal] = useState<{
    isOpen: boolean;
    category: string;
    content: string;
    loading: boolean;
  }>({
    isOpen: false,
    category: '',
    content: '',
    loading: false
  });

  const handleGetGuide = async (category: string) => {
    if (!results) return;

    setGuideModal({ isOpen: true, category, content: '', loading: true });

    try {
      const context = {
        url: results.url,
        scores: results.scores,
        issues: results.issues.filter(i => i.category === category.toLowerCase()),
        seo: results.seo
      };

      const guide = await apiClient.getImprovementGuide(category, context);
      setGuideModal(prev => ({ ...prev, loading: false, content: guide }));
    } catch (e) {
      console.error(e);
      setGuideModal(prev => ({ ...prev, loading: false, content: "Failed to generate guide. Please try again." }));
    }
  };

  useEffect(() => {
    const loadResults = async () => {
      if (!sessionId) {
        setError('No session ID provided');
        setLoading(false);
        return;
      }

      try {
        const data = await apiClient.getAnalysisResults(sessionId);
        setResults(data);
      } catch (error: any) {
        console.error('Failed to load results:', error);
        setError(error.message || 'Failed to load analysis results');
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, [sessionId]);

  const handleDownloadReport = async () => {
    if (!sessionId) return;

    setDownloadingReport(true);
    try {
      await apiClient.downloadReport(sessionId);
    } catch (error: any) {
      console.error('Failed to download report:', error);
    } finally {
      setDownloadingReport(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share && results) {
      try {
        await navigator.share({
          title: `Website Analysis Results - ${formatUrl(results.url)}`,
          text: `Analysis results showing ${Math.round(results.scores.overall)}/100 overall score`,
          url: window.location.href
        });
      } catch (error) {
        navigator.clipboard.writeText(window.location.href);
      }
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
  };

  // Group issues by category
  const groupedIssues = results?.issues.reduce((acc, issue) => {
    const category = issue.category;
    if (!acc[category]) acc[category] = [];
    acc[category].push(issue);
    return acc;
  }, {} as Record<string, DetectedIssue[]>) || {};

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Layout className="w-4 h-4" />, count: null },
    { id: 'issues', label: 'Issues & Fixes', icon: <AlertTriangle className="w-4 h-4" />, count: results?.issues.length || 0 },
    { id: 'screenshots', label: 'Screenshots', icon: <Smartphone className="w-4 h-4" />, count: results?.viewports.length || 0 },
    { id: 'scores', label: 'Details', icon: <Zap className="w-4 h-4" />, count: null },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-center">
          <div className="relative">
            <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-blue-400 animate-pulse" />
            </div>
          </div>
          <p className="text-slate-400 font-medium">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <GlassCard className="p-8 text-center max-w-md border-red-500/30 bg-red-500/5">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Analysis Not Found</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            {error || 'The analysis results could not be loaded.'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Return Home
          </button>
        </GlassCard>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500';
    if (score >= 80) return 'text-emerald-500';
    if (score >= 70) return 'text-yellow-500';
    if (score >= 60) return 'text-orange-500';
    return 'text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreGrade = (score: number) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  return (
    <div className="min-h-screen relative overflow-hidden text-slate-900 dark:text-slate-100 font-sans">
      {/* Global Animated Background */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none bg-slate-50 dark:bg-slate-950 transition-colors duration-500">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-500/10 blur-[120px] animate-blob" />
        <div className="absolute top-[20%] right-[-10%] w-[35%] h-[35%] rounded-full bg-blue-500/10 blur-[120px] animate-blob animation-delay-2000" />
        <div className="absolute bottom-[-10%] left-[20%] w-[45%] h-[45%] rounded-full bg-emerald-500/10 blur-[120px] animate-blob animation-delay-4000" />
      </div>

      <div className="container mx-auto px-4 py-8 relative z-10">

        {/* Top Navigation Bar */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row items-center justify-between mb-8 gap-4"
        >
          <div className="flex items-center gap-4 w-full md:w-auto">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                Results
                <span className="text-sm font-normal px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                  {sessionId?.substring(0, 8)}
                </span>
              </h1>
              <a href={results.url} target="_blank" rel="noreferrer" className="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1 hover:text-blue-500 transition-colors">
                <Globe className="w-3 h-3" />
                {formatUrl(results.url)}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <button onClick={handleShare} className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-white/40 dark:bg-slate-800/40 backdrop-blur-sm border border-white/20 dark:border-slate-700/50 hover:bg-white/60 dark:hover:bg-slate-800/60 transition-all font-medium text-sm">
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button onClick={handleDownloadReport} disabled={downloadingReport} className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-white/40 dark:bg-slate-800/40 backdrop-blur-sm border border-white/20 dark:border-slate-700/50 hover:bg-white/60 dark:hover:bg-slate-800/60 transition-all font-medium text-sm">
              <Download className="w-4 h-4" /> {downloadingReport ? '...' : 'PDF'}
            </button>
            <button onClick={() => navigate('/')} className="flex-1 md:flex-none flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-500/20 transition-all font-medium text-sm">
              <RefreshCw className="w-4 h-4" /> New Test
            </button>
          </div>
        </motion.div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-4 md:pb-0 mb-8 no-scrollbar">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold transition-all whitespace-nowrap ${activeTab === tab.id
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-lg'
                : 'bg-white/30 dark:bg-slate-800/30 text-slate-600 dark:text-slate-400 hover:bg-white/50 dark:hover:bg-slate-800/50'
                }`}
            >
              {tab.icon}
              {tab.label}
              {tab.count !== null && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${activeTab === tab.id
                  ? 'bg-white/20 text-white dark:bg-slate-900/10 dark:text-slate-900'
                  : 'bg-black/5 dark:bg-white/10'
                  }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {/* === OVERVIEW TAB === */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                {/* Overall Score Card */}
                <div className="md:col-span-4">
                  <GlassCard className="h-full flex flex-col items-center justify-center py-10">
                    <div className="flex flex-col items-center">
                      <div className="relative mb-2">
                        <svg className="w-48 h-48 transform -rotate-90">
                          <circle
                            cx="96" cy="96" r="80"
                            stroke="currentColor" strokeWidth="12" fill="transparent"
                            className="text-slate-200 dark:text-slate-800"
                          />
                          <motion.circle
                            cx="96" cy="96" r="80"
                            stroke="currentColor" strokeWidth="12" fill="transparent" strokeLinecap="round"
                            className={getScoreColor(results.scores.overall)}
                            strokeDasharray={`${2 * Math.PI * 80}`}
                            initial={{ strokeDashoffset: 2 * Math.PI * 80 }}
                            animate={{ strokeDashoffset: 2 * Math.PI * 80 * (1 - results.scores.overall / 100) }}
                            transition={{ duration: 1.5, ease: "easeOut" }}
                          />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className={`text-6xl font-black ${getScoreColor(results.scores.overall)}`}>
                            {Math.round(results.scores.overall)}
                          </span>
                        </div>
                      </div>

                      <div className="text-center mb-4">
                        <span className="text-sm font-medium bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent block mb-1">
                          Agentic AI Analysis
                        </span>
                        <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-200">
                          {getScoreGrade(results.scores.overall)} Grade
                        </h3>
                      </div>

                      <p className="text-slate-500 text-sm max-w-[200px] text-center">
                        Based on performance, SEO, accessibility, and best practices.
                      </p>
                    </div>
                  </GlassCard>
                </div>

                {/* Analysis & Quick Stats */}
                <div className="md:col-span-8 space-y-6">
                  {/* AI Insights Card */}
                  {results.ai_analysis && !results.ai_analysis.error && (
                    <GlassCard className="border-l-4 border-l-purple-500 bg-purple-50/40 dark:bg-purple-900/10">
                      <div className="flex items-start gap-4">
                        <div className="p-3 bg-white/50 dark:bg-slate-800/50 rounded-xl">
                          <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            AI Analysis
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-300 uppercase tracking-wide">Beta</span>
                          </h3>
                          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-sm mb-4">
                            {results.ai_analysis.overall_assessment}
                          </p>
                          {results.ai_analysis.key_insights && (
                            <div className="grid sm:grid-cols-2 gap-3">
                              {results.ai_analysis.key_insights.slice(0, 4).map((insight: string, i: number) => (
                                <div key={i} className="flex items-start gap-2 text-xs font-medium text-slate-600 dark:text-slate-400 bg-white/40 dark:bg-black/20 p-2 rounded-lg">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-purple-500 mt-0.5 shrink-0" />
                                  {insight}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </GlassCard>
                  )}

                  {/* Sub-Scores Grid */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      { label: 'Responsiveness', score: results.scores.responsiveness, icon: Smartphone },
                      { label: 'Accessibility', score: results.scores.accessibility, icon: Globe },
                      { label: 'SEO', score: results.scores.seo, icon: Search },
                      { label: 'Performance', score: results.scores.performance, icon: Zap },
                    ].map((item) => (
                      <GlassCard key={item.label} className="p-4 flex flex-col items-center justify-center text-center hover:scale-[1.02] transition-transform">
                        <item.icon className="w-6 h-6 text-slate-400 mb-2" />
                        <span className={`text-2xl font-bold mb-1 ${getScoreColor(item.score)}`}>
                          {Math.round(item.score)}
                        </span>
                        <span className="text-xs font-semibold text-slate-500 uppercase">{item.label}</span>
                        <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded-full mt-3 overflow-hidden">
                          <div className={`h-full ${getScoreBg(item.score)}`} style={{ width: `${item.score}%` }} />
                        </div>
                        {item.score < 90 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleGetGuide(item.label);
                            }}
                            className="mt-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-semibold hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors"
                          >
                            <Sparkles className="w-3 h-3" />
                            Improve with AI
                          </button>
                        )}
                      </GlassCard>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* === ISSUES TAB (Enhanced with AI Fixes) === */}
            {activeTab === 'issues' && (
              <div className="max-w-4xl mx-auto space-y-6">
                {results.issues.length === 0 ? (
                  <GlassCard className="text-center py-16">
                    <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                      <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">No Issues Found!</h3>
                    <p className="text-slate-500">Your website passed all our checks with flying colors.</p>
                  </GlassCard>
                ) : (
                  Object.entries(groupedIssues).map(([category, issues]) => (
                    <div key={category} className="space-y-4">
                      <h3 className="text-lg font-bold capitalize flex items-center gap-2 text-slate-800 dark:text-slate-200 ml-1">
                        {category === 'seo' ? <Search className="w-5 h-5" /> :
                          category === 'accessibility' ? <Globe className="w-5 h-5" /> :
                            <AlertTriangle className="w-5 h-5" />}
                        {category}
                        <span className="text-sm font-normal text-slate-500">({issues.length} issues)</span>
                      </h3>

                      {issues.map((issue, idx) => (
                        <GlassCard key={idx} className="p-0 overflow-hidden hover:shadow-lg transition-shadow">
                          {/* Issue Header */}
                          <div
                            className="p-5 flex flex-col sm:flex-row items-start gap-4 cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors"
                            onClick={() => setExpandedIssue(expandedIssue === `${category}-${idx}` ? null : `${category}-${idx}`)}
                          >
                            <div className={`mt-1 p-2 rounded-lg shrink-0 ${issue.severity === 'high' ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' :
                              issue.severity === 'medium' ? 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' :
                                'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                              }`}>
                              <AlertTriangle className="w-5 h-5" />
                            </div>
                            <div className="flex-1 w-full">
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="font-bold text-base text-slate-900 dark:text-white">
                                  {issue.issue_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </h4>
                                {expandedIssue === `${category}-${idx}` ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                              </div>
                              <p className="text-slate-600 dark:text-slate-400 text-sm mb-2">{issue.description}</p>
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${issue.severity === 'high' ? 'bg-red-100 text-red-700' :
                                  issue.severity === 'medium' ? 'bg-orange-100 text-orange-700' :
                                    'bg-blue-100 text-blue-700'
                                  }`}>
                                  {issue.severity} Priority
                                </span>
                                {issue.viewport && (
                                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">
                                    {issue.viewport}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* AI Fix Guide (Expanded) */}
                          <AnimatePresence>
                            {expandedIssue === `${category}-${idx}` && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="border-t border-slate-200/50 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-900/30"
                              >
                                <div className="p-5">
                                  <div className="flex items-center gap-2 mb-3 text-blue-600 dark:text-blue-400 font-semibold text-sm">
                                    <Sparkles className="w-4 h-4" />
                                    AI Fix Solution
                                  </div>
                                  <div className="prose prose-sm dark:prose-invert max-w-none">
                                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                                      <p className="font-medium text-slate-800 dark:text-slate-200 mb-2">Recommendation:</p>

                                      {/* Custom Markdown Renderer */}
                                      <div className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed space-y-2">
                                        {(issue.ai_suggestion || issue.suggestion || "No specific fix suggestion available.").split('\n').map((line, i) => {
                                          // Check for code blocks (simple detection)
                                          if (line.trim().startsWith('```')) return null; // Skip code fence markers for now, simpler handling below

                                          // Simple Bold parsing
                                          const parts = line.split(/(\*\*.*?\*\*)/g);
                                          return (
                                            <p key={i}>
                                              {parts.map((part, j) => {
                                                if (part.startsWith('**') && part.endsWith('**')) {
                                                  return <strong key={j} className="text-slate-900 dark:text-slate-100">{part.slice(2, -2)}</strong>;
                                                }
                                                return part;
                                              })}
                                            </p>
                                          );
                                        })}

                                        {/* Extract and render code blocks if present */}
                                        {(issue.ai_suggestion || "").match(/```([\s\S]*?)```/g)?.map((block, i) => (
                                          <div key={i} className="mt-4">
                                            <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                                              <span className="flex items-center gap-1"><Code2 className="w-3 h-3" /> Code Snippet</span>
                                            </div>
                                            <pre className="bg-slate-900 text-slate-50 p-3 rounded-lg overflow-x-auto text-xs font-mono">
                                              {block.replace(/```\w*\n?|```/g, '').trim()}
                                            </pre>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </GlassCard>
                      ))}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* === SCREENSHOTS TAB === */}
            {activeTab === 'screenshots' && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.viewports.map((viewport, index) => (
                  <GlassCard key={index} className="p-0 overflow-hidden group">
                    <div className="p-4 border-b border-slate-100 dark:border-slate-700/50 flex justify-between items-center bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm">
                      <h3 className="font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                        {viewport.name === 'Mobile' ? <Smartphone className="w-4 h-4" /> : <Layout className="w-4 h-4" />}
                        {viewport.name}
                      </h3>
                      <span className="text-xs font-mono text-slate-500 bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded">
                        {viewport.width} × {viewport.height}
                      </span>
                    </div>
                    <div
                      className="relative bg-slate-100 dark:bg-slate-900 overflow-hidden"
                      style={{ aspectRatio: `${viewport.width} / ${viewport.height}` }}
                    >
                      {viewport.screenshot_path ? (
                        <img
                          src={apiClient.getScreenshotUrl(viewport.screenshot_path)}
                          alt={`${viewport.name} screenshot`}
                          className="w-full h-full object-contain object-top transition-transform duration-700 group-hover:scale-105"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.onerror = null; // Prevent loop
                            target.src = 'https://placehold.co/600x400?text=Screenshot+Unavailable';
                            target.parentElement?.classList.add('opacity-50');
                          }}
                        />
                      ) : (<div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 p-4 text-center">
                        <AlertTriangle className="w-10 h-10 mb-2 opacity-50" />
                        <p className="text-sm">Screenshot unavailable</p>
                      </div>
                      )}

                      {/* Overlay Info */}
                      <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                        <p className="text-white text-xs font-medium">
                          {viewport.issues?.length || 0} issues detected
                        </p>
                      </div>
                    </div>
                  </GlassCard>
                ))}
              </div>
            )}

            {/* === DETAILS TAB === */}
            {activeTab === 'scores' && (
              <div className="grid lg:grid-cols-2 gap-6">
                {[
                  { label: 'Responsiveness', score: results.scores.responsiveness, desc: 'How well your site adapts to different screen sizes', bg: 'bg-blue-500' },
                  { label: 'Accessibility', score: results.scores.accessibility, desc: 'Compliance with accessibility standards and guidelines', bg: 'bg-purple-500' },
                  { label: 'SEO', score: results.scores.seo, desc: 'Search engine optimization and discoverability', bg: 'bg-green-500' },
                  { label: 'Performance', score: results.scores.performance, desc: 'Page loading speed and Core Web Vitals', bg: 'bg-orange-500' }
                ].map((item) => (
                  <GlassCard key={item.label} className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white">{item.label}</h3>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{item.desc}</p>
                      </div>
                      <div className={`text-2xl font-bold ${getScoreColor(item.score)}`}>
                        {Math.round(item.score)}
                      </div>
                    </div>
                    <div className="w-full h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full ${item.bg}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${item.score}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                      />
                    </div>
                    {item.score < 90 && (
                      <button
                        onClick={() => handleGetGuide(item.label)}
                        className="mt-4 flex items-center justify-center w-full gap-2 px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-sm transition-colors"
                      >
                        <Sparkles className="w-4 h-4 text-purple-500" />
                        Ask AI how to improve {item.label}
                      </button>
                    )}
                  </GlassCard>
                ))}
              </div>
            )}

          </motion.div>
        </AnimatePresence >

      </div >

      {/* Guide Modal */}
      <AnimatePresence>
        {guideModal.isOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setGuideModal(prev => ({ ...prev, isOpen: false }))}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-white dark:bg-slate-900 rounded-2xl shadow-2xl"
            >
              <div className="sticky top-0 z-10 flex items-center justify-between p-6 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
                <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  Improving your {guideModal.category} Score
                </h3>
                <button
                  onClick={() => setGuideModal(prev => ({ ...prev, isOpen: false }))}
                  className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-500"
                >
                  ✕
                </button>
              </div>

              <div className="p-6">
                {guideModal.loading ? (
                  <div className="flex flex-col items-center justify-center py-12 space-y-4">
                    <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                    <p className="text-slate-500">Consulting Agentic AI...</p>
                  </div>
                ) : (
                  <div className="prose prose-slate dark:prose-invert max-w-none">
                    <div className="whitespace-pre-wrap">{guideModal.content}</div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div >
  );
};

export default Results;