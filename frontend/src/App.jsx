
import { useState } from 'react'
import './App.css'

function App() {
  const [isRegister, setIsRegister] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [activePage, setActivePage] = useState('Overview')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [message, setMessage] = useState('')

  const [selectedAccount, setSelectedAccount] = useState('')
  const [amount, setAmount] = useState('')
  const [sourceAccount, setSourceAccount] = useState('')
  const [destinationAccount, setDestinationAccount] = useState('')

  function handleSubmit(event) {
    event.preventDefault()

    // Temporary frontend demonstration.
    // Real API connection will be added in Phase 7.
    if (isRegister) {
      setMessage('Registration API connection will be added in Phase 7.')
    } else {
      setIsLoggedIn(true)
      setActivePage('Overview')
    }
  }

  function switchPage() {
    setIsRegister(!isRegister)
    setEmail('')
    setPassword('')
    setName('')
    setMessage('')
  }

  function logout() {
    setIsLoggedIn(false)
    setEmail('')
    setPassword('')
    setMessage('')
    setActivePage('Overview')
  }

  function handleMoneyMovement(event) {
    event.preventDefault()

    if (Number(amount) <= 0 || !Number.isFinite(Number(amount))) {
      setMessage('Please enter a valid amount greater than zero.')
      return
    }

    if (activePage === 'Deposit' && !selectedAccount) {
      setMessage('Please select an account.')
      return
    }

    if (activePage === 'Withdraw' && !selectedAccount) {
      setMessage('Please select an account.')
      return
    }

    if (activePage === 'Transfer') {
      if (!sourceAccount || !destinationAccount) {
        setMessage('Please select both accounts.')
        return
      }

      if (sourceAccount === destinationAccount) {
        setMessage('Source and destination accounts must be different.')
        return
      }
    }

    setMessage(
      `${activePage} form validated. Backend connection will be added in Phase 7.`
    )
  }

  function openPage(page) {
    setActivePage(page)
    setMessage('')
    setAmount('')
    setSelectedAccount('')
    setSourceAccount('')
    setDestinationAccount('')
  }

  if (!isLoggedIn) {
    return (
      <div className="app-container">
        <header className="navbar">
          <div className="brand">
            <div className="brand-icon">LL</div>
            <span>LedgerLine</span>
          </div>

          <span className="nav-caption">
            Secure Digital Banking
          </span>
        </header>

        <main className="login-section">
          <div className="login-card">
            <div className="welcome-icon">LL</div>

            <h1>
              {isRegister ? 'Create account' : 'Welcome back'}
            </h1>

            <p className="subtitle">
              {isRegister
                ? 'Join LedgerLine and manage your money securely.'
                : 'Sign in to access your LedgerLine account.'}
            </p>

            <form onSubmit={handleSubmit}>
              {isRegister && (
                <div className="form-group">
                  <label htmlFor="name">Full name</label>

                  <input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    required
                  />
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email address</label>

                <input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>

                <input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={8}
                  required
                />
              </div>

              <button type="submit" className="login-button">
                {isRegister ? 'Create account' : 'Sign in'}
              </button>
            </form>

            {message && (
              <p className="form-message">{message}</p>
            )}

            <p className="register-text">
              {isRegister
                ? 'Already have an account? '
                : "Don't have an account? "}

              <a
                href="#"
                onClick={(event) => {
                  event.preventDefault()
                  switchPage()
                }}
              >
                {isRegister ? 'Sign in' : 'Create an account'}
              </a>
            </p>

            <div className="security-note">
              Your financial information is protected.
            </div>
          </div>
        </main>

        <footer className="footer">
          © 2026 LedgerLine. All rights reserved.
        </footer>
      </div>
    )
  }

  return (
    <div className="dashboard-container">

      {/* Sidebar navigation */}
      <aside className="sidebar">
        <div className="brand dashboard-brand">
          <div className="brand-icon">LL</div>
          <span>LedgerLine</span>
        </div>

        <p className="sidebar-heading">MENU</p>

        {[
          'Overview',
          'My Accounts',
          'Transactions',
          'Deposit',
          'Withdraw',
          'Transfer'
        ].map((page) => (
          <button
            key={page}
            className={`nav-item ${
              activePage === page ? 'active' : ''
            }`}
            onClick={() => openPage(page)}
          >
            {page}
          </button>
        ))}

        <button className="logout-button" onClick={logout}>
          Logout
        </button>
      </aside>

      {/* Dashboard main content */}
      <main className="dashboard-main">

        <header className="dashboard-header">
          <div>
            <h1>{activePage}</h1>
            <p>Welcome to your LedgerLine dashboard.</p>
          </div>

          <div className="profile-circle">U</div>
        </header>

        {/* Overview page */}
        {activePage === 'Overview' && (
          <>
            <section className="balance-card">
              <p>Total available balance</p>
              <h2>₹0.00</h2>
              <span>INR · Demo display</span>
            </section>

            <section className="dashboard-cards">

              <div className="summary-card">
                <h3>My Accounts</h3>
                <p>View your bank accounts</p>

                <button onClick={() => openPage('My Accounts')}>
                  View accounts
                </button>
              </div>

              <div className="summary-card">
                <h3>Transactions</h3>
                <p>Check your transaction history</p>

                <button onClick={() => openPage('Transactions')}>
                  View transactions
                </button>
              </div>

            </section>

            <section className="coming-soon">
              <h3>Money movement</h3>

              <p>
                Deposit, withdraw and transfer features are being prepared.
              </p>

              <div className="money-shortcuts">
                <button onClick={() => openPage('Deposit')}>
                  Deposit
                </button>

                <button onClick={() => openPage('Withdraw')}>
                  Withdraw
                </button>

                <button onClick={() => openPage('Transfer')}>
                  Transfer
                </button>
              </div>
            </section>
          </>
        )}

        {/* My Accounts page */}
        {activePage === 'My Accounts' && (
          <section className="accounts-section">

            <div className="section-title">
              <div>
                <h2>Your Accounts</h2>
                <p>Manage and view your bank accounts.</p>
              </div>

              <button className="create-account-button">
                + Create Account
              </button>
            </div>

            <div className="account-card">

              <div className="account-card-header">
                <div>
                  <span className="account-label">
                    SAVINGS ACCOUNT
                  </span>

                  <h3>Primary Savings</h3>
                </div>

                <span className="status-active">Active</span>
              </div>

              <div className="account-number">
                Account Number: LLXXXXXXXXXX
              </div>

              <div className="account-balance">
                <p>Available Balance</p>
                <h2>₹0.00</h2>
              </div>

              <button className="view-balance-button">
                View Account Details
              </button>

            </div>
          </section>
        )}

        {/* Transactions page */}
        {activePage === 'Transactions' && (
          <section className="transactions-section">

            <div className="section-title">
              <div>
                <h2>Transaction History</h2>
                <p>
                  View your recent deposits, withdrawals and transfers.
                </p>
              </div>
            </div>

            <div className="transaction-summary">

              <div className="transaction-summary-card">
                <p>Total Transactions</p>
                <h3>3</h3>
              </div>

              <div className="transaction-summary-card">
                <p>Total Deposits</p>
                <h3>₹5,000.00</h3>
              </div>

              <div className="transaction-summary-card">
                <p>Total Withdrawals</p>
                <h3>₹1,000.00</h3>
              </div>

            </div>

            <div className="transaction-table-card">
              <h3>Recent Transactions</h3>

              <div className="table-wrapper">
                <table className="transaction-table">

                  <thead>
                    <tr>
                      <th>Transaction ID</th>
                      <th>Type</th>
                      <th>Amount</th>
                      <th>Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    <tr>
                      <td>#LL001</td>
                      <td>Deposit</td>
                      <td className="credit-amount">+₹3,000.00</td>
                      <td>08 Nov 2026</td>
                      <td>
                        <span className="transaction-status">Posted</span>
                      </td>
                    </tr>

                    <tr>
                      <td>#LL002</td>
                      <td>Withdrawal</td>
                      <td className="debit-amount">-₹1,000.00</td>
                      <td>07 Nov 2026</td>
                      <td>
                        <span className="transaction-status">Posted</span>
                      </td>
                    </tr>

                    <tr>
                      <td>#LL003</td>
                      <td>Deposit</td>
                      <td className="credit-amount">+₹2,000.00</td>
                      <td>06 Nov 2026</td>
                      <td>
                        <span className="transaction-status">Posted</span>
                      </td>
                    </tr>
                  </tbody>

                </table>
              </div>

              <p className="demo-note">
                These are sample transactions for frontend demonstration.
              </p>
            </div>

          </section>
        )}

        {/* Deposit page */}
        {activePage === 'Deposit' && (
          <section className="money-form-section">
            <div className="money-form-card">
              <h2>Deposit Money</h2>
              <p>Add money to your LedgerLine account.</p>

              <form onSubmit={handleMoneyMovement}>
                <div className="form-group">
                  <label htmlFor="deposit-account">Select account</label>

                  <select
                    id="deposit-account"
                    value={selectedAccount}
                    onChange={(event) => setSelectedAccount(event.target.value)}
                    required
                  >
                    <option value="">Choose an account</option>
                    <option value="6">Primary Savings (Demo)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="deposit-amount">Amount (₹)</label>

                  <input
                    id="deposit-amount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="Enter deposit amount"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                    required
                  />
                </div>

                <button type="submit" className="money-submit-button">
                  Continue Deposit
                </button>
              </form>

              {message && <p className="form-message">{message}</p>}
            </div>
          </section>
        )}

        {/* Withdraw page */}
        {activePage === 'Withdraw' && (
          <section className="money-form-section">
            <div className="money-form-card">
              <h2>Withdraw Money</h2>
              <p>Withdraw money from your LedgerLine account.</p>

              <form onSubmit={handleMoneyMovement}>
                <div className="form-group">
                  <label htmlFor="withdraw-account">Select account</label>

                  <select
                    id="withdraw-account"
                    value={selectedAccount}
                    onChange={(event) => setSelectedAccount(event.target.value)}
                    required
                  >
                    <option value="">Choose an account</option>
                    <option value="6">Primary Savings (Demo)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="withdraw-amount">Amount (₹)</label>

                  <input
                    id="withdraw-amount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="Enter withdrawal amount"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                    required
                  />
                </div>

                <button type="submit" className="money-submit-button">
                  Continue Withdrawal
                </button>
              </form>

              {message && <p className="form-message">{message}</p>}
            </div>
          </section>
        )}

        {/* Transfer page */}
        {activePage === 'Transfer' && (
          <section className="money-form-section">
            <div className="money-form-card">
              <h2>Transfer Money</h2>
              <p>Move money between your LedgerLine accounts.</p>

              <form onSubmit={handleMoneyMovement}>
                <div className="form-group">
                  <label htmlFor="source-account">From account</label>

                  <select
                    id="source-account"
                    value={sourceAccount}
                    onChange={(event) => setSourceAccount(event.target.value)}
                    required
                  >
                    <option value="">Choose source account</option>
                    <option value="6">Primary Savings (Demo)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="destination-account">To account</label>

                  <select
                    id="destination-account"
                    value={destinationAccount}
                    onChange={(event) => setDestinationAccount(event.target.value)}
                    required
                  >
                    <option value="">Choose destination account</option>
                    <option value="7">Secondary Savings (Demo)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="transfer-amount">Amount (₹)</label>

                  <input
                    id="transfer-amount"
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="Enter transfer amount"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                    required
                  />
                </div>

                <button type="submit" className="money-submit-button">
                  Continue Transfer
                </button>
              </form>

              {message && <p className="form-message">{message}</p>}
            </div>
          </section>
        )}

      </main>
    </div>
  )
}

export default App
