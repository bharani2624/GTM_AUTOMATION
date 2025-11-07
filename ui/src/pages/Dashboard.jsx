import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    axios.get(`${API}/trends?weeks=6`).then(r => {
      const weeks = r.data.weeks || []
      setTrends(weeks.map(w => ({
        week: String(w.week),
        count: w.count,
        avgRelevance: Number(w.avgRelevance || 0)
      })))
    }).finally(() => setLoading(false))
  }, [])

  return (
    <div style={{ padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <h2>GTM Discussions - Weekly Trends</h2>
      {loading ? <div>Loading...</div> : (
        <div style={{ height: 360 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="count" stroke="#8884d8" name="Posts" />
              <Line yAxisId="right" type="monotone" dataKey="avgRelevance" stroke="#82ca9d" name="Avg Relevance" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}


