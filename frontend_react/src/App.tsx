import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Structure from './pages/Structure'
import Queue from './pages/Queue'
import Layout from './components/Layout'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/structure" element={<Structure />} />
          <Route path="/queue" element={<Queue />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

