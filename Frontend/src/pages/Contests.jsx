// Contests page component – NEET/JEE exam contests
// Layout: main content left, filter sidebar right. Light theme.
// Columns: Code, Name, Start, Length, Before start, Before registration (no Writers).
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Header from '../components/Header'
import './Contests.css'

function Contests() {
  const [upcomingContests, setUpcomingContests] = useState([])
  const [pastContests, setPastContests] = useState([])

  useEffect(() => {
    fetch('/api/contests')
      .then((res) => res.json())
      .then((data) => {
        setUpcomingContests(data.upcoming || [])
        setPastContests(data.past || [])
      })
      .catch((err) => console.error('Failed to load contests:', err))
  }, [])
  return (
    <div className="app app-contests">
      <Header />
      <main className="contests-main">
        <div className="contests-layout">
          {/* Left: Current/upcoming and past contests tables */}
          <div className="contests-content">
            <section className="contests-section">
              <h2 className="contests-section-title">Current or upcoming contests</h2>
              <div className="contests-table-wrapper">
                <table className="contests-table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Name</th>
                      <th>Start</th>
                      <th>Length</th>
                      <th>Before start</th>
                      <th>Before registration</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {upcomingContests.map((c) => (
                      <tr key={c.code}>
                        <td><span className="contest-code">{c.code}</span></td>
                        <td>
                          <Link to={`/exam/${c.code}`} state={{ name: c.name }} className="contest-name-link">{c.name}</Link>
                        </td>
                        <td><button type="button" className="date-link">{c.start}</button></td>
                        <td>{c.length}</td>
                        <td>{c.beforeStart}</td>
                        <td>{c.beforeReg}</td>
                        <td>
                          <Link to={`/exam/${c.code}`} state={{ name: c.name }} className="action-link">Start</Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="contests-section">
              <h2 className="contests-section-title">Past contests</h2>
              <div className="contests-table-wrapper">
                <table className="contests-table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Name</th>
                      <th>Start</th>
                      <th>Length</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {pastContests.map((c) => (
                      <tr key={c.code}>
                        <td><span className="contest-code">{c.code}</span></td>
                        <td>
                          <div className="past-name-cell">
                            <Link to={`/exam/${c.code}`} state={{ name: c.name }} className="contest-name-link">{c.name}</Link>
                            <div className="past-links">
                              <Link to={`/exam/${c.code}`} state={{ name: c.name }} className="action-link">Enter &gt;&gt;</Link>
                              <button type="button" className="action-link">Virtual participation &gt;&gt;</button>
                            </div>
                          </div>
                        </td>
                        <td><button type="button" className="date-link">{c.start}</button></td>
                        <td>{c.length}</td>
                        <td>
                          <div className="past-extra-cell">
                            <button type="button" className="action-link">Final standings</button>
                            <span className="participants">×{c.participants}</span>
                            {c.unrated && <span className="badge">Unrated allowed</span>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>

          {/* Right: Pay attention + Past contests filter */}
          <aside className="contests-sidebar">
            <div className="sidebar-block">
              <h3 className="sidebar-title">→ Pay attention</h3>
              <button type="button" className="sidebar-attention-link">
                Before contest NEET Mock 1 – Physics, Chemistry, Biology
              </button>
            </div>
            <div className="sidebar-block">
              <h3 className="sidebar-title">→ Past contests filter</h3>
              <div className="filter-form">
                <label className="filter-label">Contest type:</label>
                <select className="filter-select">
                  <option>Any</option>
                  <option>NEET</option>
                  <option>JEE Main</option>
                  <option>JEE Advanced</option>
                </select>
                <label className="filter-label">Rated:</label>
                <select className="filter-select">
                  <option>Doesn&apos;t matter</option>
                </select>
                <label className="filter-label">Tried:</label>
                <select className="filter-select">
                  <option>Doesn&apos;t matter</option>
                </select>
                <label className="filter-label">Substring:</label>
                <input type="text" className="filter-input" placeholder="In contest title" />
                <button type="button" className="filter-btn">Filter</button>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  )
}

export default Contests
