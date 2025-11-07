import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

// 🟢 Default trend data (visible before fetching)
const DEFAULT_TREND_SUMMARY = {
  totalPosts: 10,
  avgRelevance: 0.87,
  trend: "INCREASING",
  highPriority: 0,
  weeklyBreakdown: [{ week: "2025-11-03/2025-11-09", posts: 10 }],
  byIntent: [
    { name: "advice_seeking", count: 4 },
    { name: "case_study", count: 2 },
    { name: "general_chatter", count: 1 },
    { name: "question", count: 1 },
    { name: "complaint", count: 1 },
    { name: "vendor_search", count: 1 },
  ],
  bySubreddit: [
    { name: "r/marketing", count: 5 },
    { name: "r/smallbusiness", count: 3 },
    { name: "r/Entrepreneur", count: 1 },
    { name: "r/shopify", count: 1 },
  ],
};

// 🟢 Default posts if backend fails
const FALLBACK_POSTS = [
  {
    _key: "1oo73f1",
    post_id: "1oo73f1",
    post_link:
      "https://www.reddit.com/r/marketing/comments/1oo73f1/i_think_its_a_fact_ai_will_replace_traffickers_at/",
    post_title:
      "I think it's a fact, AI will replace traffickers, at least when it comes to creating campaigns. How should traffickers evolve?",
    post_summary:
      "AI will soon automate ad campaign creation. How should 'traffickers' evolve to stay relevant?",
    author: "Miyamoto_Musashi_x",
    subreddit: "marketing",
    timestamp: "2025-11-04T18:58:03",
    relevance_score: 0.9,
    intent: "advice_seeking",
    sentiment: "Negative",
  },
  {
    _key: "1ooanzd",
    post_id: "1ooanzd",
    post_title: "Generated 206 Crypto Leads in France with $18 CPL – Full 1-Week Breakdown",
    post_summary:
      "Breakdown of a 1-week crypto lead gen test in France: 206 leads at $18 CPL via Meta ads. Success hinged on extreme localization and tailored creatives.",
    author: "clo-king",
    subreddit: "marketing",
    timestamp: "2025-11-04T21:18:29",
    relevance_score: 0.98,
    intent: "case_study",
    sentiment: "Positive",
  },
];

export default function AIDashboard() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [popupMessage, setPopupMessage] = useState("");
  const [error, setError] = useState(null);
  const [trendSummary, setTrendSummary] = useState(DEFAULT_TREND_SUMMARY);

  // 🎯 Fetch weekly report
  async function fetchWeeklyReport() {
    try {
      const res = await fetch("http://127.0.0.1:8000/gtm_week",{ method: "POST" });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      if (!data) throw new Error("Empty data from server");

      setTrendSummary({
        totalPosts: data.total_posts,
        avgRelevance: data.average_relevance,
        trend: data.trend.toUpperCase(),
        highPriority: data.high_priority_count,
        weeklyBreakdown: Object.entries(data.weekly_counts).map(([week, posts]) => ({
          week,
          posts,
        })),
        byIntent: Object.entries(data.by_intent).map(([name, count]) => ({
          name,
          count,
        })),
        bySubreddit: Object.entries(data.by_subreddit).map(([name, count]) => ({
          name: `r/${name}`,
          count,
        })),
      });
    } catch (err) {
      console.error("Error fetching trend data:", err);
      // 🟡 Fallback if fetch fails
      setTrendSummary(DEFAULT_TREND_SUMMARY);
    }
  }

  // 🟣 Handle week start workflow
  async function handleWeekStart() {
    try {
      setPopupMessage("Starting weekly workflow...");
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/gtm_week", { method: "POST" });
      if (!res.ok) throw new Error("Failed to start weekly workflow");

      setPopupMessage("Loading weekly data...");
      await fetchWeeklyReport();
      setPopupMessage("Weekly report loaded ✅");
    } catch (err) {
      console.error(err);
      setPopupMessage("Failed ❌");
    } finally {
      setTimeout(() => setPopupMessage(""), 2000);
      setLoading(false);
    }
  }

  // 🟠 Fetch posts
  async function fetchPosts() {
    try {
      const res = await fetch("http://localhost:4000/api/posts");
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const data = await res.json();
      const docs = Array.isArray(data) ? data : data.result || data.documents || [];
      setPosts(docs);
    } catch (err) {
      console.error("Error fetching posts:", err);
      setError(err.message);
      setPosts(FALLBACK_POSTS);
    }
  }

  // 🔵 Handle main start (runs everything)
  async function handleStart() {
    try {
      setPopupMessage("Starting...");
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/gtm", { method: "POST" });
      if (!res.ok) throw new Error("Failed to start workflow");

      setPopupMessage("Loading posts...");
      await fetchPosts();

      setPopupMessage("Updating weekly report...");
      await handleWeekStart();

      setPopupMessage("Loaded successfully ✅");
    } catch (err) {
      console.error(err);
      setPopupMessage("Failed ❌");
    } finally {
      setTimeout(() => setPopupMessage(""), 2000);
      setLoading(false);
    }
  }

  const COLORS = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

  return (
    <div className="relative min-h-screen bg-gray-100 w-screen p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl text-black font-bold">AI Marketing Dashboard</h1>
        <button
          onClick={handleStart}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-all"
          disabled={loading}
        >
          {loading ? "Starting..." : "Start"}
        </button>
      </div>

      {/* Popup */}
      {popupMessage && (
        <div className="fixed top-4 right-4 bg-black text-white px-4 py-1 rounded-md text-sm shadow-md z-50 h-8 flex items-center">
          {popupMessage}
        </div>
      )}

      {/* Chart Section */}
      <Card className="mb-8 shadow-md">
        <CardContent className="p-6">
          <h2 className="text-2xl text-black font-bold mb-4">📊 Trends Analysis</h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="p-4 bg-blue-100 rounded-lg text-center">
              <h3 className="text-lg font-semibold text-black">Total Posts</h3>
              <p className="text-2xl font-bold">{trendSummary.totalPosts}</p>
            </div>
            <div className="p-4 bg-green-100 rounded-lg text-center">
              <h3 className="text-lg font-semibold text-black">Avg. Relevance</h3>
              <p className="text-2xl font-bold">{trendSummary.avgRelevance}</p>
            </div>
            <div className="p-4 bg-yellow-100 rounded-lg text-center">
              <h3 className="text-lg font-semibold text-black">Trend</h3>
              <p className="text-2xl font-bold">{trendSummary.trend}</p>
            </div>
            <div className="p-4 bg-red-100 rounded-lg text-center">
              <h3 className="text-lg font-semibold text-black">High Priority</h3>
              <p className="text-2xl font-bold">{trendSummary.highPriority}</p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-2 text-black">Posts by Intent</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trendSummary.byIntent}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563EB" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2 text-black">Posts by Subreddit</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={trendSummary.bySubreddit}
                    dataKey="count"
                    nameKey="name"
                    outerRadius={100}
                    label
                  >
                    {trendSummary.bySubreddit.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>

      {loading && posts.length === 0 ? (
        <div className="flex grid-cols-1 md:grid-cols-3 gap-6">Loading data...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Card key={post._key || post.post_id} className="col-span-1 shadow">
              <CardContent className="p-6">
                <h2 className="text-xl text-black font-semibold mb-2">{post.post_title}</h2>
                <p className="text-gray-700 mb-4">{post.post_summary}</p>

                <h2 className="text-lg text-black font-semibold mb-2">Engagement Comment</h2>
                <p className="text-gray-700 mb-4">{post.engagement_comment}</p>

                <h2 className="text-lg text-black font-semibold mb-2">Engagement Strategy</h2>
                <p className="text-gray-700 mb-4">{post.engagement_strategy}</p>

                <div className="flex flex-wrap gap-2 text-sm mb-3">
                  <span className="px-2 py-1 bg-blue-500 rounded-sm">{post.subreddit}</span>
                  <span className="px-2 py-1 bg-green-500 rounded-sm">{post.intent}</span>
                  <span className="px-2 py-1 bg-red-400 rounded-sm">{post.sentiment}</span>
                  <span className="px-2 py-1 bg-yellow-400 rounded-sm">
                    {Math.round((post.relevance_score || 0) * 100)}%
                  </span>
                </div>

                <div className="flex flex-col text-sm mb-3 gap-1">
                  <span className="text-black">-{post.author}</span>
                  <span className="text-black">{post.timestamp}</span>
                </div>

                {post.post_link ? (
                  <a
                    href={post.post_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline"
                  >
                    View Original Post
                  </a>
                ) : (
                  <div className="text-xs text-gray-500">No original link</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
      
    </div>
  );
}
  