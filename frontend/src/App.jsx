
import { useState } from 'react'
import './App.css'
import API_BASE_URL from './api'

function App() {
  const [isRegister, setIsRegister] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [activePage, setActivePage] = useState('Overview')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [message, setMessage] = useState('')
  const [token, setToken] = useState('')
  const [currentUser, setCurrentUser] = useState(null)

  const [accounts, setAccounts] = useState([])
  const [loadingAccounts, setLoadingAccounts] = useState(false)

  const [transactions, setTransactions] = useState([])
  const [loadingTransactions, setLoadingTransactions] = useState(false)
  const [transactionError, setTransactionError] = useState('')

  const [selectedAccount, setSelectedAccount] = useState('')
  const [amount, setAmount] = useState('')
  const [sourceAccount, setSourceAccount] = useState('')
  const [destinationAccount, setDestinationAccount] = useState('')

  const [loading, setLoading] = useState(false)

  function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value || 0)
  }

  // Fetch the logged-in user's accounts and their balances.
  async function loadAccounts(loginToken) {
    setLoadingAccounts(true)

    try {
      const response = await fetch(`${API_BASE_URL}/accounts/`, {
        headers: {
          Authorization: `Bearer ${loginToken}`
        }
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error('Unable to load your accounts.')
      }

      const accountsWithBalances = await Promise.all(
        data.map(async (account) => {
          try {
            const balanceResponse = await fetch(
              `${API_BASE_URL}/accounts/${account.id}/balance`,
              {
                headers: {
                  Authorization: `Bearer ${loginToken}`
                }
              }
            )

            const balanceData = await balanceResponse.json()

            if (!balanceResponse.ok) {
              throw new Error('Unable to load balance.')
            }

            return {
              ...account,
              balance: balanceData.balance,
              balance_paise: balanceData.balance_paise,
              balanceError: false
            }
          } catch {
            return {
              ...account,
              balance: null,
              balance_paise: null,
              balanceError: true
            }
          }
        })
      )

      setAccounts(accountsWithBalances)
    } catch (error) {
      setAccounts([])
      setMessage(error.message)
    } finally {
      setLoadingAccounts(false)
    }
  }

  // Fetch the logged-in user's real transaction history.
  async function loadTransactions(loginToken) {
    setLoadingTransactions(true)
    setTransactionError('')

    try {
      const response = await fetch(
        `${API_BASE_URL}/transactions/history`,
        {
          headers: {
            Authorization: `Bearer ${loginToken}`
          }
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to load transaction history.'
        )
      }

      setTransactions(data)
    } catch (error) {
      setTransactions([])
      setTransactionError(
        error.message || 'Unable to load transaction history.'
      )
    } finally {
      setLoadingTransactions(false)
    }
  }

  // Format transaction date and time.
  function formatDate(dateValue) {
    if (!dateValue) return 'Date unavailable'

    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return 'Date unavailable'
    }

    return date.toLocaleString('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short'
    })
  }

  // Test backend connection.
  const testBackendConnection = async () => {
    try {
      setMessage('Checking backend connection...')

      const response = await fetch(`${API_BASE_URL}/health`)

      if (response.ok) {
        setMessage('Backend connection successful!')
      } else {
        setMessage('Backend responded, but something went wrong.')
      }
    } catch {
      setMessage('Cannot connect to backend. Check whether the server is running.')
    }
  }

  // Register or log in using the real backend.
  async function handleSubmit(event) {
    event.preventDefault()

    setMessage('')
    setLoading(true)

    try {
      if (isRegister) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            full_name: name,
            email: email,
            password: password
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Registration failed. Please check your details.'
          )
        }

        setMessage('Registration successful! Please sign in.')
        setIsRegister(false)
        setName('')
        setPassword('')
      } else {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: email,
            password: password
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Login failed. Please check your details.'
          )
        }

        const loginToken = data.access_token

        const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${loginToken}`
          }
        })

        const userData = await userResponse.json()

        if (!userResponse.ok) {
          throw new Error('Login successful, but unable to load your profile.')
        }

        setToken(loginToken)
        setCurrentUser(userData)
        setIsLoggedIn(true)
        setActivePage('Overview')
        setPassword('')
        setMessage('')

        await loadAccounts(loginToken)
        await loadTransactions(loginToken)
      }
    } catch (error) {
      setMessage(error.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  // Switch between login and registration.
  function switchPage() {
    setIsRegister(!isRegister)
    setEmail('')
    setPassword('')
    setName('')
    setMessage('')
  }

  // Logout.
  function logout() {
    setIsLoggedIn(false)
    setEmail('')
    setPassword('')
    setName('')
    setToken('')
    setCurrentUser(null)
    setAccounts([])
    setTransactions([])
    setTransactionError('')
    setMessage('')
    setActivePage('Overview')
  }

  // Convert rupees into paise accurately.
  function convertToPaise(amountText) {
    const cleanAmount = amountText.trim()

    if (!/^\d+(\.\d{1,2})?$/.test(cleanAmount)) {
      return null
    }

    const [rupeesPart, paisePart = ''] = cleanAmount.split('.')

    const amountPaise =
      Number(rupeesPart) * 100 + Number(paisePart.padEnd(2, '0'))

    if (!Number.isSafeInteger(amountPaise) || amountPaise <= 0) {
      return null
    }

    return amountPaise
  }

  // Handle deposits, withdrawals and transfers.
  async function handleMoneyMovement(event) {
    event.preventDefault()
    setMessage('')

    const amountPaise = convertToPaise(amount)

    if (amountPaise === null) {
      setMessage(
        'Please enter a valid amount with no more than two decimal places.'
      )
      return
    }

    // Handle deposit.
    if (activePage === 'Deposit') {
      if (!selectedAccount) {
        setMessage('Please select an account.')
        return
      }

      const selectedAccountData = accounts.find(
        (account) => account.id === Number(selectedAccount)
      )

      if (!selectedAccountData || selectedAccountData.status !== 'active') {
        setMessage('Please select an active account.')
        return
      }

      setLoading(true)

      try {
        const response = await fetch(
          `${API_BASE_URL}/transactions/deposit`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
              account_id: Number(selectedAccount),
              amount_paise: amountPaise,
              idempotency_key: crypto.randomUUID()
            })
          }
        )

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Deposit failed. Please try again.'
          )
        }

        setMessage(
          `Deposit successful! Transaction #${data.id}. Amount: ${formatCurrency(data.amount_paise / 100)}`
        )

        setAmount('')
        setSelectedAccount('')

        await loadAccounts(token)
        await loadTransactions(token)
      } catch (error) {
        setMessage(error.message || 'Unable to complete the deposit.')
      } finally {
        setLoading(false)
      }

      return
    }

    // Handle withdrawal.
    if (activePage === 'Withdraw') {
      if (!selectedAccount) {
        setMessage('Please select an account.')
        return
      }

      const selectedAccountData = accounts.find(
        (account) => account.id === Number(selectedAccount)
      )

      if (!selectedAccountData || selectedAccountData.status !== 'active') {
        setMessage('Please select an active account.')
        return
      }

      setLoading(true)

      try {
        const response = await fetch(
          `${API_BASE_URL}/transactions/withdraw`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
              account_id: Number(selectedAccount),
              amount_paise: amountPaise,
              idempotency_key: crypto.randomUUID()
            })
          }
        )

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Withdrawal failed. Please try again.'
          )
        }

        setMessage(
          `Withdrawal successful! Transaction #${data.id}. Amount: ${formatCurrency(data.amount_paise / 100)}`
        )

        setAmount('')
        setSelectedAccount('')

        await loadAccounts(token)
        await loadTransactions(token)
      } catch (error) {
        setMessage(error.message || 'Unable to complete the withdrawal.')
      } finally {
        setLoading(false)
      }

      return
    }

    // Handle transfer.
    if (activePage === 'Transfer') {
      if (!sourceAccount || !destinationAccount) {
        setMessage('Please select both accounts.')
        return
      }

      if (Number(sourceAccount) === Number(destinationAccount)) {
        setMessage('Source and destination accounts must be different.')
        return
      }

      const sourceAccountData = accounts.find(
        (account) => account.id === Number(sourceAccount)
      )

      const destinationAccountData = accounts.find(
        (account) => account.id === Number(destinationAccount)
      )

      if (!sourceAccountData || sourceAccountData.status !== 'active') {
        setMessage('Please select an active source account.')
        return
      }

      if (
        !destinationAccountData ||
        destinationAccountData.status !== 'active'
      ) {
        setMessage('Please select an active destination account.')
        return
      }

      setLoading(true)

      try {
        const response = await fetch(
          `${API_BASE_URL}/transactions/transfer`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
              source_account_id: Number(sourceAccount),
              destination_account_id: Number(destinationAccount),
              amount_paise: amountPaise,
              idempotency_key: crypto.randomUUID()
            })
          }
        )

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Transfer failed. Please try again.'
          )
        }

        setMessage(
          `Transfer successful! Transaction #${data.id}. Amount: ${formatCurrency(data.amount_paise / 100)}`
        )

        setAmount('')
        setSourceAccount('')
        setDestinationAccount('')

        await loadAccounts(token)
        await loadTransactions(token)
      } catch (error) {
        setMessage(error.message || 'Unable to complete the transfer.')
      } finally {
        setLoading(false)
      }

      return
    }
  }

  // Navigate between dashboard pages.
  function openPage(page) {
    setActivePage(page)
    setMessage('')
    setAmount('')
    setSelectedAccount('')
    setSourceAccount('')
    setDestinationAccount('')

    if (page === 'Transactions' && token) {
      loadTransactions(token)
    }
  }

  const totalBalance = accounts.reduce((total, account) => {
    return total + (account.balance_paise ?? 0)
  }, 0)

  // Login and registration screen.
  if (!isLoggedIn) {
    return (
      <div className="app-container">
        <header className="navbar">
          <div className="brand">
            <div className="brand-icon">LL</div>
            <span>LedgerLine</span>
          </div>

          <span className="nav-caption">Secure Digital Banking</span>
        </header>

        <main className="login-section">
          <div className="login-card">
            <div className="welcome-icon">LL</div>

            <h1>{isRegister ? 'Create account' : 'Welcome back'}</h1>

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
                    minLength={2}
                    maxLength={100}
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
                  maxLength={128}
                  required
                />
              </div>

              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading
                  ? 'Please wait...'
                  : isRegister
                    ? 'Create account'
                    : 'Sign in'}
              </button>
            </form>

            {message && <p className="form-message">{message}</p>}

            <button
              type="button"
              className="login-button"
              onClick={testBackendConnection}
              disabled={loading}
            >
              Test Backend Connection
            </button>

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

  // Dashboard screen.
  return (
    <div className="dashboard-container">
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
            className={`nav-item ${activePage === page ? 'active' : ''}`}
            onClick={() => openPage(page)}
          >
            {page}
          </button>
        ))}

        <button className="logout-button" onClick={logout}>
          Logout
        </button>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>{activePage}</h1>
            <p>Welcome, {currentUser?.full_name || 'User'}!</p>
          </div>

          <div className="profile-circle">
            {(currentUser?.full_name || 'U').charAt(0).toUpperCase()}
          </div>
        </header>

        {/* Overview page */}
        {activePage === 'Overview' && (
          <>
            <section className="balance-card">
              <p>Total available balance</p>
              <h2>{formatCurrency(totalBalance / 100)}</h2>
              <span>INR · Based on your ledger accounts</span>
            </section>

            <section className="dashboard-cards">
              <div className="summary-card">
                <h3>My Accounts</h3>
                <p>{accounts.length} account(s) found</p>

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
                Deposits, withdrawals and transfers are connected.
              </p>

              <div className="money-shortcuts">
                <button onClick={() => openPage('Deposit')}>Deposit</button>
                <button onClick={() => openPage('Withdraw')}>Withdraw</button>
                <button onClick={() => openPage('Transfer')}>Transfer</button>
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
            </div>

            {loadingAccounts ? (
              <p>Loading your accounts...</p>
            ) : accounts.length === 0 ? (
              <div className="account-card">
                <h3>No accounts found</h3>
                <p>You do not have any accounts yet.</p>
              </div>
            ) : (
              <div className="accounts-list">
                {accounts.map((account) => (
                  <div className="account-card" key={account.id}>
                    <div className="account-card-header">
                      <div>
                        <span className="account-label">
                          {account.account_type.toUpperCase()} ACCOUNT
                        </span>

                        <h3>{account.account_type} Account</h3>
                      </div>

                      <span
                        className={
                          account.status === 'active'
                            ? 'status-active'
                            : 'transaction-status'
                        }
                      >
                        {account.status}
                      </span>
                    </div>

                    <div className="account-number">
                      Account Number: {account.account_number}
                    </div>

                    <div className="account-balance">
                      <p>Available Balance</p>
                      <h2>
                        {account.balanceError
                          ? 'Balance unavailable'
                          : formatCurrency(account.balance)}
                      </h2>
                    </div>

                    <p>Currency: {account.currency}</p>
                  </div>
                ))}
              </div>
            )}
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

              <button
                type="button"
                onClick={() => loadTransactions(token)}
                disabled={loadingTransactions}
              >
                {loadingTransactions ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            <div className="transaction-table-card">
              <h3>Recent Transactions</h3>

              {loadingTransactions ? (
                <p>Loading your transaction history...</p>
              ) : transactionError ? (
                <p className="form-message">{transactionError}</p>
              ) : transactions.length === 0 ? (
                <p>No transactions found for your accounts.</p>
              ) : (
                <div className="transaction-table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Transaction ID</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Source Account</th>
                        <th>Destination Account</th>
                        <th>Date</th>
                        <th>Status</th>
                      </tr>
                    </thead>

                    <tbody>
                      {transactions.map((transaction) => (
                        <tr key={transaction.id}>
                          <td>#{transaction.id}</td>

                          <td>
                            {transaction.transaction_type
                              .charAt(0)
                              .toUpperCase() +
                              transaction.transaction_type.slice(1)}
                          </td>

                          <td>
                            {formatCurrency(transaction.amount_paise / 100)}
                          </td>

                          <td>
                            {transaction.source_account_id ?? '—'}
                          </td>

                          <td>
                            {transaction.destination_account_id ?? '—'}
                          </td>

                          <td>{formatDate(transaction.created_at)}</td>

                          <td>
                            <span
                              className={
                                transaction.status === 'posted'
                                  ? 'status-active'
                                  : 'transaction-status'
                              }
                            >
                              {transaction.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
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

                    {accounts
                      .filter((account) => account.status === 'active')
                      .map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.account_number} - {account.account_type}
                        </option>
                      ))}
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

                <button
                  type="submit"
                  className="money-submit-button"
                  disabled={loading}
                >
                  {loading ? 'Processing Deposit...' : 'Continue Deposit'}
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

                    {accounts
                      .filter((account) => account.status === 'active')
                      .map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.account_number} - {account.account_type}
                        </option>
                      ))}
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

                <button
                  type="submit"
                  className="money-submit-button"
                  disabled={loading}
                >
                  {loading ? 'Processing Withdrawal...' : 'Continue Withdrawal'}
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

                    {accounts
                      .filter((account) => account.status === 'active')
                      .map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.account_number} - {account.account_type}
                        </option>
                      ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="destination-account">To account</label>

                  <select
                    id="destination-account"
                    value={destinationAccount}
                    onChange={(event) =>
                      setDestinationAccount(event.target.value)
                    }
                    required
                  >
                    <option value="">Choose destination account</option>

                    {accounts
                      .filter((account) => account.status === 'active')
                      .map((account) => (
                        <option key={account.id} value={account.id}>
                          {account.account_number} - {account.account_type}
                        </option>
                      ))}
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

                <button
                  type="submit"
                  className="money-submit-button"
                  disabled={loading}
                >
                  {loading ? 'Processing Transfer...' : 'Continue Transfer'}
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
