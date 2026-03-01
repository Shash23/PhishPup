function MessageInput({ value, onChange, placeholder = 'Paste a message to analyze...' }) {
  return (
    <textarea
      className="message-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={6}
      aria-label="Message to analyze"
    />
  );
}

export default MessageInput;
