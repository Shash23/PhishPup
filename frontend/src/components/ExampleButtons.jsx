const EXAMPLES = [
  {
    label: 'OTP scam',
    text: 'send me the verification code',
    conversation: '',
    situationDescription: 'Someone asking for a one-time code or verification',
  },
  {
    label: 'Schedule commitment',
    text: 'Yes, 2pm Tuesday works. See you then.',
    conversation: 'Can we meet next week? I need 30 min.',
    situationDescription: 'Scheduling a meeting or commitment',
  },
  {
    label: 'External sharing',
    text: 'Here is the link to the document: https://example.com/doc',
    conversation: '',
    situationDescription: 'Sharing a file or link with someone outside the team',
  },
];

function ExampleButtons({ onSelect }) {
  return (
    <div className="example-buttons">
      {EXAMPLES.map((ex) => (
        <button
          key={ex.label}
          type="button"
          className="example-btn"
          onClick={() => onSelect(ex)}
        >
          {ex.label}
        </button>
      ))}
    </div>
  );
}

export default ExampleButtons;
