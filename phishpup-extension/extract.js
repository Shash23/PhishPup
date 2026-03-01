function findEditor() {
  const selectors = [
    'div[aria-label="Message Body"][contenteditable="true"]',
    'div[aria-label^="Reply"][contenteditable="true"]',
    'div[role="textbox"][contenteditable="true"][g_editable="true"]',
  ];

  for (const s of selectors) {
    const el = document.querySelector(s);
    if (el && el.offsetParent !== null) return el;
  }
  return null;
}

function waitForCompose(timeout = 5000) {
  return new Promise((resolve) => {
    const start = Date.now();

    function tryFind() {
      const el = findEditor();
      if (el) return resolve(el);

      if (Date.now() - start > timeout) return resolve(null);
    }

    const observer = new MutationObserver(() => {
      const el = findEditor();
      if (el) {
        observer.disconnect();
        resolve(el);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    tryFind();
    setTimeout(() => {
      observer.disconnect();
      resolve(null);
    }, timeout);
  });
}

(async () => {
  const compose = await waitForCompose();

  if (!compose) return null;

  // Draft
  const draft = compose.innerText.trim();

  // Conversation
  const messageNodes = document.querySelectorAll("div.a3s.aiL");
  let conversation = "";
  messageNodes.forEach((node) => {
    const text = node.innerText.trim();
    if (text && text !== draft) {
      conversation += text + "\n\n---\n\n";
    }
  });
  conversation = conversation.slice(-6000);

  // Recipients
  const recipients = [];
  document.querySelectorAll('span[email], span[data-hovercard-id]').forEach((el) => {
    const email =
      el.getAttribute("email") ||
      el.getAttribute("data-hovercard-id");

    if (email && !recipients.includes(email)) recipients.push(email);
  });

  return {
    draft,
    conversation,
    recipients,
  };
})();
