function AnalyzeButton({ label = 'Check Email', onClick, disabled = false }) {
  return (
    <button
      type="button"
      className="analyze-btn"
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
    >
      {label}
    </button>
  );
}

export default AnalyzeButton;
