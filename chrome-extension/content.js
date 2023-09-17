async function main() {
  const url = window.location.href;
  const encodedUrl = encodeURIComponent(url);
  const api = `https://mau-md--embeddings-app.modal.run/get-lecture-id/${encodedUrl}`;

  console.log(url);

  const res = await fetch(api);
  const { id } = await res.json();

  console.log(id == -1);
  if (id == -1) return;

  window.watsonAssistantChatOptions = {
    integrationID: "b1edb76c-b5b7-48f1-81bc-1d4b6beffd68", // The ID of this integration.
    region: "us-east", // The region your integration is hosted in.
    serviceInstanceID: "e5fa945d-0470-491c-a731-719f63cd76ff", // The ID of your service instance.
    onLoad: function (instance) {
      instance.render();
    },
  };
  setTimeout(function () {
    const t = document.createElement("script");
    t.src =
      "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" +
      (window.watsonAssistantChatOptions.clientVersion || "latest") +
      "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
  });
}

main();

function injectScript(scriptContent) {
  const script = document.createElement("script");
  script.textContent = scriptContent;
  (document.head || document.documentElement).appendChild(script);
}
