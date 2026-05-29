import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { NotificationProvider } from './context/NotificationContext'
import { TransactionProvider } from './context/TransactionContext'
import { BudgetProvider } from './context/BudgetContext'
import { GoalProvider } from './context/GoalContext'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider defaultTheme="system">
        <NotificationProvider>
          <TransactionProvider>
            <BudgetProvider>
              <GoalProvider>
                <App />
              </GoalProvider>
            </BudgetProvider>
          </TransactionProvider>
        </NotificationProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
