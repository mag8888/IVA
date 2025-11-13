import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container-fluid">
          <Link className="navbar-brand" to="/">
            <i className="fas fa-chart-line"></i> Equilibrium MLM
          </Link>
          <div className="navbar-nav ms-auto">
            <Link 
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`} 
              to="/"
            >
              Дашборд
            </Link>
            <Link 
              className={`nav-link ${location.pathname === '/structure' ? 'active' : ''}`} 
              to="/structure"
            >
              Структура
            </Link>
            <Link 
              className={`nav-link ${location.pathname === '/queue' ? 'active' : ''}`} 
              to="/queue"
            >
              Очередь
            </Link>
          </div>
        </div>
      </nav>
      <main className="container-fluid mt-4">
        {children}
      </main>
    </div>
  )
}

