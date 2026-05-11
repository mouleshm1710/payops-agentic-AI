import { useEffect, useState } from "react";
import {
  askAgent,
  getPayrollExceptions,
  getOvertimeTrends,
  getTicketStatus,
  getDeductionSummary,
  getHighRiskRecords,
} from "./services/api";

const samplePrompts = [
   "Can you explain why my net pay decreased compared to the previous pay cycle?",
   "Why is my overtime payment still pending and what approval is missing?",
   "Can you explain the PTO carry-over policy and maximum allowed balance?",
   "Were there any payroll anomalies or risk flags detected for my payroll record?",
];

function App() {
  const [activeTab, setActiveTab] = useState("assistant");
  const [question, setQuestion] = useState("");
  const [employeeId, setEmployeeId] = useState("E0002");
  const [sessionId, setSessionId] = useState("session_1");
  const [response, setResponse] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const [analytics, setAnalytics] = useState({
    exceptions: [],
    overtime: [],
    tickets: [],
    deductions: [],
    highRisk: [],
  });
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  useEffect(() => {
    if (activeTab === "payroll") {
      loadAnalytics();
    }
  }, [activeTab]);

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);

      const [exceptions, overtime, tickets, deductions, highRisk] = await Promise.all([
        getPayrollExceptions(),
        getOvertimeTrends(),
        getTicketStatus(),
        getDeductionSummary(),
        getHighRiskRecords(),
      ]);

      setAnalytics({
        exceptions: exceptions.records || exceptions.data || [],
        overtime: overtime.records || overtime.data || [],
        tickets: tickets.records || tickets.data || [],
        deductions: deductions.records || deductions.data || [],
        highRisk: highRisk.records || highRisk.data || [],
      });
    } catch (error) {
      console.error("Analytics load failed", error);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newSession = `session_${Date.now()}`;
    setSessionId(newSession);
    setMessages([]);
    setResponse(null);
    setQuestion("");
    setEmployeeId("E0002");
    setActiveTab("assistant");
  };

  const handleAsk = async (customQuestion) => {
    const finalQuestion = customQuestion || question;
    if (!finalQuestion.trim()) return;

    setLoading(true);
    setQuestion("");
    setActiveTab("assistant");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: finalQuestion,
        employeeId,
      },
    ]);

    try {
      const result = await askAgent({
        session_id: sessionId,
        employee_id: employeeId,
        user_question: finalQuestion,
      });

      setResponse(result);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          intent: result.intent,
          confidence: result.confidence,
        },
      ]);
    } catch (error) {
      console.error(error);
      alert("Backend request failed");
    } finally {
      setLoading(false);
    }
  };

  const maxValue = (data, key) => {
    if (!data?.length) return 1;
    return Math.max(...data.map((item) => Number(item[key]) || 0), 1);
  };

  return (
    <div style={styles.page}>
      <aside style={styles.sidebar}>
        <div>
          <h2 style={styles.logo}>PayOps AI</h2>
          <p style={styles.sidebarText}>Agentic Payroll Intelligence</p>

          <div style={styles.navSection}>
            <button
              style={activeTab === "assistant" ? styles.activeNav : styles.navItem}
              onClick={() => setActiveTab("assistant")}
            >
              AI Assistant
            </button>

            <button
              style={activeTab === "workflow" ? styles.activeNav : styles.navItem}
              onClick={() => setActiveTab("workflow")}
            >
              Workflow Monitor
            </button>

            <button
              style={activeTab === "payroll" ? styles.activeNav : styles.navItem}
              onClick={() => setActiveTab("payroll")}
            >
              Payroll Exceptions
            </button>
          </div>
        </div>

        <div style={styles.sidebarFooter}>
          <p style={styles.smallText}>Powered by</p>
          <p style={styles.stackText}>FastAPI • LangGraph • Azure SQL • AI Search</p>
        </div>
      </aside>

      <main style={styles.main}>
        {activeTab !== "payroll" && (
          <>
            <header style={styles.topbar}>
              <div>
                <p style={styles.eyebrow}>Enterprise Agentic AI Platform</p>
                <h1 style={styles.title}>Payroll Operations Copilot</h1>
                <p style={styles.subtitle}>
                  Resolve payroll queries, retrieve policy context, and visualize
                  agent workflow execution.
                </p>
              </div>

              <div style={styles.topbarActions}>
                <button onClick={handleNewChat} style={styles.newChatButton}>
                  New Chat
                </button>

                <div style={styles.statusCard}>
                  <span style={styles.statusDot}></span>
                  Backend Connected
                </div>
              </div>
            </header>

            <section style={styles.kpiGrid}>
              <Kpi title="Agent Mode" value="Planner + RAG" />
              <Kpi title="Workflow" value={`${response?.workflow_trace?.length || 0} steps`} />
              <Kpi title="Intent" value={response?.intent || "Waiting"} />
              <Kpi title="Employee" value={employeeId || "--"} />
            </section>
          </>
        )}

        {activeTab === "assistant" && (
          <section style={styles.chatCard}>
            <div style={styles.cardHeader}>
              <h3>AI Payroll Assistant</h3>
              <span style={styles.badge}>Live Agent Workflow</span>
            </div>

            <div style={styles.controlRow}>
              <div>
                <label style={styles.label}>Employee ID</label>
                <input
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  placeholder="E0002"
                  style={styles.employeeInput}
                />
              </div>

              <div>
                <label style={styles.label}>Session</label>
                <input value={sessionId} readOnly style={styles.sessionInput} />
              </div>
            </div>

            <div style={styles.promptGrid}>
              {samplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  style={styles.promptChip}
                  onClick={() => handleAsk(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div style={styles.chatWindow}>
              {messages.length === 0 && (
                <div style={styles.emptyChat}>
                  Ask a payroll, PTO, deduction, overtime, or policy question to
                  start the workflow.
                </div>
              )}

              {messages.map((msg, index) => (
                <div
                  key={index}
                  style={
                    msg.role === "user"
                      ? styles.userBubbleWrapper
                      : styles.aiBubbleWrapper
                  }
                >
                  <div style={msg.role === "user" ? styles.userBubble : styles.aiBubble}>
                    <strong>{msg.role === "user" ? "You" : "PayOps AI"}</strong>

                    {msg.role === "user" && (
                      <p style={styles.employeeTag}>Employee: {msg.employeeId}</p>
                    )}

                    <div
                      style={styles.messageText}
                      dangerouslySetInnerHTML={{
                        __html: formatMessage(msg.content),
                      }}
                    />

                    {msg.role === "assistant" && (
                      <div style={styles.messageMeta}>
                        <span>Intent: {msg.intent}</span>
                        <span>Confidence: {msg.confidence}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div style={styles.aiBubbleWrapper}>
                  <div style={styles.aiBubble}>
                    <strong>PayOps AI</strong>
                    <p style={styles.messageText}>
                      Running planner, retrieval, and reasoning workflow...
                    </p>
                  </div>
                </div>
              )}
            </div>

            <div style={styles.inputRow}>
              <textarea
                rows="2"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask your payroll or HR operations question..."
                style={styles.textarea}
              />

              <button onClick={() => handleAsk()} style={styles.button}>
                {loading ? "Running..." : "Send"}
              </button>
            </div>
          </section>
        )}

        {activeTab === "workflow" && <Timeline response={response} />}

        {activeTab === "payroll" && (
          <section style={styles.dashboardCard}>
            <div style={styles.dashboardHeader}>
              <div>
                <p style={styles.eyebrow}>HR / Payroll Operations View</p>
                <h1 style={styles.dashboardTitle}>Payroll Exceptions Dashboard</h1>
                <p style={styles.subtitle}>
                  Monitor payroll risk levels, timesheet bottlenecks, anomaly
                  patterns, and payroll ticket workload across the organization.
                </p>
              </div>

              <div style={styles.topbarActions}>
                <button onClick={loadAnalytics} style={styles.newChatButton}>
                  Refresh Data
                </button>

                <div style={styles.statusCard}>
                  <span style={styles.statusDot}></span>
                  Azure SQL Connected
                </div>
              </div>
            </div>

            <section style={styles.dashboardKpiGrid}>
              <Kpi
                title="Risk Categories"
                value={analytics.exceptions.length}
              />
              <Kpi
                title="Timesheet Groups"
                value={analytics.overtime.length}
              />
              <Kpi
                title="Ticket Status Groups"
                value={analytics.tickets.length}
              />
              <Kpi
                title="Anomaly Types"
                value={analytics.deductions.length}
              />
            </section>

            {analyticsLoading && (
              <p style={styles.emptyText}>Loading latest payroll operations data...</p>
            )}

            <section style={styles.tableSection}>
                <div style={styles.cardHeader}>
                  <h3>High Risk Payroll Exceptions</h3>
                  <span style={styles.badge}>Operational Drilldown</span>
                </div>

                <div style={styles.tableWrapper}>
                  <table style={styles.table}>
                   <thead>
                    <tr>
                      <th style={styles.tableHeaderCell}>Employee</th>
                      <th style={styles.tableHeaderCell}>Risk</th>
                      <th style={styles.tableHeaderCell}>Score</th>
                      <th style={styles.tableHeaderCell}>Approval</th>
                      <th style={styles.tableHeaderCell}>Timesheet</th>
                      <th style={styles.tableHeaderCell}>Net Pay Change</th>
                      <th style={styles.tableHeaderCell}>Issue</th>
                    </tr>
                  </thead>

                    <tbody>
                      {analytics.highRisk?.map((row, index) => (
                        <tr key={index} style={styles.tableRow}>
                          <td style={styles.tableCell}>{row.employee_id}</td>
                          <td style={styles.tableCell}>{row.risk_level}</td>
                          <td style={styles.tableCell}>{row.risk_score}</td>
                          <td style={styles.tableCell}>{row.approval_status}</td>
                          <td style={styles.tableCell}>{row.timesheet_status}</td>
                          <td style={styles.tableCell}>{Number(row.net_pay_change)?.toFixed?.(2)}</td>
                          <td style={styles.tableCell}>{row.issue_summary}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

            <div style={styles.chartGrid}>
              <BarChart
                title="Payroll Risk Levels"
                data={analytics.exceptions}
                labelKey="risk_level"
                valueKey="count_records"
                max={maxValue(analytics.exceptions, "count_records")}
              />

              <BarChart
                title="Timesheet Status"
                data={analytics.overtime}
                labelKey="timesheet_status"
                valueKey="count_records"
                max={maxValue(analytics.overtime, "count_records")}
              />

              <BarChart
                title="Payroll Ticket Status"
                data={analytics.tickets}
                labelKey="ticket_status"
                valueKey="ticket_count"
                max={maxValue(analytics.tickets, "ticket_count")}
              />

              <BarChart
                title="Top Anomaly Types"
                data={analytics.deductions}
                labelKey="anomaly_type"
                valueKey="count_records"
                max={maxValue(analytics.deductions, "count_records")}
              />
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function formatMessage(text) {
  return (text || "")
    .replace(/\*\*/g, "")
    .replace(/###/g, "")
    .replace(/\n/g, "<br/>");
}

function Kpi({ title, value }) {
  return (
    <div style={styles.kpiCard}>
      <p style={styles.kpiLabel}>{title}</p>
      <h3 style={styles.kpiValue}>{value}</h3>
    </div>
  );
}

function Timeline({ response }) {
  return (
    <section style={styles.timelineSection}>
      <div style={styles.cardHeader}>
        <h3>Agent Execution Timeline</h3>
        <span style={styles.badge}>Orchestration Trace</span>
      </div>

      {!response && (
        <p style={styles.emptyText}>
          The workflow timeline will appear here after the first query.
        </p>
      )}

      {response && (
        <div style={styles.timelineGrid}>
          {response.workflow_trace?.map((step, index) => (
            <div key={index} style={styles.timelineItem}>
              <div style={styles.timelineMarker}>{index + 1}</div>
              <div>
                <strong>{step.step}</strong>
                <p style={styles.traceText}>{step.details}</p>
                <span style={styles.completed}>{step.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function BarChart({ title, data, labelKey, valueKey, max }) {
  return (
    <div style={styles.chartCard}>
      <h3>{title}</h3>

      {!data?.length && <p style={styles.emptyText}>No data available.</p>}

      {data?.map((item, index) => {
        const value = Number(item[valueKey]) || 0;
        const width = `${Math.max((value / max) * 100, 8)}%`;

        return (
          <div key={index} style={styles.barRow}>
            <div style={styles.barLabel}>
              {item[labelKey] || "Unknown"}
              <span>{value}</span>
            </div>
            <div style={styles.barTrack}>
              <div style={{ ...styles.barFill, width }}></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    background:
      "linear-gradient(135deg, #eef4ff 0%, #f8fafc 45%, #f1f5f9 100%)",
    fontFamily: "Inter, Arial, sans-serif",
    color: "#0f172a",
  },
  sidebar: {
    width: "260px",
    background: "#07111f",
    color: "white",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  logo: { margin: 0, fontSize: "24px" },
  sidebarText: { color: "#94a3b8", fontSize: "13px" },
  navSection: { marginTop: "32px" },
  activeNav: {
    width: "100%",
    border: "none",
    textAlign: "left",
    background: "#2563eb",
    color: "white",
    padding: "12px 14px",
    borderRadius: "13px",
    marginBottom: "10px",
    fontWeight: 700,
    cursor: "pointer",
  },
  navItem: {
    width: "100%",
    border: "none",
    textAlign: "left",
    background: "rgba(255,255,255,0.06)",
    padding: "12px 14px",
    borderRadius: "13px",
    marginBottom: "10px",
    color: "#cbd5e1",
    cursor: "pointer",
  },
  sidebarFooter: {
    background: "rgba(255,255,255,0.06)",
    padding: "14px",
    borderRadius: "16px",
  },
  smallText: { color: "#94a3b8", fontSize: "12px", margin: 0 },
  stackText: { fontSize: "12px", marginBottom: 0 },
  main: { flex: 1, padding: "28px", overflow: "auto" },
  topbar: {
    display: "flex",
    justifyContent: "space-between",
    gap: "24px",
    alignItems: "flex-start",
    marginBottom: "22px",
  },
  dashboardHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: "24px",
    alignItems: "flex-start",
    marginBottom: "24px",
  },
  topbarActions: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
  },
  eyebrow: {
    color: "#2563eb",
    fontWeight: 800,
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
  },
  title: { fontSize: "36px", margin: "6px 0" },
  dashboardTitle: { fontSize: "34px", margin: "6px 0" },
  subtitle: {
    color: "#64748b",
    maxWidth: "760px",
    fontSize: "15px",
    lineHeight: 1.55,
  },
  newChatButton: {
    background: "#0f172a",
    color: "white",
    border: "none",
    padding: "11px 15px",
    borderRadius: "999px",
    cursor: "pointer",
    fontWeight: 800,
  },
  statusCard: {
    background: "white",
    padding: "11px 15px",
    borderRadius: "999px",
    boxShadow: "0 12px 30px rgba(15,23,42,0.08)",
    fontSize: "13px",
    fontWeight: 700,
    display: "flex",
    alignItems: "center",
    gap: "8px",
    whiteSpace: "nowrap",
  },
  statusDot: {
    width: "9px",
    height: "9px",
    background: "#22c55e",
    borderRadius: "50%",
  },
  kpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "14px",
    marginBottom: "20px",
  },
  dashboardKpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "14px",
    marginBottom: "20px",
  },
  kpiCard: {
    background: "white",
    padding: "18px",
    borderRadius: "18px",
    boxShadow: "0 12px 30px rgba(15,23,42,0.07)",
  },
  kpiLabel: { color: "#64748b", margin: 0, fontSize: "12px" },
  kpiValue: { margin: "7px 0 0", fontSize: "19px" },
  chatCard: card(),
  dashboardCard: card(),
  timelineSection: card(),
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    marginBottom: "14px",
  },
  badge: {
    background: "#dbeafe",
    color: "#1d4ed8",
    padding: "7px 10px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: 800,
  },
  controlRow: {
    display: "flex",
    gap: "14px",
    marginBottom: "14px",
  },
  label: {
    display: "block",
    fontSize: "12px",
    color: "#64748b",
    fontWeight: 800,
    marginBottom: "6px",
  },
  employeeInput: inputStyle(),
  sessionInput: {
    ...inputStyle(),
    background: "#f8fafc",
    color: "#64748b",
    width: "240px",
  },
  promptGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "9px",
    marginBottom: "14px",
  },
  promptChip: {
    border: "1px solid #dbe4f0",
    background: "#f8fafc",
    padding: "10px",
    borderRadius: "13px",
    cursor: "pointer",
    textAlign: "left",
    color: "#334155",
    fontSize: "12px",
  },
  chatWindow: {
    minHeight: "250px",
    maxHeight: "340px",
    overflowY: "auto",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    padding: "16px",
    marginBottom: "14px",
  },
  emptyChat: {
    color: "#64748b",
    textAlign: "center",
    marginTop: "95px",
  },
  userBubbleWrapper: {
    display: "flex",
    justifyContent: "flex-end",
    marginBottom: "13px",
  },
  aiBubbleWrapper: {
    display: "flex",
    justifyContent: "flex-start",
    marginBottom: "13px",
  },
  userBubble: {
    maxWidth: "72%",
    background: "#2563eb",
    color: "white",
    padding: "13px 15px",
    borderRadius: "18px 18px 4px 18px",
  },
  aiBubble: {
    maxWidth: "78%",
    background: "white",
    color: "#0f172a",
    padding: "13px 15px",
    borderRadius: "18px 18px 18px 4px",
    boxShadow: "0 8px 22px rgba(15,23,42,0.06)",
  },
  employeeTag: {
    fontSize: "12px",
    margin: "6px 0 0",
    opacity: 0.85,
  },
  messageText: {
    margin: "8px 0 0",
    lineHeight: 1.65,
    whiteSpace: "normal",
  },
  messageMeta: {
    display: "flex",
    gap: "10px",
    marginTop: "12px",
    fontSize: "12px",
    color: "#475569",
    fontWeight: 700,
  },
  inputRow: {
    display: "grid",
    gridTemplateColumns: "1fr 110px",
    gap: "12px",
  },
  textarea: {
    width: "100%",
    padding: "13px",
    borderRadius: "15px",
    border: "1px solid #cbd5e1",
    fontSize: "14px",
    resize: "vertical",
    outline: "none",
    boxSizing: "border-box",
  },
  button: {
    background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
    color: "white",
    border: "none",
    padding: "13px 17px",
    borderRadius: "15px",
    cursor: "pointer",
    fontWeight: 800,
    fontSize: "14px",
  },
  timelineGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: "14px",
  },
  timelineItem: {
    display: "grid",
    gridTemplateColumns: "34px 1fr",
    gap: "12px",
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "16px",
    padding: "15px",
  },
  timelineMarker: {
    width: "30px",
    height: "30px",
    borderRadius: "50%",
    background: "#2563eb",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 800,
    fontSize: "12px",
  },
  traceText: {
    margin: "5px 0",
    color: "#64748b",
    fontSize: "13px",
    lineHeight: 1.5,
  },
  completed: {
    color: "#16a34a",
    fontSize: "12px",
    fontWeight: 800,
    textTransform: "uppercase",
  },
  emptyText: { color: "#64748b", lineHeight: 1.6 },
  chartGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: "18px",
  },
  chartCard: {
    background: "#f8fafc",
    padding: "20px",
    borderRadius: "20px",
    border: "1px solid #e2e8f0",
  },
    tableSection: {
    marginTop: "24px",
  },

  tableWrapper: {
    overflowX: "auto",
    background: "#f8fafc",
    borderRadius: "18px",
    border: "1px solid #e2e8f0",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "14px",
  },

  tableHeaderCell: {
    background: "#eff6ff",
    padding: "14px 12px",
    border: "1px solid #e2e8f0",
    textAlign: "center",
    fontWeight: 700,
  },

  tableCell: {
    padding: "14px 12px",
    border: "1px solid #e2e8f0",
    textAlign: "center",
    verticalAlign: "middle",
  },

  tableRow: {
    borderBottom: "1px solid #e2e8f0",
  },
  barRow: { marginBottom: "14px" },
  barLabel: {
    display: "flex",
    justifyContent: "space-between",
    fontSize: "13px",
    fontWeight: 700,
    marginBottom: "6px",
  },
  barTrack: {
    height: "12px",
    background: "#e2e8f0",
    borderRadius: "999px",
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    background: "linear-gradient(135deg, #2563eb, #60a5fa)",
    borderRadius: "999px",
  },
};

function card() {
  return {
    background: "rgba(255,255,255,0.95)",
    padding: "22px",
    borderRadius: "22px",
    boxShadow: "0 18px 45px rgba(15,23,42,0.08)",
    border: "1px solid rgba(226,232,240,0.9)",
    marginBottom: "22px",
  };
}

function inputStyle() {
  return {
    width: "170px",
    padding: "12px",
    borderRadius: "13px",
    border: "1px solid #cbd5e1",
    fontSize: "14px",
    outline: "none",
    boxSizing: "border-box",
  };
}

export default App;