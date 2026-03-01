function ResultCard({ risk_level, action, explanation, pressure_signals, interpreted_context }) {
  if (!risk_level && !action) return null;

  const borderClass =
    risk_level === 'HIGH'
      ? 'result-card high'
      : risk_level === 'MEDIUM'
        ? 'result-card medium'
        : 'result-card low';

  const hasContext = interpreted_context && typeof interpreted_context === 'object' && Object.keys(interpreted_context).length > 0;

  return (
    <section className={borderClass} aria-labelledby="result-heading">
      <h2 id="result-heading" className="result-heading">
        Analysis result
      </h2>
      <dl className="result-dl">
        <dt>Detected action</dt>
        <dd>{action || '—'}</dd>
        <dt>Risk level</dt>
        <dd>{risk_level || '—'}</dd>
        {pressure_signals && pressure_signals.length > 0 && (
          <>
            <dt>Why this is risky</dt>
            <dd>{pressure_signals.join(', ')}</dd>
          </>
        )}
      </dl>
      <div className="result-explanation">
        <h3>Explanation</h3>
        <p className="explanation-text">{explanation || '—'}</p>
      </div>
      {hasContext && (
        <div className="understood-context">
          <p className="context-tailor-msg">
            {interpreted_context.sensitivity === 'high'
              ? 'PhishPup is tailoring checks for a high-risk situation'
              : interpreted_context.sensitivity === 'medium'
                ? 'PhishPup is tailoring checks for an important communication'
                : 'PhishPup is tailoring checks for a general conversation'}
          </p>
          <h3>Understood Context</h3>
          <dl className="result-dl">
            <dt>Category</dt>
            <dd>{interpreted_context.category ?? '—'}</dd>
            <dt>Sensitivity</dt>
            <dd>{interpreted_context.sensitivity ?? '—'}</dd>
            <dt>Focus</dt>
            <dd>
              {Array.isArray(interpreted_context.focus_checks) && interpreted_context.focus_checks.length > 0
                ? interpreted_context.focus_checks.join(', ')
                : '—'}
            </dd>
          </dl>
        </div>
      )}
    </section>
  );
}

export default ResultCard;
