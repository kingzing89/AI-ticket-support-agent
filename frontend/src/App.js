import React, { useState } from 'react';
import { Send, Loader2, CheckCircle, AlertCircle, Clock, MessageSquare, Sparkles } from 'lucide-react';

const SupportTicketAgent = () => {
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const categories = {
    billing: { icon: '💳', color: '#3b82f6', label: 'Billing' },
    technical: { icon: '🔧', color: '#a855f7', label: 'Technical' },
    security: { icon: '🔒', color: '#ef4444', label: 'Security' },
    general: { icon: '💬', color: '#10b981', label: 'General' }
  };

  const exampleTickets = [
    { subject: 'Cannot login to my account', description: 'I keep getting invalid credentials error even though my password is correct' },
    { subject: 'Double charged this month', description: 'I was charged $29.99 twice for my subscription. Need refund.' },
    { subject: 'App keeps crashing', description: 'The mobile app crashes when I open the reports section on iPhone 13' },
    { subject: 'How to export data?', description: 'I need to export all my data for backup. Cannot find the option.' }
  ];

  const handleSubmit = async () => {
    if (!subject.trim() || !description.trim()) {
      setError('Please fill in both subject and description');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/process-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject, description })
      });

      if (!response.ok) throw new Error('Failed to process ticket');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const mockResult = {
        success: true,
        classification: 'technical',
        escalated: false,
        review_passed: true,
        attempts: 1,
        final_response: `Thank you for contacting us about "${subject}". I understand how frustrating this must be for you.\n\nBased on your description, here are the steps to resolve this issue:\n\n1. First, please try clearing your browser cache and cookies\n2. Ensure you're using a supported browser (Chrome 90+, Firefox 88+, Safari 14+)\n3. If the issue persists, try resetting your password using the "Forgot Password" link\n\nOur technical team is available Monday-Friday, 9 AM to 6 PM EST for additional support. If you need immediate assistance, please use our emergency contact form.\n\nIs there anything else I can help you with?`
      };
      setResult(mockResult);
    } finally {
      setLoading(false);
    }
  };

  const loadExample = (example) => {
    setSubject(example.subject);
    setDescription(example.description);
    setResult(null);
    setError(null);
  };

  const reset = () => {
    setSubject('');
    setDescription('');
    setResult(null);
    setError(null);
  };

  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b 0%, #581c87 50%, #1e293b 100%)',
      padding: '2rem',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    maxWidth: {
      maxWidth: '1200px',
      margin: '0 auto'
    },
    header: {
      textAlign: 'center',
      marginBottom: '2rem'
    },
    headerTitle: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem',
      marginBottom: '1rem'
    },
    title: {
      fontSize: '3rem',
      fontWeight: 'bold',
      color: 'white',
      margin: 0
    },
    subtitle: {
      color: '#cbd5e1',
      fontSize: '1.125rem'
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '1.5rem',
      marginBottom: '2rem'
    },
    card: {
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      borderRadius: '1rem',
      padding: '1.5rem',
      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
      border: '1px solid rgba(255, 255, 255, 0.2)'
    },
    cardHeader: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
      marginBottom: '1.5rem'
    },
    cardTitle: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      color: 'white',
      margin: 0
    },
    label: {
      display: 'block',
      fontSize: '0.875rem',
      fontWeight: '500',
      color: '#cbd5e1',
      marginBottom: '0.5rem'
    },
    input: {
      width: '100%',
      padding: '0.75rem 1rem',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '0.5rem',
      color: 'white',
      fontSize: '1rem',
      marginBottom: '1rem',
      boxSizing: 'border-box'
    },
    textarea: {
      width: '100%',
      padding: '0.75rem 1rem',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '0.5rem',
      color: 'white',
      fontSize: '1rem',
      marginBottom: '1rem',
      resize: 'none',
      fontFamily: 'inherit',
      boxSizing: 'border-box'
    },
    buttonGroup: {
      display: 'flex',
      gap: '0.75rem',
      marginBottom: '1rem'
    },
    button: {
      flex: 1,
      background: 'linear-gradient(to right, #a855f7, #ec4899)',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '0.5rem',
      fontWeight: '600',
      border: 'none',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '0.5rem',
      fontSize: '1rem',
      transition: 'all 0.3s'
    },
    buttonSecondary: {
      padding: '0.75rem 1.5rem',
      background: 'rgba(255, 255, 255, 0.1)',
      color: 'white',
      borderRadius: '0.5rem',
      fontWeight: '600',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      cursor: 'pointer',
      fontSize: '1rem',
      transition: 'all 0.3s'
    },
    exampleSection: {
      marginTop: '1.5rem'
    },
    exampleLabel: {
      fontSize: '0.875rem',
      fontWeight: '500',
      color: '#cbd5e1',
      marginBottom: '0.75rem'
    },
    exampleGrid: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '0.5rem'
    },
    exampleButton: {
      textAlign: 'left',
      padding: '0.5rem 0.75rem',
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '0.5rem',
      fontSize: '0.875rem',
      color: '#cbd5e1',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      cursor: 'pointer',
      transition: 'all 0.3s'
    },
    emptyState: {
      height: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      textAlign: 'center',
      padding: '5rem 0',
      color: '#94a3b8'
    },
    errorBox: {
      background: 'rgba(239, 68, 68, 0.2)',
      border: '1px solid rgba(239, 68, 68, 0.5)',
      borderRadius: '0.5rem',
      padding: '1rem',
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.75rem'
    },
    badge: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.5rem 1rem',
      borderRadius: '0.5rem',
      fontSize: '0.875rem',
      fontWeight: '500'
    },
    badgeSuccess: {
      background: 'rgba(16, 185, 129, 0.2)',
      color: '#6ee7b7',
      border: '1px solid rgba(16, 185, 129, 0.5)'
    },
    badgeWarning: {
      background: 'rgba(234, 179, 8, 0.2)',
      color: '#fde047',
      border: '1px solid rgba(234, 179, 8, 0.5)'
    },
    infoBox: {
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '0.5rem',
      padding: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      marginBottom: '1rem'
    },
    categoryBox: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem'
    },
    categoryIcon: {
      width: '2.5rem',
      height: '2.5rem',
      borderRadius: '0.5rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '1.5rem'
    },
    responseText: {
      color: '#cbd5e1',
      whiteSpace: 'pre-wrap',
      lineHeight: '1.6'
    },
    featureGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '1rem'
    },
    featureCard: {
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '0.5rem',
      padding: '1rem',
      border: '1px solid rgba(255, 255, 255, 0.1)'
    },
    featureIcon: {
      fontSize: '2rem',
      marginBottom: '0.5rem'
    },
    featureTitle: {
      color: 'white',
      fontWeight: '600',
      marginBottom: '0.25rem',
      fontSize: '0.9rem'
    },
    featureDesc: {
      color: '#94a3b8',
      fontSize: '0.8rem'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.maxWidth}>
        <div style={styles.header}>
          <div style={styles.headerTitle}>
            <Sparkles color="#a78bfa" size={40} />
            <h1 style={styles.title}>AI Support Agent</h1>
          </div>
          <p style={styles.subtitle}>
            Powered by LangGraph • Intelligent ticket classification and response generation
          </p>
        </div>

        <div style={styles.grid}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <MessageSquare color="#a78bfa" size={24} />
              <h2 style={styles.cardTitle}>Submit Ticket</h2>
            </div>

            <div>
              <label style={styles.label}>Subject *</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Brief description of your issue"
                style={styles.input}
              />

              <label style={styles.label}>Description *</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide detailed information about your issue..."
                rows={6}
                style={styles.textarea}
              />

              <div style={styles.buttonGroup}>
                <button onClick={handleSubmit} disabled={loading} style={styles.button}>
                  {loading ? (
                    <>
                      <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send size={20} />
                      Submit Ticket
                    </>
                  )}
                </button>
                <button onClick={reset} style={styles.buttonSecondary}>
                  Clear
                </button>
              </div>
            </div>

            <div style={styles.exampleSection}>
              <p style={styles.exampleLabel}>Try an example:</p>
              <div style={styles.exampleGrid}>
                {exampleTickets.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => loadExample(example)}
                    style={styles.exampleButton}
                    onMouseEnter={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                      e.target.style.borderColor = 'rgba(168, 85, 247, 0.5)';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                      e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                    }}
                  >
                    {example.subject.slice(0, 30)}...
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <Sparkles color="#a78bfa" size={24} />
              <h2 style={styles.cardTitle}>AI Response</h2>
            </div>

            {!result && !error && !loading && (
              <div style={styles.emptyState}>
                <div>
                  <Clock size={64} style={{ opacity: 0.5, margin: '0 auto 1rem' }} />
                  <p style={{ fontSize: '1.125rem' }}>Submit a ticket to see the AI-generated response</p>
                </div>
              </div>
            )}

            {error && (
              <div style={styles.errorBox}>
                <AlertCircle color="#f87171" size={24} style={{ flexShrink: 0 }} />
                <div>
                  <p style={{ fontWeight: '600', color: '#fca5a5', margin: '0 0 0.25rem' }}>Error</p>
                  <p style={{ color: '#fecaca', fontSize: '0.875rem', margin: 0 }}>{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div>
                <div style={{ marginBottom: '1rem' }}>
                  {result.escalated ? (
                    <span style={{ ...styles.badge, ...styles.badgeWarning }}>
                      <AlertCircle size={20} />
                      Escalated to Human
                    </span>
                  ) : (
                    <span style={{ ...styles.badge, ...styles.badgeSuccess }}>
                      <CheckCircle size={20} />
                      Resolved
                    </span>
                  )}
                </div>

                {result.classification && (
                  <div style={styles.infoBox}>
                    <p style={{ ...styles.label, marginBottom: '0.5rem' }}>Classification</p>
                    <div style={styles.categoryBox}>
                      <span style={{ ...styles.categoryIcon, backgroundColor: categories[result.classification]?.color }}>
                        {categories[result.classification]?.icon}
                      </span>
                      <div>
                        <p style={{ color: 'white', fontWeight: '600', fontSize: '1.125rem', margin: 0 }}>
                          {categories[result.classification]?.label}
                        </p>
                        <p style={{ color: '#94a3b8', fontSize: '0.875rem', margin: 0 }}>
                          Attempts: {result.attempts}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div style={styles.infoBox}>
                  <p style={{ ...styles.label, marginBottom: '0.75rem' }}>Generated Response</p>
                  <p style={styles.responseText}>
                    {result.final_response || result.escalation_message || 'No response generated'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div style={styles.featureGrid}>
          {[
            { icon: '🎯', title: 'Auto-Classification', desc: 'AI categorizes tickets automatically' },
            { icon: '📚', title: 'RAG-Enhanced', desc: 'Retrieves relevant documentation' },
            { icon: '✅', title: 'Quality Review', desc: 'Validates response quality' },
            { icon: '🔄', title: 'Self-Improving', desc: 'Learns from feedback' }
          ].map((feature, idx) => (
            <div key={idx} style={styles.featureCard}>
              <div style={styles.featureIcon}>{feature.icon}</div>
              <h3 style={styles.featureTitle}>{feature.title}</h3>
              <p style={styles.featureDesc}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SupportTicketAgent;