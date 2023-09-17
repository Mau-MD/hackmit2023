async function main() {
  const url = window.location.href;
  const encodedUrl = encodeURIComponent(url);
  const api = `https://mau-md--embeddings-app.modal.run/get-lecture-id/${encodedUrl}`;

  console.log(url);

  const res = await fetch(api);
  const { id } = await res.json();

  console.log(id);
  if (id === -1) return;

  // Set Watson Assistant Chat Options
  window.watsonAssistantChatOptions = {
    integrationID: "aec400f8-ffeb-4672-a3b0-5c0ec7582f75",
    region: "us-east",
    serviceInstanceID: "e5fa945d-0470-491c-a731-719f63cd76ff",
    onLoad: function (instance) {
      instance.render();
    },
  };

  // Set Watson Assistant Chat Options
  window.watsonAssistantChatOptions = {
    integrationID: "aec400f8-ffeb-4672-a3b0-5c0ec7582f75",
    region: "us-east",
    serviceInstanceID: "e5fa945d-0470-491c-a731-719f63cd76ff",
    onLoad: function (instance) {
      instance.render();
    },
  };

  // Fetch and execute the Watson Assistant script
  fetch(
    "https://web-chat.global.assistant.watson.appdomain.cloud/versions/latest/WatsonAssistantChatEntry.js"
  )
    .then((response) => response.text())
    .then((scriptContent) => {
      const script = document.createElement("script");
      script.textContent = scriptContent;
      (document.head || document.documentElement).appendChild(script);
      script.remove();
    })
    .catch((error) => {
      console.error("Error executing the fetched script:", error);
    });
}

main();
