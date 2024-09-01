window.onload = function () {
  chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
    const hostname = new URL(tabs[0].url).hostname;
    document.querySelector(".heading").innerHTML =
      document.querySelector(".heading").innerHTML + hostname;
    fetch("http:/127.0.0.1:5000/privacy?url=" + hostname)
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data) {
          document.querySelector(".privacy-content").innerHTML = data.policy;
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });

    chrome.tabs.sendMessage(tabs[0].id, { message: "popup_open" });
  });

  chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
    chrome.tabs.sendMessage(tabs[0].id, { message: "popup_open" });
  });

  if (document.getElementsByClassName("analyze-button")) {
    document.getElementsByClassName("analyze-button")[0].onclick = function () {
      chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
        console.log("i work");
        chrome.tabs.sendMessage(tabs[0].id, { message: "analyze_site" });
      });
    };
  }

  document.getElementsByClassName("proxy-button")[0].onclick = function () {
    chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
      const url = new URL(tabs[0].url);

      chrome.tabs.update(tabs[0].id, { url: "https://12ft.io/" + url });
    });
  };

  document.getElementsByClassName("link")[0].onclick = function () {
    chrome.tabs.create({
      url: document.getElementsByClassName("link")[0].getAttribute("href"),
    });
  };

  document.getElementsByClassName("reviews-button")[0].onclick = function () {
    chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
      const hostname = new URL(tabs[0].url).hostname;
      fetch("http:/127.0.0.1:5000/reviews?url=" + hostname)
        .then((response) => {
          return response.text();
        })
        .then((html) => {
       
          console.log(html);
        });
      console.log(hostname)
      window.location.replace("http:/127.0.0.1:5000/reviews?url=https://" + hostname)
    });
  };

};

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.message === "update_current_count") {
    document.getElementsByClassName("number")[0].textContent = request.count;
  }
});



