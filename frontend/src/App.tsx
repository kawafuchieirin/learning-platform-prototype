import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Dashboard } from '@/pages/dashboard/Dashboard'
import { Analytics } from '@/pages/analytics/Analytics'
import Roadmap from '@/pages/roadmap/Roadmap'
import Records from '@/pages/records/Records'
import RecordsTest from '@/pages/RecordsTest'
import Test from '@/pages/Test'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/records" element={<Records />} />
          <Route path="/records-test" element={<RecordsTest />} />
          <Route path="/test" element={<Test />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App